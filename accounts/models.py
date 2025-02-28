# accounts/models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15, blank=True)
    bio = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}'s profile"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        db_table = 'accounts_studentprofile'

# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         StudentProfile.objects.create(user=instance)

# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     instance.studentprofile.save()


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
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Activities'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.student.user.username} - {self.activity_type} - {self.timestamp.strftime('%Y-%m-%d')}"