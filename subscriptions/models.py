# subscriptions/models.py
from django.db import models
from django.conf import settings

class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2)
    price_yearly = models.DecimalField(max_digits=10, decimal_places=2)
    max_documents_per_month = models.IntegerField()
    max_words_per_document = models.IntegerField()
    supports_charts = models.BooleanField(default=False)
    supports_formulas = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class UserSubscription(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    documents_used_this_month = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user} - {self.plan}"