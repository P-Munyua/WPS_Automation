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
    list_display = ('email', 'phone_number', 'login_method', 'is_verified', 
                   'document_count', 'is_staff', 'is_active', 'created_at')
    
    def document_count(self, obj):
        count = DocumentGenerationTask.objects.filter(user=obj).count()
        url = reverse('admin:documents_documentgenerationtask_changelist')
        return format_html('<a href="{}?user__id__exact={}">{}</a>', url, obj.id, count)
    document_count.short_description = '文档数量'



admin.site.register(User, CustomUserAdmin)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'company', 'position', 'usage_count', 
                   'last_activity', 'subscription_status')
    search_fields = ('user__email', 'user__phone_number', 'company')
    
    def subscription_status(self, obj):
        try:
            subscription = UserSubscription.objects.get(user=obj.user)
            return format_html(
                '<span style="color: {};">{}</span>',
                'green' if subscription.is_active() else 'red',
                subscription.plan.name
            )
        except UserSubscription.DoesNotExist:
            return "无订阅"
    subscription_status.short_description = '订阅状态'