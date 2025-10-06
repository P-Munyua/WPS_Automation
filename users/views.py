# users/views.py
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User
from .serializers import UserRegistrationSerializer, UserSerializer

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    email = request.data.get('email')
    phone_number = request.data.get('phone_number')
    password = request.data.get('password')
    
    if not password:
        return Response({"error": "Password is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Try to find user by email or phone
    user = None
    if email:
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            pass
    elif phone_number:
        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            pass
    
    if user and user.check_password(password):
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })
    
    return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user_profile(request):
    serializer = UserSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




# users/views.py - Add these imports
from rest_framework_simplejwt.tokens import RefreshToken
from utils.wechat_auth import WeChatAuth
from .serializers import UserSerializer

# Add these new views to users/views.py

@api_view(['POST'])
@permission_classes([AllowAny])
def wechat_login(request):
    """Handle WeChat OAuth login"""
    code = request.data.get('code')
    
    if not code:
        return Response({"error": "WeChat authorization code is required"}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    wechat_auth = WeChatAuth()
    token_data, error = wechat_auth.get_access_token(code)
    
    if error:
        return Response({"error": f"WeChat authentication failed: {error}"}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    # Get user info from WeChat
    user_info, error = wechat_auth.get_user_info(
        token_data['access_token'], 
        token_data['openid']
    )
    
    if error:
        return Response({"error": f"Failed to get user info: {error}"}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    # Create or update user
    user = wechat_auth.create_or_update_user(user_info)
    
    # Generate JWT tokens
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'user': UserSerializer(user).data,
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def link_wechat_account(request):
    """Link WeChat account to existing user"""
    code = request.data.get('code')
    
    if not code:
        return Response({"error": "WeChat authorization code is required"}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    wechat_auth = WeChatAuth()
    token_data, error = wechat_auth.get_access_token(code)
    
    if error:
        return Response({"error": f"WeChat authentication failed: {error}"}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    # Check if WeChat account is already linked to another user
    openid = token_data['openid']
    if User.objects.filter(wechat_openid=openid).exclude(id=request.user.id).exists():
        return Response({"error": "This WeChat account is already linked to another user"}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    # Link WeChat to current user
    request.user.wechat_openid = openid
    request.user.login_method = User.WE_CHAT
    
    # Get and update user info from WeChat
    user_info, error = wechat_auth.get_user_info(
        token_data['access_token'], 
        openid
    )
    
    if not error and user_info:
        request.user.avatar_url = user_info.get('headimgurl', request.user.avatar_url)
    
    request.user.save()
    
    return Response({
        'user': UserSerializer(request.user).data,
        'message': 'WeChat account linked successfully'
    })




# users/views.py - Add these imports
from utils.sms_verification import SMSVerification

# Add these new views

@api_view(['POST'])
@permission_classes([AllowAny])
def send_sms_code(request):
    """Send SMS verification code"""
    phone_number = request.data.get('phone_number')
    country_code = request.data.get('country_code', '+86')
    
    if not phone_number:
        return Response({"error": "Phone number is required"}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    sms_service = SMSVerification()
    success = sms_service.send_verification_code(phone_number, country_code)
    
    if success:
        return Response({"message": "Verification code sent successfully"})
    else:
        return Response({"error": "Failed to send verification code"}, 
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_sms_code(request):
    """Verify SMS code and login/register user"""
    phone_number = request.data.get('phone_number')
    code = request.data.get('code')
    country_code = request.data.get('country_code', '+86')
    
    if not phone_number or not code:
        return Response({"error": "Phone number and code are required"}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    sms_service = SMSVerification()
    is_valid, message = sms_service.verify_code(phone_number, code, country_code)
    
    if not is_valid:
        return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)
    
    # Find or create user
    try:
        user = User.objects.get(phone_number=phone_number)
    except User.DoesNotExist:
        # Create new user with phone number
        user = User.objects.create(
            phone_number=phone_number,
            country_code=country_code,
            login_method=User.MOBILE,
            is_verified=True
        )
        UserProfile.objects.create(user=user)
    else:
        # Mark existing user as verified
        user.is_verified = True
        user.save()
    
    # Generate JWT tokens
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'user': UserSerializer(user).data,
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'message': message
    })




# users/views.py - Add these imports
from documents.models import DocumentGenerationTask
from subscriptions.models import UserSubscription
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

# Add these new views

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_dashboard(request):
    """Get user dashboard data"""
    user = request.user
    
    # Get subscription info
    try:
        subscription = UserSubscription.objects.get(user=user)
        subscription_data = UserSubscriptionSerializer(subscription).data
    except UserSubscription.DoesNotExist:
        subscription_data = None
    
    # Get document statistics
    total_documents = DocumentGenerationTask.objects.filter(user=user).count()
    completed_documents = DocumentGenerationTask.objects.filter(
        user=user, 
        status=DocumentGenerationTask.COMPLETED
    ).count()
    
    # Recent documents (last 7 days)
    seven_days_ago = timezone.now() - timedelta(days=7)
    recent_documents = DocumentGenerationTask.objects.filter(
        user=user,
        created_at__gte=seven_days_ago
    ).count()
    
    # Document status breakdown
    status_breakdown = DocumentGenerationTask.objects.filter(user=user).values(
        'status'
    ).annotate(count=Count('id'))
    
    # Monthly usage
    current_month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_documents = DocumentGenerationTask.objects.filter(
        user=user,
        created_at__gte=current_month_start
    ).count()
    
    # Recent activity (last 5 tasks)
    recent_tasks = DocumentGenerationTask.objects.filter(
        user=user
    ).order_by('-created_at')[:5]
    
    from documents.serializers import DocumentGenerationTaskSerializer
    recent_tasks_data = DocumentGenerationTaskSerializer(recent_tasks, many=True).data
    
    return Response({
        'user': UserSerializer(user).data,
        'subscription': subscription_data,
        'statistics': {
            'total_documents': total_documents,
            'completed_documents': completed_documents,
            'recent_documents': recent_documents,
            'monthly_documents': monthly_documents,
            'status_breakdown': status_breakdown,
        },
        'recent_activity': recent_tasks_data,
        'limits': {
            'max_documents': subscription.plan.max_documents_per_month if subscription else 5,
            'documents_used': subscription.documents_used_this_month if subscription else 0,
            'remaining_documents': (
                subscription.plan.max_documents_per_month - subscription.documents_used_this_month 
                if subscription else 5
            ),
        } if subscription else None
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_analytics(request):
    """Get user analytics data"""
    user = request.user
    
    # Daily document count for the last 30 days
    thirty_days_ago = timezone.now() - timedelta(days=30)
    
    daily_stats = DocumentGenerationTask.objects.filter(
        user=user,
        created_at__gte=thirty_days_ago
    ).extra({
        'date': "DATE(created_at)"
    }).values('date').annotate(
        count=Count('id')
    ).order_by('date')
    
    # Word count statistics
    word_stats = DocumentGenerationTask.objects.filter(
        user=user,
        status=DocumentGenerationTask.COMPLETED
    ).aggregate(
        total_words=Count('word_count'),
        avg_words=models.Avg('word_count'),
        max_words=models.Max('word_count')
    )
    
    # Most common topics (simplified)
    common_topics = DocumentGenerationTask.objects.filter(
        user=user
    ).values('topic').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    return Response({
        'daily_activity': list(daily_stats),
        'word_statistics': word_stats,
        'common_topics': list(common_topics),
        'time_period': 'last_30_days'
    })


# Create new app for analytics or add to existing views
# Let's create it in users/views.py for now

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def system_analytics(request):
    """Get system-wide analytics (admin only)"""
    if not request.user.is_staff:
        return Response({"error": "Permission denied"}, 
                       status=status.HTTP_403_FORBIDDEN)
    
    # User growth (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    user_growth = User.objects.filter(
        date_joined__gte=thirty_days_ago
    ).extra({
        'date': "DATE(date_joined)"
    }).values('date').annotate(
        count=Count('id')
    ).order_by('date')
    
    # Document generation trends
    doc_trends = DocumentGenerationTask.objects.filter(
        created_at__gte=thirty_days_ago
    ).extra({
        'date': "DATE(created_at)"
    }).values('date').annotate(
        total=Count('id'),
        completed=Count('id', filter=Q(status='completed')),
        failed=Count('id', filter=Q(status='failed'))
    ).order_by('date')
    
    # Subscription distribution
    subscription_dist = UserSubscription.objects.values(
        'plan__name'
    ).annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Popular topics
    popular_topics = DocumentGenerationTask.objects.values(
        'topic'
    ).annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    return Response({
        'user_growth': list(user_growth),
        'document_trends': list(doc_trends),
        'subscription_distribution': list(subscription_dist),
        'popular_topics': list(popular_topics),
        'time_period': 'last_30_days'
    })




# users/views.py - Add template-based views
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def dashboard(request):
    """User dashboard template view"""
    # Get user data for dashboard
    from documents.models import DocumentGenerationTask
    from subscriptions.models import UserSubscription
    
    # Recent documents
    recent_documents = DocumentGenerationTask.objects.filter(
        user=request.user
    ).order_by('-created_at')[:5]
    
    # Subscription info
    try:
        subscription = UserSubscription.objects.get(user=request.user)
    except UserSubscription.DoesNotExist:
        subscription = None
    
    # Statistics
    total_docs = DocumentGenerationTask.objects.filter(user=request.user).count()
    completed_docs = DocumentGenerationTask.objects.filter(
        user=request.user, 
        status=DocumentGenerationTask.COMPLETED
    ).count()
    
    context = {
        'recent_documents': recent_documents,
        'subscription': subscription,
        'total_docs': total_docs,
        'completed_docs': completed_docs,
    }
    
    return render(request, 'dashboard/dashboard.html', context)


# users/views.py - Add profile view
@login_required
def profile_view(request):
    """User profile page"""
    if request.method == 'POST':
        # Handle profile update
        user = request.user
        user.email = request.POST.get('email', user.email)
        user.phone_number = request.POST.get('phone_number', user.phone_number)
        user.country_code = request.POST.get('country_code', user.country_code)
        user.save()
        
        # Update profile
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.company = request.POST.get('company', '')
        profile.position = request.POST.get('position', '')
        profile.save()
        
        messages.success(request, '个人资料更新成功！')
        return redirect('profile')
    
    context = {
        'user': request.user
    }
    return render(request, 'auth/profile.html', context)

@login_required
def logout_view(request):
    """Logout user"""
    from django.contrib.auth import logout
    logout(request)
    messages.success(request, '您已成功退出登录')
    return redirect('login')