# documents/views.py
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import DocumentTemplate, DocumentGenerationTask
from .serializers import (
    DocumentTemplateSerializer, 
    DocumentGenerationTaskSerializer,
    DocumentGenerationRequestSerializer
)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_templates(request):
    """Get available document templates"""
    templates = DocumentTemplate.objects.filter(is_active=True)
    serializer = DocumentTemplateSerializer(templates, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_document(request):
    """Create a new document generation task"""
    serializer = DocumentGenerationRequestSerializer(data=request.data)
    
    if serializer.is_valid():
        # Create generation task
        task = DocumentGenerationTask.objects.create(
            user=request.user,
            topic=serializer.validated_data['topic'],
            requirements=serializer.validated_data
        )
        
        # In production, this would trigger a Celery task
        # For now, we'll just create the task
        task_serializer = DocumentGenerationTaskSerializer(task)
        
        return Response({
            'task': task_serializer.data,
            'message': 'Document generation task created successfully'
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_tasks(request):
    """Get user's document generation tasks"""
    tasks = DocumentGenerationTask.objects.filter(user=request.user).order_by('-created_at')
    serializer = DocumentGenerationTaskSerializer(tasks, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_task_detail(request, task_id):
    """Get details of a specific task"""
    try:
        task = DocumentGenerationTask.objects.get(id=task_id, user=request.user)
        serializer = DocumentGenerationTaskSerializer(task)
        return Response(serializer.data)
    except DocumentGenerationTask.DoesNotExist:
        return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)




# documents/views.py - Update generate_document view
from .tasks import generate_document_task

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_document(request):
    """Create a new document generation task"""
    serializer = DocumentGenerationRequestSerializer(data=request.data)
    
    if serializer.is_valid():
        # Create generation task
        task = DocumentGenerationTask.objects.create(
            user=request.user,
            topic=serializer.validated_data['topic'],
            requirements=serializer.validated_data
        )
        
        # Start async task
        generate_document_task.delay(task.id)
        
        task_serializer = DocumentGenerationTaskSerializer(task)
        
        return Response({
            'task': task_serializer.data,
            'message': 'Document generation started successfully'
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# documents/views.py - Add these imports
from django.http import HttpResponse
from utils.file_handlers import FileHandler
import os

# Add these new views

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_document(request, task_id):
    """Download generated document"""
    try:
        task = DocumentGenerationTask.objects.get(id=task_id, user=request.user)
        
        if not task.generated_file:
            return Response({"error": "Document not generated yet"}, 
                           status=status.HTTP_404_NOT_FOUND)
        
        if not FileHandler.file_exists(task.generated_file):
            return Response({"error": "File not found"}, 
                           status=status.HTTP_404_NOT_FOUND)
        
        # Create download filename
        filename = f"{task.topic[:50]}.docx".replace(' ', '_')
        response = FileHandler.create_download_response(task.generated_file, filename)
        
        if response:
            return response
        else:
            return Response({"error": "Failed to prepare download"}, 
                           status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except DocumentGenerationTask.DoesNotExist:
        return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_document_preview(request, task_id):
    """Get document preview information"""
    try:
        task = DocumentGenerationTask.objects.get(id=task_id, user=request.user)
        serializer = DocumentGenerationTaskSerializer(task)
        
        # Add file info to response
        response_data = serializer.data
        response_data['file_available'] = FileHandler.file_exists(task.generated_file)
        response_data['file_size'] = FileHandler.get_file_size(task.generated_file)
        response_data['download_url'] = f"/api/documents/tasks/{task_id}/download/"
        
        return Response(response_data)
            
    except DocumentGenerationTask.DoesNotExist:
        return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_document(request, task_id):
    """Delete document and task"""
    try:
        task = DocumentGenerationTask.objects.get(id=task_id, user=request.user)
        
        # Delete physical file
        if task.generated_file:
            FileHandler.delete_file(task.generated_file)
        
        # Delete database record
        task.delete()
        
        return Response({"message": "Document deleted successfully"})
            
    except DocumentGenerationTask.DoesNotExist:
        return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)




# documents/views.py - Add template views
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def document_generate(request):
    """Document generation form"""
    from .models import DocumentTemplate
    
    templates = DocumentTemplate.objects.filter(is_active=True)
    
    context = {
        'templates': templates
    }
    return render(request, 'documents/generate.html', context)

@login_required
def document_list(request):
    """User's document list"""
    documents = DocumentGenerationTask.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'documents': documents
    }
    return render(request, 'documents/list.html', context)

@login_required
def document_detail(request, task_id):
    """Document detail view"""
    try:
        document = DocumentGenerationTask.objects.get(id=task_id, user=request.user)
    except DocumentGenerationTask.DoesNotExist:
        messages.error(request, "文档不存在")
        return redirect('document_list')
    
    context = {
        'document': document
    }
    return render(request, 'documents/detail.html', context)