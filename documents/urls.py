# documents/urls.py
from django.urls import path
from . import views

# documents/urls.py - Update urlpatterns
urlpatterns = [
    path('templates/', views.get_templates, name='templates'),
    path('generate/', views.generate_document, name='generate_document'),
    path('tasks/', views.get_user_tasks, name='user_tasks'),
    path('tasks/<int:task_id>/', views.get_task_detail, name='task_detail'),
    path('tasks/<int:task_id>/download/', views.download_document, name='download_document'),
    path('tasks/<int:task_id>/preview/', views.get_document_preview, name='document_preview'),
    path('tasks/<int:task_id>/delete/', views.delete_document, name='delete_document'),
]