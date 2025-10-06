# subscriptions/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

class SubscriptionPlan(models.Model):
    FREE = 'free'
    BASIC = 'basic'
    PROFESSIONAL = 'professional'
    ENTERPRISE = 'enterprise'
    PLAN_TIERS = [
        (FREE, '免费版'),
        (BASIC, '基础版'),
        (PROFESSIONAL, '专业版'),
        (ENTERPRISE, '企业版'),
    ]
    
    name = models.CharField(max_length=50, verbose_name="套餐名称")
    tier = models.CharField(max_length=20, choices=PLAN_TIERS, default=FREE, verbose_name="套餐等级")
    description = models.TextField(verbose_name="套餐描述")
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="月价格")
    price_yearly = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="年价格")
    
    # Limits
    max_documents_per_month = models.IntegerField(default=5, verbose_name="每月最大文档数")
    max_words_per_document = models.IntegerField(default=2000, verbose_name="每文档最大字数")
    supports_charts = models.BooleanField(default=False, verbose_name="支持图表")
    supports_formulas = models.BooleanField(default=False, verbose_name="支持公式")
    supports_templates = models.BooleanField(default=False, verbose_name="支持模板")
    priority_processing = models.BooleanField(default=False, verbose_name="优先处理")
    
    is_active = models.BooleanField(default=True, verbose_name="是否激活")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "订阅套餐"
        verbose_name_plural = "订阅套餐"
        ordering = ['price_monthly']

    def __str__(self):
        return f"{self.get_tier_display()} - {self.name}"

class UserSubscription(models.Model):
    ACTIVE = 'active'
    CANCELED = 'canceled'
    EXPIRED = 'expired'
    STATUS_CHOICES = [
        (ACTIVE, '活跃'),
        (CANCELED, '已取消'),
        (EXPIRED, '已过期'),
    ]
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="用户")
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE, verbose_name="套餐")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=ACTIVE, verbose_name="状态")
    
    # Subscription dates
    start_date = models.DateTimeField(default=timezone.now, verbose_name="开始时间")
    end_date = models.DateTimeField(verbose_name="结束时间")
    
    # Usage tracking
    documents_used_this_month = models.IntegerField(default=0, verbose_name="本月已用文档数")
    last_reset_date = models.DateTimeField(default=timezone.now, verbose_name="最后重置时间")
    
    # Payment info
    stripe_subscription_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="Stripe订阅ID")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "用户订阅"
        verbose_name_plural = "用户订阅"

    def __str__(self):
        return f"{self.user} - {self.plan.name}"

    def is_active(self):
        """Check if subscription is active and not expired"""
        return self.status == self.ACTIVE and timezone.now() < self.end_date

    def reset_monthly_usage(self):
        """Reset monthly usage counter"""
        now = timezone.now()
        if now.month != self.last_reset_date.month or now.year != self.last_reset_date.year:
            self.documents_used_this_month = 0
            self.last_reset_date = now
            self.save()

    def can_generate_document(self, word_count=0):
        """Check if user can generate a new document"""
        if not self.is_active():
            return False, "订阅已过期或已取消"
        
        self.reset_monthly_usage()
        
        if self.documents_used_this_month >= self.plan.max_documents_per_month:
            return False, "本月文档生成次数已用完"
        
        if word_count > self.plan.max_words_per_document:
            return False, f"文档字数超过限制（最大{self.plan.max_words_per_document}字）"
        
        return True, "可以生成文档"

    def record_document_generation(self, word_count=0):
        """Record document generation and update usage"""
        can_generate, message = self.can_generate_document(word_count)
        if can_generate:
            self.documents_used_this_month += 1
            self.save()
            return True
        return False

class PaymentHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="用户")
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE, verbose_name="套餐")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="支付金额")
    currency = models.CharField(max_length=3, default='CNY', verbose_name="货币")
    payment_method = models.CharField(max_length=50, default='wechat', verbose_name="支付方式")
    stripe_payment_intent_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="Stripe支付ID")
    status = models.CharField(max_length=20, default='pending', verbose_name="支付状态")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "支付记录"
        verbose_name_plural = "支付记录"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - {self.amount} {self.currency}"