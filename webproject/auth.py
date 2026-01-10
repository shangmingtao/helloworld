"""
认证相关模块
"""
from datetime import datetime, timedelta
from typing import Optional, Dict
import hashlib
import secrets

class AuthService:
    """认证服务类"""
    
    def __init__(self):
        self.sessions: Dict[str, dict] = {}
        self.session_timeout = timedelta(hours=2)
    
    @staticmethod
    def hash_password(password: str) -> str:
        """密码哈希（简单示例，实际项目中应使用更安全的方法）"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def generate_token(self, user_id: int, username: str) -> str:
        """生成会话令牌"""
        token = secrets.token_urlsafe(32)
        self.sessions[token] = {
            'user_id': user_id,
            'username': username,
            'created_at': datetime.now(),
            'expires_at': datetime.now() + self.session_timeout
        }
        return token
    
    def validate_token(self, token: str) -> Optional[dict]:
        """验证令牌"""
        if token not in self.sessions:
            return None
        
        session = self.sessions[token]
        if datetime.now() > session['expires_at']:
            del self.sessions[token]
            return None
        
        return session
    
    def logout(self, token: str) -> bool:
        """用户注销"""
        if token in self.sessions:
            del self.sessions[token]
            return True
        return False
    
    def cleanup_expired_sessions(self):
        """清理过期会话"""
        now = datetime.now()
        expired_tokens = [
            token for token, session in self.sessions.items()
            if now > session['expires_at']
        ]
        for token in expired_tokens:
            del self.sessions[token]

# 全局认证服务实例
auth_service = AuthService()