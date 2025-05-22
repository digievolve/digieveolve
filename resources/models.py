from django.db import models
from django.urls import reverse
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill
# resources/models.py
from django.contrib.postgres.search import SearchVectorField  # Add this import

class ResourceCategory(models.Model):
    CATEGORY_TYPES = (
        ('technical', 'Technical'),
        ('career', 'Career'),
        ('research', 'Research'),
    )
    title = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(unique=True)
    category_type = models.CharField(max_length=20, choices=CATEGORY_TYPES)
    description = models.TextField()
    image = ProcessedImageField(
        upload_to='resources/categories/',
        processors=[ResizeToFill(800, 600)],
        format='WEBP',
        options={'quality': 80}
    )

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
    category = models.ForeignKey('ResourceCategory', on_delete=models.CASCADE, db_index=True)  # Add db_index
    updated_date = models.DateTimeField(auto_now=True)
    search_vector = SearchVectorField(null=True)  # For PostgreSQL full-text search


    def __str__(self):
        return self.title