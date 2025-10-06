# documents/models.py
from django.db import models
from django.conf import settings

import os
import uuid
from django.db import models

def document_upload_path(instance, filename):
    """Generate upload path for documents"""
    # Generate unique filename
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('documents', filename)

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

    generated_file = models.FileField(
        upload_to=document_upload_path, 
        null=True, 
        blank=True,
        verbose_name="生成的文件"
    )
    
    # Add file-related fields
    file_size = models.BigIntegerField(default=0, verbose_name="文件大小")
    file_format = models.CharField(max_length=10, default='docx', verbose_name="文件格式")
    
    class Meta:
        verbose_name = "文档生成任务"
        verbose_name_plural = "文档生成任务"
        ordering = ['-created_at']