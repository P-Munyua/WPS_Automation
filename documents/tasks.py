# documents/tasks.py
import os
from celery import shared_task
from django.utils import timezone
from django.conf import settings
from .models import DocumentGenerationTask
from .services.content_generator import ContentGenerator

@shared_task(bind=True)
def generate_document_task(self, task_id):
    """Async task for document generation"""
    try:
        # Get the task
        task = DocumentGenerationTask.objects.get(id=task_id)
        task.status = DocumentGenerationTask.PROCESSING
        task.save()
        
        # Initialize content generator
        generator = ContentGenerator()
        
        # Determine document type and generate
        requirements = task.requirements
        template_type = requirements.get('template_type', 'academic')
        
        if template_type == 'business':
            file_path, content = generator.generate_business_report(
                task.topic, requirements, task.user
            )
        else:
            file_path, content = generator.generate_academic_paper(
                task.topic, requirements, task.user
            )
        
        # Update task with results
        task.generated_file.name = os.path.relpath(file_path, settings.MEDIA_ROOT)
        task.status = DocumentGenerationTask.COMPLETED
        task.completed_at = timezone.now()
        
        # Calculate statistics
        task.word_count = len(content.split())
        task.charts_count = content.count('[图表位置]') + content.count('[CHART LOCATION]')
        task.formulas_count = content.count('[公式位置]') + content.count('[FORMULA LOCATION]')
        
        task.save()
        
        return {
            'status': 'success',
            'task_id': task_id,
            'file_path': task.generated_file.url if task.generated_file else None
        }
        
    except Exception as e:
        # Update task with error
        try:
            task = DocumentGenerationTask.objects.get(id=task_id)
            task.status = DocumentGenerationTask.FAILED
            task.error_message = str(e)
            task.save()
        except:
            pass
        
        return {
            'status': 'error',
            'task_id': task_id,
            'error': str(e)
        }