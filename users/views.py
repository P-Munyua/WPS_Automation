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