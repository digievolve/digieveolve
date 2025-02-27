# courses/models.py
from django.db import models
from accounts.models import StudentProfile

class Course(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    short_description = models.TextField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='courses/', null=True, blank=True)
    duration = models.IntegerField(help_text="Duration in hours")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Enrollment(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrollment_date = models.DateTimeField(auto_now_add=True)
    completed_modules = models.PositiveIntegerField(default=0)
    is_completed = models.BooleanField(default=False)  # Ensure this field exists
    completion_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.full_name} - {self.course.title}"

class Certificate(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    issued_date = models.DateTimeField(auto_now_add=True)
    certificate_number = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f"{self.student.full_name} - {self.course.title}"