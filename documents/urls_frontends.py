from django.urls import path
from . import views

urlpatterns = [
    path('generate/', views.document_generate, name='document_generate'),
    path('generate/submit/', views.generate_document, name='document_generate_submit'),
    path('list/', views.document_list, name='document_list'),
    path('detail/<int:task_id>/', views.document_detail, name='document_detail'),
    path('download/<int:task_id>/', views.download_document, name='document_download'),
]