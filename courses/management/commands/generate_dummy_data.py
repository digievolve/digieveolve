from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from accounts.models import StudentProfile, Activity
from courses.models import Course, Enrollment, Certificate
from courses.quiz_models import Module, Quiz, Question, Answer, QuizAttempt, QuestionResponse
import random
from datetime import timedelta

class Command(BaseCommand):
    help = 'Generate dummy data for testing'

    def handle(self, *args, **kwargs):
        self.stdout.write('Generating dummy data...')

        # Create test user if it doesn't exist
        if not User.objects.filter(username='testuser').exists():
            user = User.objects.create_user(
                username='testuser',
                email='test@example.com',
                password='testpassword',
                first_name='Test',
                last_name='User'
            )

            # Create student profile
            student = StudentProfile.objects.create(
                user=user,
                phone='1234567890',
                bio='This is a test user for demonstration purposes.'
            )

            self.stdout.write(self.style.SUCCESS('Created test user and profile'))
        else:
            user = User.objects.get(username='testuser')
            student = StudentProfile.objects.get(user=user)
            self.stdout.write('Test user already exists')

        # Create courses
        courses_data = [
            {
                'title': 'Data Analytics Fundamentals',
                'slug': 'data-analytics-fundamentals',
                'short_description': 'Learn the basics of data analytics',
                'description': 'This course covers the fundamentals of data analytics, including data collection, cleaning, analysis, and visualization.',
                'duration': 20,
            },
            {
                'title': 'Python for Data Science',
                'slug': 'python-for-data-science',
                'short_description': 'Master Python for data science applications',
                'description': 'Learn how to use Python for data science, including pandas, NumPy, and matplotlib.',
                'duration': 30,
            },
            {
                'title': 'Machine Learning Essentials',
                'slug': 'machine-learning-essentials',
                'short_description': 'Introduction to machine learning concepts',
                'description': 'This course introduces the fundamental concepts of machine learning, including supervised and unsupervised learning.',
                'duration': 40,
            },
            {
                'title': 'Business Intelligence with Power BI',
                'slug': 'business-intelligence-power-bi',
                'short_description': 'Create powerful BI dashboards',
                'description': 'Learn how to create interactive dashboards and reports using Microsoft Power BI.',
                'duration': 25,
            },
        ]

        created_courses = []
        for course_data in courses_data:
            course, created = Course.objects.get_or_create(
                slug=course_data['slug'],
                defaults=course_data
            )
            created_courses.append(course)
            if created:
                self.stdout.write(f'Created course: {course.title}')
            else:
                self.stdout.write(f'Course already exists: {course.title}')

        # Create modules for each course
        for course in created_courses:
            # Clear existing modules
            Module.objects.filter(course=course).delete()

            # Create new modules
            for i in range(1, 6):  # 5 modules per course
                module = Module.objects.create(
                    course=course,
                    title=f'Module {i}: {course.title} - Part {i}',
                    description=f'This is module {i} of the {course.title} course.',
                    content=f'<p>Detailed content for module {i} of {course.title}.</p>',
                    order=i,
                    video_url='https://www.youtube.com/embed/dQw4w9WgXcQ',  # Placeholder video
                    video_duration=random.randint(15, 45),
                    has_quiz=(i % 2 == 0)  # Every other module has a quiz
                )

                self.stdout.write(f'Created module: {module.title}')

                # Create quiz for modules that have quizzes
                if module.has_quiz:
                    quiz = Quiz.objects.create(
                        title=f'Quiz for {module.title}',
                        description=f'Test your knowledge of {module.title}',
                        module=module,
                        time_limit=random.randint(10, 30),
                        passing_score=70
                    )

                    self.stdout.write(f'Created quiz: {quiz.title}')

                    # Create questions for the quiz
                    for j in range(1, 6):  # 5 questions per quiz
                        question_type = random.choice(['multiple_choice', 'true_false', 'short_answer'])

                        question = Question.objects.create(
                            quiz=quiz,
                            text=f'Question {j} for {module.title}?',
                            question_type=question_type,
                            points=random.choice([1, 2, 3]),
                            order=j
                        )

                        self.stdout.write(f'Created question: {question.text}')

                        # Create answers for multiple choice and true/false questions
                        if question_type in ['multiple_choice', 'true_false']:
                            num_answers = 4 if question_type == 'multiple_choice' else 2
                            correct_answer = random.randint(0, num_answers - 1)

                            for k in range(num_answers):
                                is_correct = (k == correct_answer)

                                if question_type == 'true_false':
                                    answer_text = 'True' if k == 0 else 'False'
                                else:
                                    answer_text = f'Answer {k+1} for Question {j}'

                                Answer.objects.create(
                                    question=question,
                                    text=answer_text,
                                    is_correct=is_correct
                                )

                                if is_correct:
                                    self.stdout.write(f'Created correct answer: {answer_text}')
                                else:
                                    self.stdout.write(f'Created incorrect answer: {answer_text}')

        # Enroll student in courses
        for course in created_courses:
            enrollment, created = Enrollment.objects.get_or_create(
                student=student,
                course=course,
                defaults={
                    'enrollment_date': timezone.now() - timedelta(days=random.randint(1, 30)),
                    'completed_modules': '',
                    'is_completed': False
                }
            )

            if created:
                self.stdout.write(f'Enrolled student in course: {course.title}')

                # Create enrollment activity
                Activity.objects.create(
                    student=student,
                    activity_type='enrollment',
                    description=f'Enrolled in course: {course.title}',
                    course=course,
                    timestamp=enrollment.enrollment_date
                )
            else:
                self.stdout.write(f'Student already enrolled in course: {course.title}')

            # Mark some modules as completed
            modules = Module.objects.filter(course=course).order_by('order')
            completed_count = random.randint(0, len(modules))

            completed_modules = []
            for i in range(completed_count):
                completed_modules.append(str(modules[i].id))

                # Create module completion activity
                Activity.objects.create(
                    student=student,
                    activity_type='completion',
                    description=f'Completed module: {modules[i].title}',
                    course=course,
                    timestamp=timezone.now() - timedelta(days=random.randint(0, 20))
                )

            enrollment.completed_modules = ','.join(completed_modules)

            # If all modules are completed, mark the course as completed
            if completed_count == len(modules):
                enrollment.is_completed = True
                enrollment.completion_date = timezone.now() - timedelta(days=random.randint(0, 10))

                # Create certificate
                certificate, cert_created = Certificate.objects.get_or_create(
                    student=student,
                    course=course,
                    defaults={
                        'issued_date': enrollment.completion_date
                    }
                )

                if cert_created:
                    self.stdout.write(f'Created certificate for course: {course.title}')

                    # Create certificate activity
                    Activity.objects.create(
                        student=student,
                        activity_type='certificate',
                        description=f'Earned certificate for: {course.title}',
                        course=course,
                        timestamp=certificate.issued_date
                    )

            enrollment.save()

            # Create quiz attempts for some quizzes
            for module in modules:
                if module.has_quiz:
                    quiz = Quiz.objects.get(module=module)

                    # 50% chance of having attempted the quiz
                    if random.random() > 0.5:
                        # Create quiz attempt
                        attempt = QuizAttempt.objects.create(
                            student=student,
                            quiz=quiz,
                            started_at=timezone.now() - timedelta(days=random.randint(0, 15))
                        )

                        # 70% chance of having completed the quiz
                        if random.random() > 0.3:
                            # Calculate random score
                            score = random.uniform(50, 100)
                            is_passed = score >= quiz.passing_score

                            attempt.score = score
                            attempt.is_passed = is_passed
                            attempt.completed_at = attempt.started_at + timedelta(minutes=random.randint(5, quiz.time_limit))
                            attempt.save()

                            self.stdout.write(f'Created completed quiz attempt for {quiz.title} with score {score:.1f}%')

                            # Create responses for each question
                            questions = Question.objects.filter(quiz=quiz)
                            for question in questions:
                                if question.question_type in ['multiple_choice', 'true_false']:
                                    # Select a random answer
                                    answers = Answer.objects.filter(question=question)
                                    selected_answer = random.choice(answers)

                                    QuestionResponse.objects.create(
                                        attempt=attempt,
                                        question=question,
                                        selected_answer=selected_answer,
                                        is_correct=selected_answer.is_correct
                                    )
                                elif question.question_type == 'short_answer':
                                    QuestionResponse.objects.create(
                                        attempt=attempt,
                                        question=question,
                                        text_response=f'Sample answer for {question.text}',
                                        is_correct=random.choice([True, False])
                                    )
                        else:
                            self.stdout.write(f'Created incomplete quiz attempt for {quiz.title}')

        self.stdout.write(self.style.SUCCESS('Successfully generated dummy data'))