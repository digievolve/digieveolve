from django.contrib import admin
from .models import Course, Enrollment, Certificate
from .quiz_models import Module, Quiz, Question, Answer, QuizAttempt, QuestionResponse

# Register your models here.
admin.site.register(Course)
admin.site.register(Enrollment)
admin.site.register(Certificate)
admin.site.register(Module)
admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(QuizAttempt)
admin.site.register(QuestionResponse)