"""
JWT/OAuth 2.0 Authentication Module
Handles token generation, validation, and refresh
"""
from datetime import datetime, timedelta
from typing import Optional, Dict
import jwt
import json
import os
from config import settings
import requests

# ===================== JWT TOKEN MANAGEMENT =====================

def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
    """Generate JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: Dict) -> str:
    """Generate JWT refresh token with longer expiration"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_EXPIRATION_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[Dict]:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def refresh_access_token(refresh_token: str) -> Optional[str]:
    """Generate new access token from refresh token"""
    payload = verify_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        return None
    
    # Remove old token fields
    payload.pop("exp", None)
    payload.pop("iat", None)
    payload.pop("type", None)
    
    return create_access_token(payload)

# ===================== FACEBOOK OAUTH 2.0 =====================

def get_facebook_auth_url(state: str = "") -> str:
    """Generate Facebook OAuth authorization URL"""
    params = {
        'client_id': settings.FACEBOOK_CLIENT_ID,
        'redirect_uri': settings.FACEBOOK_OAUTH_REDIRECT,
        'scope': 'pages_manage_posts,instagram_basic,instagram_graph_user_profile',
        'response_type': 'code',
        'state': state
    }
    query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
    return f"https://www.facebook.com/v18.0/dialog/oauth?{query_string}"

def exchange_facebook_code(code: str) -> Optional[Dict]:
    """Exchange Facebook authorization code for access token"""
    try:
        token_url = "https://graph.facebook.com/v18.0/oauth/access_token"
        params = {
            'client_id': settings.FACEBOOK_CLIENT_ID,
            'client_secret': settings.FACEBOOK_CLIENT_SECRET,
            'redirect_uri': settings.FACEBOOK_OAUTH_REDIRECT,
            'code': code
        }
        response = requests.get(token_url, params=params)
        data = response.json()
        
        if 'access_token' in data:
            # Save token to file
            with open(settings.FACEBOOK_ACCESS_TOKEN_PATH, 'w') as f:
                json.dump(data, f)
            return data
        return None
    except Exception as e:
        print(f"Facebook token exchange error: {e}")
        return None

def get_facebook_access_token() -> Optional[str]:
    """Retrieve stored Facebook access token"""
    try:
        if os.path.exists(settings.FACEBOOK_ACCESS_TOKEN_PATH):
            with open(settings.FACEBOOK_ACCESS_TOKEN_PATH, 'r') as f:
                data = json.load(f)
                return data.get('access_token')
    except Exception as e:
        print(f"Error reading Facebook token: {e}")
    return None

# ===================== LINKEDIN OAUTH 2.0 =====================

def get_linkedin_auth_url(state: str = "") -> str:
    """Generate LinkedIn OAuth authorization URL"""
    params = {
        'response_type': 'code',
        'client_id': settings.LINKEDIN_CLIENT_ID,
        'redirect_uri': settings.LINKEDIN_OAUTH_REDIRECT,
        'scope': 'w_member_social,r_member_social',
        'state': state
    }
    query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
    return f"https://www.linkedin.com/oauth/v2/authorization?{query_string}"

def exchange_linkedin_code(code: str) -> Optional[Dict]:
    """Exchange LinkedIn authorization code for access token"""
    try:
        token_url = "https://www.linkedin.com/oauth/v2/accessToken"
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': settings.LINKEDIN_OAUTH_REDIRECT,
            'client_id': settings.LINKEDIN_CLIENT_ID,
            'client_secret': settings.LINKEDIN_CLIENT_SECRET
        }
        response = requests.post(token_url, data=data)
        token_data = response.json()
        
        if 'access_token' in token_data:
            # Save token to file
            with open(settings.LINKEDIN_ACCESS_TOKEN_PATH, 'w') as f:
                json.dump(token_data, f)
            return token_data
        return None
    except Exception as e:
        print(f"LinkedIn token exchange error: {e}")
        return None

def get_linkedin_access_token() -> Optional[str]:
    """Retrieve stored LinkedIn access token"""
    try:
        if os.path.exists(settings.LINKEDIN_ACCESS_TOKEN_PATH):
            with open(settings.LINKEDIN_ACCESS_TOKEN_PATH, 'r') as f:
                data = json.load(f)
                return data.get('access_token')
    except Exception as e:
        print(f"Error reading LinkedIn token: {e}")
    return None

def refresh_linkedin_token(refresh_token: str) -> Optional[Dict]:
    """Refresh LinkedIn access token"""
    try:
        token_url = "https://www.linkedin.com/oauth/v2/accessToken"
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'client_id': settings.LINKEDIN_CLIENT_ID,
            'client_secret': settings.LINKEDIN_CLIENT_SECRET
        }
        response = requests.post(token_url, data=data)
        token_data = response.json()
        
        if 'access_token' in token_data:
            with open(settings.LINKEDIN_ACCESS_TOKEN_PATH, 'w') as f:
                json.dump(token_data, f)
            return token_data
        return None
    except Exception as e:
        print(f"LinkedIn token refresh error: {e}")
        return None

# ===================== DEPRECATED METHODS (For Reference) =====================
# These methods are deprecated and should not be used
# Use OAuth 2.0 methods above instead

def load_token_from_file(path: str) -> Optional[str]:
    """Legacy method - Use get_facebook_access_token() or get_linkedin_access_token() instead"""
    try:
        if os.path.exists(path):
            with open(path, 'r') as f:
                data = json.load(f)
                return data.get('access_token')
    except:
        pass
    return None

