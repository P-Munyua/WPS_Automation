# subscriptions/serializers.py
from rest_framework import serializers
from .models import SubscriptionPlan, UserSubscription, PaymentHistory

class SubscriptionPlanSerializer(serializers.ModelSerializer):
    features = serializers.SerializerMethodField()

    class Meta:
        model = SubscriptionPlan
        fields = [
            'id', 'name', 'tier', 'description', 'price_monthly', 'price_yearly',
            'max_documents_per_month', 'max_words_per_document', 
            'supports_charts', 'supports_formulas', 'supports_templates',
            'priority_processing', 'features'
        ]

    def get_features(self, obj):
        features = []
        if obj.supports_charts:
            features.append("图表生成")
        if obj.supports_formulas:
            features.append("数学公式")
        if obj.supports_templates:
            features.append("专业模板")
        if obj.priority_processing:
            features.append("优先处理")
        features.append(f"每月 {obj.max_documents_per_month} 个文档")
        features.append(f"每文档最多 {obj.max_words_per_document} 字")
        return features

class UserSubscriptionSerializer(serializers.ModelSerializer):
    plan = SubscriptionPlanSerializer(read_only=True)
    plan_id = serializers.IntegerField(write_only=True, required=False)
    is_active = serializers.SerializerMethodField()
    days_remaining = serializers.SerializerMethodField()
    usage_percentage = serializers.SerializerMethodField()

    class Meta:
        model = UserSubscription
        fields = [
            'id', 'plan', 'plan_id', 'status', 'start_date', 'end_date',
            'documents_used_this_month', 'is_active', 'days_remaining',
            'usage_percentage'
        ]
        read_only_fields = ['id', 'status', 'start_date', 'end_date', 'documents_used_this_month']

    def get_is_active(self, obj):
        return obj.is_active()

    def get_days_remaining(self, obj):
        if obj.is_active():
            from django.utils import timezone
            remaining = obj.end_date - timezone.now()
            return max(0, remaining.days)
        return 0

    def get_usage_percentage(self, obj):
        if obj.plan.max_documents_per_month > 0:
            return min(100, int((obj.documents_used_this_month / obj.plan.max_documents_per_month) * 100))
        return 0

class PaymentHistorySerializer(serializers.ModelSerializer):
    plan_name = serializers.CharField(source='plan.name', read_only=True)

    class Meta:
        model = PaymentHistory
        fields = [
            'id', 'plan', 'plan_name', 'amount', 'currency', 
            'payment_method', 'status', 'created_at'
        ]
        read_only_fields = fields

class SubscriptionUpgradeSerializer(serializers.Serializer):
    plan_id = serializers.IntegerField(required=True)
    payment_method = serializers.ChoiceField(
        choices=[('wechat', '微信支付'), ('alipay', '支付宝')],
        default='wechat'
    )
    billing_cycle = serializers.ChoiceField(
        choices=[('monthly', '月付'), ('yearly', '年付')],
        default='monthly'
    )

    def validate_plan_id(self, value):
        from .models import SubscriptionPlan
        if not SubscriptionPlan.objects.filter(id=value, is_active=True).exists():
            raise serializers.ValidationError("无效的套餐ID")
        return value