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