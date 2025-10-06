# subscriptions/admin.py
from django.contrib import admin
from .models import SubscriptionPlan, UserSubscription

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'price_monthly', 'price_yearly', 'max_documents_per_month', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']

@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'start_date', 'end_date', 'is_active', 'documents_used_this_month']
    list_filter = ['is_active', 'plan']
    search_fields = ['user__email', 'user__phone_number']