# subscriptions/management/commands/seed_plans.py
from django.core.management.base import BaseCommand
from subscriptions.models import SubscriptionPlan

class Command(BaseCommand):
    help = 'Seed initial subscription plans'
    
    def handle(self, *args, **options):
        plans = [
            {
                'name': '免费版',
                'tier': SubscriptionPlan.FREE,
                'description': '适合个人用户试用，体验基本功能',
                'price_monthly': 0,
                'price_yearly': 0,
                'max_documents_per_month': 5,
                'max_words_per_document': 1500,
                'supports_charts': False,
                'supports_formulas': False,
                'supports_templates': False,
                'priority_processing': False,
            },
            {
                'name': '基础版', 
                'tier': SubscriptionPlan.BASIC,
                'description': '适合学生和个人用户，满足基本文档生成需求',
                'price_monthly': 29,
                'price_yearly': 299,
                'max_documents_per_month': 20,
                'max_words_per_document': 3000,
                'supports_charts': True,
                'supports_formulas': False,
                'supports_templates': True,
                'priority_processing': False,
            },
            {
                'name': '专业版',
                'tier': SubscriptionPlan.PROFESSIONAL, 
                'description': '适合专业人士和团队，支持高级功能',
                'price_monthly': 99,
                'price_yearly': 999,
                'max_documents_per_month': 100,
                'max_words_per_document': 5000,
                'supports_charts': True,
                'supports_formulas': True,
                'supports_templates': True,
                'priority_processing': True,
            },
            {
                'name': '企业版',
                'tier': SubscriptionPlan.ENTERPRISE,
                'description': '适合企业用户，无限制使用所有功能',
                'price_monthly': 299,
                'price_yearly': 2999,
                'max_documents_per_month': 1000,
                'max_words_per_document': 10000,
                'supports_charts': True,
                'supports_formulas': True,
                'supports_templates': True,
                'priority_processing': True,
            }
        ]
        
        for plan_data in plans:
            plan, created = SubscriptionPlan.objects.get_or_create(
                name=plan_data['name'],
                defaults=plan_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created plan: {plan.name}')
                )