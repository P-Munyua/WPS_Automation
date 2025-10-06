# documents/models.py
from django.db import models
from django.conf import settings

class DocumentTemplate(models.Model):
    ACADEMIC_PAPER = 'academic'
    BUSINESS_REPORT = 'business'
    TEMPLATE_TYPES = [
        (ACADEMIC_PAPER, 'Academic Paper'),
        (BUSINESS_REPORT, 'Business Report'),
    ]
    
    name = models.CharField(max_length=100)
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPES)
    description = models.TextField(blank=True)
    file_path = models.FileField(upload_to='templates/')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class DocumentGenerationTask(models.Model):
    PENDING = 'pending'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    FAILED = 'failed'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (PROCESSING, 'Processing'),
        (COMPLETED, 'Completed'),
        (FAILED, 'Failed'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    topic = models.TextField()
    requirements = models.JSONField(default=dict)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    generated_file = models.FileField(upload_to='documents/', null=True, blank=True)
    word_count = models.IntegerField(default=0)
    charts_count = models.IntegerField(default=0)
    formulas_count = models.IntegerField(default=0)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Task {self.id} - {self.topic[:50]}"