# subscriptions/urls_frontend.py
from django.urls import path
from . import views_frontend

urlpatterns = [
    path('plans/', views_frontend.subscription_plans, name='subscription'),
    path('payment-history/', views_frontend.payment_history, name='payment_history'),
]
