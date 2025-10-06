# users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserProfile

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('email', 'phone_number', 'login_method', 'is_verified', 'is_staff', 'is_active')
    list_filter = ('login_method', 'is_verified', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('phone_number', 'wechat_openid', 'avatar_url', 'country_code')}),
        ('Permissions', {'fields': ('is_verified', 'is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('email', 'phone_number')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'company', 'position', 'usage_count', 'last_activity')
    search_fields = ('user__email', 'user__phone_number', 'company')

admin.site.register(User, CustomUserAdmin)