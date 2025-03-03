from django.db import models
from django.urls import reverse

class ResourceCategory(models.Model):
    CATEGORY_TYPES = (
        ('technical', 'Technical'),
        ('career', 'Career'),
        ('research', 'Research'),
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    category_type = models.CharField(max_length=20, choices=CATEGORY_TYPES)
    description = models.TextField()
    image = models.ImageField(upload_to='resources/categories/')

    class Meta:
        verbose_name_plural = "Resource Categories"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('resources:category_detail', kwargs={'slug': self.slug})

class Resource(models.Model):
    FILE_TYPES = (
        ('pdf', 'PDF'),
        ('doc', 'Document'),
        ('code', 'Code'),
        ('other', 'Other'),
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    file = models.FileField(upload_to='resources/files/')
    file_type = models.CharField(max_length=10, choices=FILE_TYPES)
    file_size = models.CharField(max_length=20)  # e.g. "1.2 MB"
    category = models.ForeignKey(ResourceCategory, on_delete=models.CASCADE)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title