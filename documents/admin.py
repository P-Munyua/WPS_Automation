# documents/admin.py
from django.contrib import admin
from .models import DocumentTemplate, DocumentGenerationTask

@admin.register(DocumentTemplate)
class DocumentTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'template_type', 'is_active', 'created_at']
    list_filter = ['template_type', 'is_active']
    search_fields = ['name', 'description']

@admin.register(DocumentGenerationTask)
class DocumentGenerationTaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'topic', 'status', 'word_count', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['topic', 'user__email']
    readonly_fields = ['created_at', 'completed_at']