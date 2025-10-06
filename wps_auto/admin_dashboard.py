# wps_auto/admin_dashboard.py
from django.contrib import admin
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from users.models import User
from documents.models import DocumentGenerationTask
from subscriptions.models import SubscriptionPlan, UserSubscription

class CustomAdminSite(admin.AdminSite):
    site_header = "WPS办公自动化系统管理"
    site_title = "WPS自动化系统"
    index_title = "系统概览"
    
    def index(self, request, extra_context=None):
        # Get statistics for admin dashboard
        extra_context = extra_context or {}
        
        # User statistics
        total_users = User.objects.count()
        new_users_today = User.objects.filter(
            date_joined__date=timezone.now().date()
        ).count()
        active_users = User.objects.filter(
            last_login__gte=timezone.now() - timedelta(days=30)
        ).count()
        
        # Document statistics
        total_documents = DocumentGenerationTask.objects.count()
        completed_documents = DocumentGenerationTask.objects.filter(
            status=DocumentGenerationTask.COMPLETED
        ).count()
        failed_documents = DocumentGenerationTask.objects.filter(
            status=DocumentGenerationTask.FAILED
        ).count()
        
        # Subscription statistics
        total_subscriptions = UserSubscription.objects.count()
        active_subscriptions = UserSubscription.objects.filter(
            status=UserSubscription.ACTIVE
        ).count()
        
        # Recent activity
        recent_tasks = DocumentGenerationTask.objects.select_related('user').order_by('-created_at')[:10]
        
        extra_context.update({
            'total_users': total_users,
            'new_users_today': new_users_today,
            'active_users': active_users,
            'total_documents': total_documents,
            'completed_documents': completed_documents,
            'failed_documents': failed_documents,
            'success_rate': (completed_documents / total_documents * 100) if total_documents > 0 else 0,
            'total_subscriptions': total_subscriptions,
            'active_subscriptions': active_subscriptions,
            'recent_tasks': recent_tasks,
        })
        
        return super().index(request, extra_context)

# Replace the default admin site
admin_site = CustomAdminSite()

# Register all models with the custom admin site
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

admin_site.register(Group)