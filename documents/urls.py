# documents/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('templates/', views.get_templates, name='templates'),
    path('generate/', views.generate_document, name='generate_document'),
    path('tasks/', views.get_user_tasks, name='user_tasks'),
    path('tasks/<int:task_id>/', views.get_task_detail, name='task_detail'),
]