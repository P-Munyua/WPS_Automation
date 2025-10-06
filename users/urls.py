# users/urls.py
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

# users/urls.py - Update urlpatterns
urlpatterns = [
    # Authentication
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('wechat/login/', views.wechat_login, name='wechat_login'),
    path('wechat/link/', views.link_wechat_account, name='link_wechat'),
    path('sms/send-code/', views.send_sms_code, name='send_sms_code'),
    path('sms/verify/', views.verify_sms_code, name='verify_sms_code'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # User profile
    path('profile/', views.get_user_profile, name='profile'),
    path('profile/update/', views.update_user_profile, name='update_profile'),
    
    # Dashboard
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('analytics/', views.user_analytics, name='user_analytics'),
    path('system-analytics/', views.system_analytics, name='system_analytics'),
    
]
