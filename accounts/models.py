from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.text import slugify

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15, blank=True)
    bio = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

    class Meta:
        db_table = 'accounts_studentprofile'

class Course(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=255)
    short_description = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='course_images/', blank=True, null=True)
    duration = models.PositiveIntegerField(help_text="Duration in hours")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total_modules = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Enrollment(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrollment_date = models.DateTimeField(auto_now_add=True)
    completed_modules = models.PositiveIntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    completion_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.full_name} - {self.course.title}"

class Certificate(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    issue_date = models.DateTimeField(auto_now_add=True)
    certificate_id = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f"{self.student.full_name} - {self.course.title} Certificate"

class Activity(models.Model):
    ACTIVITY_TYPES = (
        ('enrollment', 'Course Enrollment'),
        ('completion', 'Module Completion'),
        ('certificate', 'Certificate Earned'),
        ('other', 'Other Activity'),
    )

    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    description = models.CharField(max_length=255)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Activities'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.student.full_name} - {self.activity_type} - {self.timestamp.strftime('%Y-%m-%d')}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Get full name from first_name and last_name
        full_name = f"{instance.first_name} {instance.last_name}".strip()
        if not full_name:  # If both first_name and last_name are empty
            full_name = instance.username  # Use username as fallback

        StudentProfile.objects.get_or_create(
            user=instance,
            defaults={
                'full_name': full_name,
                'phone': ''
            }
        )

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.studentprofile.save()
    except StudentProfile.DoesNotExist:
        # Create profile if it doesn't exist
        full_name = f"{instance.first_name} {instance.last_name}".strip()
        if not full_name:
            full_name = instance.username
        StudentProfile.objects.create(
            user=instance,
            full_name=full_name,
            phone=''
        )