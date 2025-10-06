# utils/sms_verification.py
import random
import time
from django.core.cache import cache
from django.conf import settings

class SMSVerification:
    def __init__(self):
        # In production, you would integrate with SMS service provider
        # For development, we'll simulate SMS sending
        self.cache_timeout = 300  # 5 minutes
    
    def generate_verification_code(self):
        """Generate 6-digit verification code"""
        return str(random.randint(100000, 999999))
    
    def send_verification_code(self, phone_number, country_code='+86'):
        """Send verification code to phone number"""
        # Generate verification code
        verification_code = self.generate_verification_code()
        
        # Store in cache with phone number as key
        cache_key = f"sms_verification_{country_code}{phone_number}"
        cache.set(cache_key, verification_code, self.cache_timeout)
        
        # In development, just print the code
        print(f"DEBUG: SMS verification code for {country_code}{phone_number}: {verification_code}")
        
        # In production, integrate with SMS provider like:
        # - Aliyun SMS
        # - Tencent Cloud SMS
        # - Twilio (for international)
        
        return True
    
    def verify_code(self, phone_number, code, country_code='+86'):
        """Verify the SMS code"""
        cache_key = f"sms_verification_{country_code}{phone_number}"
        stored_code = cache.get(cache_key)
        
        if not stored_code:
            return False, "Verification code expired or not sent"
        
        if stored_code != code:
            return False, "Invalid verification code"
        
        # Code verified successfully, remove from cache
        cache.delete(cache_key)
        return True, "Verification successful"