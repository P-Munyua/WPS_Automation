# utils/wechat_auth.py
import requests
from django.conf import settings
from users.models import User, UserProfile

class WeChatAuth:
    def __init__(self):
        self.app_id = settings.WECHAT_APP_ID
        self.app_secret = settings.WECHAT_APP_SECRET
    
    def get_access_token(self, code):
        """Get WeChat access token using authorization code"""
        url = "https://api.weixin.qq.com/sns/oauth2/access_token"
        params = {
            'appid': self.app_id,
            'secret': self.app_secret,
            'code': code,
            'grant_type': 'authorization_code'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if 'errcode' in data:
                return None, data.get('errmsg', 'WeChat API error')
            
            return data, None
        except requests.RequestException as e:
            return None, str(e)
    
    def get_user_info(self, access_token, openid):
        """Get WeChat user info using access token"""
        url = "https://api.weixin.qq.com/sns/userinfo"
        params = {
            'access_token': access_token,
            'openid': openid,
            'lang': 'zh_CN'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if 'errcode' in data:
                return None, data.get('errmsg', 'WeChat API error')
            
            return data, None
        except requests.RequestException as e:
            return None, str(e)
    
    def create_or_update_user(self, wechat_user_info):
        """Create or update user from WeChat user info"""
        openid = wechat_user_info.get('openid')
        nickname = wechat_user_info.get('nickname', '')
        avatar = wechat_user_info.get('headimgurl', '')
        
        try:
            # Try to find existing user with this WeChat openid
            user = User.objects.get(wechat_openid=openid)
            user.avatar_url = avatar
            user.save()
        except User.DoesNotExist:
            # Create new user
            user = User.objects.create(
                wechat_openid=openid,
                login_method=User.WE_CHAT,
                avatar_url=avatar
            )
            
            # Create user profile
            UserProfile.objects.create(user=user)
        
        return user