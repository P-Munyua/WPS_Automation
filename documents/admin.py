# documents/admin.py
from django.contrib import admin
from .models import DocumentTemplate, DocumentGenerationTask

@admin.register(DocumentTemplate)
class DocumentTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'template_type', 'is_active', 'created_at']
    list_filter = ['template_type', 'is_active']
    search_fields = ['name', 'description']


# documents/admin.py - Enhanced with more features
from django.utils.html import format_html
from django.urls import reverse

@admin.register(DocumentGenerationTask)
class DocumentGenerationTaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_link', 'topic_preview', 'status_badge', 
                   'word_count', 'charts_count', 'formulas_count', 
                   'created_at', 'completed_at', 'download_link']
    list_filter = ['status', 'created_at', 'user__subscription__plan']
    search_fields = ['topic', 'user__email', 'user__phone_number']
    readonly_fields = ['created_at', 'completed_at', 'task_duration']
    list_per_page = 20
    
    def user_link(self, obj):
        url = reverse('admin:users_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.email or obj.user.phone_number)
    user_link.short_description = '用户'
    
    def topic_preview(self, obj):
        return obj.topic[:50] + '...' if len(obj.topic) > 50 else obj.topic
    topic_preview.short_description = '主题'
    
    def status_badge(self, obj):
        colors = {
            'pending': 'gray',
            'processing': 'blue', 
            'completed': 'green',
            'failed': 'red'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 10px;">{}</span>',
            colors.get(obj.status, 'gray'),
            obj.get_status_display()
        )
    status_badge.short_description = '状态'
    
    def download_link(self, obj):
        if obj.generated_file:
            return format_html(
                '<a href="{}" download>下载</a>',
                obj.generated_file.url
            )
        return '-'
    download_link.short_description = '文件'
    
    def task_duration(self, obj):
        if obj.completed_at and obj.created_at:
            duration = obj.completed_at - obj.created_at
            return f"{duration.total_seconds():.1f}秒"
        return '-'
    task_duration.short_description = '处理时长'