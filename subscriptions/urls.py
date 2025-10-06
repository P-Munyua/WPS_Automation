# subscriptions/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('plans/', views.get_subscription_plans, name='subscription_plans'),
    path('current/', views.get_user_subscription, name='current_subscription'),
    path('upgrade/', views.upgrade_subscription, name='upgrade_subscription'),
    path('cancel/', views.cancel_subscription, name='cancel_subscription'),
    path('payments/', views.get_payment_history, name='payment_history'),
]