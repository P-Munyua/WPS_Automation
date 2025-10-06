# subscriptions/views.py
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from .models import SubscriptionPlan, UserSubscription, PaymentHistory
from .serializers import (
    SubscriptionPlanSerializer, UserSubscriptionSerializer,
    PaymentHistorySerializer, SubscriptionUpgradeSerializer
)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_subscription_plans(request):
    """Get all available subscription plans"""
    plans = SubscriptionPlan.objects.filter(is_active=True).order_by('price_monthly')
    serializer = SubscriptionPlanSerializer(plans, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_subscription(request):
    """Get user's current subscription"""
    try:
        subscription = UserSubscription.objects.get(user=request.user)
        serializer = UserSubscriptionSerializer(subscription)
        return Response(serializer.data)
    except UserSubscription.DoesNotExist:
        # Create free subscription if doesn't exist
        free_plan = SubscriptionPlan.objects.filter(tier=SubscriptionPlan.FREE).first()
        if free_plan:
            subscription = UserSubscription.objects.create(
                user=request.user,
                plan=free_plan,
                end_date=timezone.now() + timedelta(days=365 * 10)  # 10 years for free plan
            )
            serializer = UserSubscriptionSerializer(subscription)
            return Response(serializer.data)
        return Response({"error": "No subscription plan available"}, 
                       status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upgrade_subscription(request):
    """Upgrade user subscription"""
    serializer = SubscriptionUpgradeSerializer(data=request.data)
    
    if serializer.is_valid():
        plan_id = serializer.validated_data['plan_id']
        billing_cycle = serializer.validated_data['billing_cycle']
        payment_method = serializer.validated_data['payment_method']
        
        try:
            plan = SubscriptionPlan.objects.get(id=plan_id, is_active=True)
            
            # Calculate price and end date
            if billing_cycle == 'yearly':
                amount = plan.price_yearly
                duration = timedelta(days=365)
            else:
                amount = plan.price_monthly
                duration = timedelta(days=30)
            
            # Create payment record
            payment = PaymentHistory.objects.create(
                user=request.user,
                plan=plan,
                amount=amount,
                payment_method=payment_method,
                status='completed'  # For demo - in production, wait for actual payment
            )
            
            # Update or create user subscription
            user_subscription, created = UserSubscription.objects.get_or_create(
                user=request.user,
                defaults={
                    'plan': plan,
                    'end_date': timezone.now() + duration
                }
            )
            
            if not created:
                user_subscription.plan = plan
                user_subscription.status = UserSubscription.ACTIVE
                user_subscription.end_date = timezone.now() + duration
                user_subscription.save()
            
            # Return updated subscription info
            subscription_serializer = UserSubscriptionSerializer(user_subscription)
            
            return Response({
                'subscription': subscription_serializer.data,
                'payment': PaymentHistorySerializer(payment).data,
                'message': 'Subscription upgraded successfully'
            })
            
        except SubscriptionPlan.DoesNotExist:
            return Response({"error": "Subscription plan not found"}, 
                           status=status.HTTP_404_NOT_FOUND)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_payment_history(request):
    """Get user's payment history"""
    payments = PaymentHistory.objects.filter(user=request.user).order_by('-created_at')
    serializer = PaymentHistorySerializer(payments, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_subscription(request):
    """Cancel user subscription"""
    try:
        subscription = UserSubscription.objects.get(user=request.user)
        
        if subscription.plan.tier == SubscriptionPlan.FREE:
            return Response({"error": "Cannot cancel free subscription"}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        subscription.status = UserSubscription.CANCELED
        subscription.save()
        
        serializer = UserSubscriptionSerializer(subscription)
        return Response({
            'subscription': serializer.data,
            'message': 'Subscription canceled successfully'
        })
        
    except UserSubscription.DoesNotExist:
        return Response({"error": "Subscription not found"}, 
                       status=status.HTTP_404_NOT_FOUND)



# subscriptions/views_frontend.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import SubscriptionPlan, UserSubscription, PaymentHistory

@login_required
def subscription_plans(request):
    """Subscription plans page"""
    plans = SubscriptionPlan.objects.filter(is_active=True).order_by('price_monthly')
    
    try:
        current_subscription = UserSubscription.objects.get(user=request.user)
    except UserSubscription.DoesNotExist:
        current_subscription = None
    
    context = {
        'plans': plans,
        'current_subscription': current_subscription
    }
    return render(request, 'subscriptions/plans.html', context)

@login_required
def payment_history(request):
    """User payment history"""
    payments = PaymentHistory.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'payments': payments
    }
    return render(request, 'subscriptions/payment_history.html', context)