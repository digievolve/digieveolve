from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s profile"
    
    class Meta:
        db_table = 'accounts_studentprofile'


        
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