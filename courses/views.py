from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages  # Add this import
from django.utils import timezone
from django.urls import reverse
from django.http import JsonResponse
from .models import Course, Certificate, Enrollment, Payment
from .quiz_models import Module, Quiz, Question, Answer, QuizAttempt, QuestionResponse
from accounts.models import StudentProfile, Activity
import uuid
import json
import requests
from django.conf import settings



@login_required(login_url='accounts:login')
def enrolled_courses(request):
    enrollments = Enrollment.objects.filter(
        student__user=request.user
    ).select_related('course')
    return render(request, 'courses/enrolled_courses.html', {'enrollments': enrollments})

@login_required(login_url='accounts:login')
def certificate_list(request):
    # Assuming you have a way to get the user's certificates
    certificates = Certificate.objects.filter(student__user=request.user)
    return render(request, 'courses/certificate_list.html', {'certificates': certificates})

@login_required(login_url='accounts:login')
def certificate_detail(request, certificate_id):
    certificate = get_object_or_404(
        Certificate,
        id=certificate_id,
        student__user=request.user
    )
    return render(request, 'courses/certificate_detail.html', {'certificate': certificate})



@login_required(login_url='accounts:login')
def course_list(request):
    courses = Course.objects.all()
    return render(request, 'courses/list.html', {'courses': courses})

@login_required(login_url='accounts:login')
def course_detail(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    modules = Module.objects.filter(course=course).order_by('order')

    student_profile = StudentProfile.objects.get(user=request.user)

    # Check if user is enrolled
    try:
        enrollment = Enrollment.objects.get(student=student_profile, course=course)
        is_enrolled = True
        completed_modules = enrollment.completed_modules.split(',') if enrollment.completed_modules else []
        progress = enrollment.progress
    except Enrollment.DoesNotExist:
        enrollment = None
        is_enrolled = False
        completed_modules = []
        progress = 0

    context = {
        'course': course,
        'modules': modules,
        'enrollment': enrollment,
        'is_enrolled': is_enrolled,
        'completed_modules': completed_modules,
        'progress': progress
    }

    return render(request, 'courses/detail.html', context)

@login_required(login_url='accounts:login')
def initiate_payment(request, course_slug):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)

    try:
        course = get_object_or_404(Course, slug=course_slug)
        student_profile = StudentProfile.objects.get(user=request.user)

        # Check if already enrolled
        if Enrollment.objects.filter(student=student_profile, course=course).exists():
            return JsonResponse({'error': 'Already enrolled in this course'}, status=400)

        # For free courses, enroll directly
        if course.is_free:
            enrollment = Enrollment.objects.create(
                student=student_profile,
                course=course
            )

            # Create activity record
            Activity.objects.create(
                student=student_profile,
                activity_type='enrollment',
                description=f"Enrolled in course: {course.title}",
                course=course
            )

            return JsonResponse({
                'success': True,
                'redirect_url': reverse('courses:detail', kwargs={'course_slug': course.slug})
            })

        # Generate unique reference
        reference = f"DIGI-{uuid.uuid4().hex[:8].upper()}"

        # Create pending payment record
        payment = Payment.objects.create(
            student=student_profile,
            course=course,
            amount=course.price,
            reference=reference,
            status='pending'
        )

        # Prepare Paystack API request
        url = "https://api.paystack.co/transaction/initialize"
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json"
        }

        callback_url = request.build_absolute_uri(
            reverse('courses:verify_payment', kwargs={'reference': reference})
        )

        data = {
            "email": request.user.email,
            "amount": int(course.price * 100),  # Paystack expects amount in kobo
            "currency": "NGN",
            "reference": reference,
            "callback_url": callback_url,
            "metadata": {
                "course_id": course.id,
                "course_title": course.title,
                "student_id": student_profile.id
            }
        }

        # Print debug information
        print(f"Paystack Request URL: {url}")
        print(f"Paystack Request Headers: {headers}")
        print(f"Paystack Request Data: {data}")

        response = requests.post(url, headers=headers, data=json.dumps(data))
        response_data = response.json()

        # Print response for debugging
        print(f"Paystack Response Status: {response.status_code}")
        print(f"Paystack Response Data: {response_data}")

        if response.status_code == 200 and response_data['status']:
            # Update payment with authorization URL
            payment.transaction_id = response_data['data']['reference']
            payment.save()

            return JsonResponse({
                'success': True,
                'authorization_url': response_data['data']['authorization_url']
            })
        else:
            payment.status = 'failed'
            payment.save()
            error_message = response_data.get('message', 'Payment initialization failed')
            print(f"Paystack Error: {error_message}")
            return JsonResponse({'error': error_message}, status=400)

    except Exception as e:
        print(f"Exception in initiate_payment: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@login_required(login_url='accounts:login')
def verify_payment(request, reference):
    try:
        # Get the payment
        payment = get_object_or_404(Payment, reference=reference)

        # If already processed, redirect to course
        if payment.status == 'completed':
            return redirect('courses:detail', course_slug=payment.course.slug)

        # Verify with Paystack
        url = f"https://api.paystack.co/transaction/verify/{reference}"
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"
        }

        # Print debug information
        print(f"Verify Payment URL: {url}")
        print(f"Verify Payment Headers: {headers}")

        response = requests.get(url, headers=headers)
        response_data = response.json()

        # Print response for debugging
        print(f"Verify Payment Response Status: {response.status_code}")
        print(f"Verify Payment Response Data: {response_data}")

        if response.status_code == 200 and response_data['status'] and response_data['data']['status'] == 'success':
            # Update payment status
            payment.status = 'completed'
            payment.payment_method = response_data['data'].get('channel', 'unknown')
            payment.save()

            # Create enrollment
            student_profile = payment.student
            course = payment.course

            enrollment, created = Enrollment.objects.get_or_create(
                student=student_profile,
                course=course,
                defaults={
                    'enrollment_date': timezone.now()
                }
            )

            if created:
                # Create activity record
                Activity.objects.create(
                    student=student_profile,
                    activity_type='enrollment',
                    description=f"Enrolled in course: {course.title}",
                    course=course
                )

            messages.success(request, f"Payment successful! You are now enrolled in {course.title}.")
            return redirect('courses:detail', course_slug=course.slug)
        else:
            payment.status = 'failed'
            payment.save()
            messages.error(request, "Payment verification failed. Please contact support.")
            return redirect('courses:detail', course_slug=payment.course.slug)

    except Exception as e:
        print(f"Exception in verify_payment: {str(e)}")
        if 'payment' in locals():
            payment.status = 'failed'
            payment.save()
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect('courses:detail', course_slug=payment.course.slug)
        else:
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect('courses:course_list')
    
    

@login_required(login_url='accounts:login')
def module_detail(request, course_slug, module_id):
    course = get_object_or_404(Course, slug=course_slug)
    module = get_object_or_404(Module, id=module_id, course=course)

    student_profile = StudentProfile.objects.get(user=request.user)
    enrollment = get_object_or_404(Enrollment, student=student_profile, course=course)

    # Check if this module has been completed
    completed_modules = enrollment.completed_modules.split(',') if enrollment.completed_modules else []
    is_completed = str(module.id) in completed_modules

    # Get quizzes for this module
    quizzes = Quiz.objects.filter(module=module)

    # Track video progress if needed
    if request.method == 'POST' and 'video_progress' in request.POST:
        progress = request.POST.get('video_progress')
        if progress == '100' and not is_completed and not module.has_quiz:
            # Mark module as completed if video is watched and no quiz is required
            if enrollment.completed_modules:
                enrollment.completed_modules += f",{module.id}"
            else:
                enrollment.completed_modules = str(module.id)

            enrollment.save()

            # Create activity record
            Activity.objects.create(
                student=student_profile,
                activity_type='completion',
                description=f"Completed module: {module.title}",
                course=course
            )

            is_completed = True

            # Check if all modules are completed
            all_modules = Module.objects.filter(course=course)
            all_completed = all(str(m.id) in enrollment.completed_modules.split(',') for m in all_modules)

            if all_completed and not enrollment.is_completed:
                enrollment.is_completed = True
                enrollment.completion_date = timezone.now()
                enrollment.save()

                # Generate certificate
                Certificate.objects.create(
                    student=student_profile,
                    course=course,
                    issued_date=timezone.now()
                )

                # Create activity record
                Activity.objects.create(
                    student=student_profile,
                    activity_type='certificate',
                    description=f"Earned certificate for: {course.title}",
                    course=course
                )

    context = {
        'course': course,
        'module': module,
        'is_completed': is_completed,
        'quizzes': quizzes,
    }

    return render(request, 'courses/module_detail.html', context)

@login_required(login_url='accounts:login')
def quiz_list(request, course_slug, module_id):
    course = get_object_or_404(Course, slug=course_slug)
    module = get_object_or_404(Module, id=module_id, course=course)
    quizzes = Quiz.objects.filter(module=module)

    student_profile = StudentProfile.objects.get(user=request.user)
    quiz_attempts = {
        quiz.id: QuizAttempt.objects.filter(
            student=student_profile,
            quiz=quiz
        ).order_by('-started_at').first()
        for quiz in quizzes
    }

    context = {
        'course': course,
        'module': module,
        'quizzes': quizzes,
        'quiz_attempts': quiz_attempts,
    }

    return render(request, 'courses/quiz_list.html', context)

@login_required(login_url='accounts:login')
def take_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    student_profile = StudentProfile.objects.get(user=request.user)

    # Check if there's an incomplete attempt
    attempt = QuizAttempt.objects.filter(
        student=student_profile,
        quiz=quiz,
        completed_at__isnull=True
    ).first()

    if not attempt:
        # Create a new attempt
        attempt = QuizAttempt.objects.create(
            student=student_profile,
            quiz=quiz
        )

    if request.method == 'POST':
        # Process quiz submission
        questions = Question.objects.filter(quiz=quiz)
        score = 0
        total_points = sum(q.points for q in questions)

        for question in questions:
            if question.question_type == 'multiple_choice':
                answer_id = request.POST.get(f'question_{question.id}')
                if answer_id:
                    selected_answer = Answer.objects.get(id=answer_id)
                    is_correct = selected_answer.is_correct

                    QuestionResponse.objects.create(
                        attempt=attempt,
                        question=question,
                        selected_answer=selected_answer,
                        is_correct=is_correct
                    )

                    if is_correct:
                        score += question.points

            elif question.question_type == 'true_false':
                answer_id = request.POST.get(f'question_{question.id}')
                if answer_id:
                    selected_answer = Answer.objects.get(id=answer_id)
                    is_correct = selected_answer.is_correct

                    QuestionResponse.objects.create(
                        attempt=attempt,
                        question=question,
                        selected_answer=selected_answer,
                        is_correct=is_correct
                    )

                    if is_correct:
                        score += question.points

            elif question.question_type == 'short_answer':
                text_response = request.POST.get(f'question_{question.id}')
                # For short answers, instructor will need to grade manually
                QuestionResponse.objects.create(
                    attempt=attempt,
                    question=question,
                    text_response=text_response
                )

        # Calculate percentage score
        percentage_score = (score / total_points) * 100 if total_points > 0 else 0

        # Update attempt
        attempt.score = percentage_score
        attempt.is_passed = percentage_score >= quiz.passing_score
        attempt.completed_at = timezone.now()
        attempt.save()

        # Update module completion if passed
        if attempt.is_passed:
            enrollment = Enrollment.objects.get(
                student=student_profile,
                course=quiz.module.course
            )

            # Add this module to completed modules if not already there
            if str(quiz.module.id) not in enrollment.completed_modules.split(',') if enrollment.completed_modules else []:
                if enrollment.completed_modules:
                    enrollment.completed_modules += f",{quiz.module.id}"
                else:
                    enrollment.completed_modules = str(quiz.module.id)

                enrollment.save()

                # Create activity record
                Activity.objects.create(
                    student=student_profile,
                    activity_type='completion',
                    description=f"Completed module: {quiz.module.title}",
                    course=quiz.module.course
                )

                # Check if all modules are completed
                all_modules = Module.objects.filter(course=quiz.module.course)
                completed_modules = enrollment.completed_modules.split(',') if enrollment.completed_modules else []
                all_completed = all(str(m.id) in completed_modules for m in all_modules)

                if all_completed and not enrollment.is_completed:
                    enrollment.is_completed = True
                    enrollment.completion_date = timezone.now()
                    enrollment.save()

                    # Generate certificate
                    Certificate.objects.create(
                        student=student_profile,
                        course=quiz.module.course,
                        issued_date=timezone.now()
                    )

                    # Create activity record
                    Activity.objects.create(
                        student=student_profile,
                        activity_type='certificate',
                        description=f"Earned certificate for: {quiz.module.course.title}",
                        course=quiz.module.course
                    )

        return redirect('courses:quiz_result', attempt_id=attempt.id)

    questions = Question.objects.filter(quiz=quiz).order_by('order')

    context = {
        'quiz': quiz,
        'questions': questions,
        'attempt': attempt,
    }

    return render(request, 'courses/take_quiz.html', context)

@login_required(login_url='accounts:login')
def quiz_result(request, attempt_id):
    attempt = get_object_or_404(QuizAttempt, id=attempt_id)

    # Ensure the user can only see their own results
    if attempt.student.user != request.user:
        return redirect('accounts:dashboard')

    responses = QuestionResponse.objects.filter(attempt=attempt)

    context = {
        'attempt': attempt,
        'responses': responses,
        'quiz': attempt.quiz,
        'module': attempt.quiz.module,
        'course': attempt.quiz.module.course,
    }

    return render(request, 'courses/quiz_result.html', context)


# courses/views.py
def public_certificate_view(request, uuid):
    """View for publicly shared certificates"""
    certificate = get_object_or_404(Certificate, uuid=uuid)
    return render(request, 'courses/public_certificate.html', {
        'certificate': certificate
    })