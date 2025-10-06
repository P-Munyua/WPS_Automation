# wps_auto/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('users.urls')),
    path('api/documents/', include('documents.urls')),
    path('api/subscriptions/', include('subscriptions.urls')),
    path('', include('users.urls_frontend')),
    path('documents/', include('documents.urls_frontend')),
    path('subscriptions/', include('subscriptions.urls_frontend')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)