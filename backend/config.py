import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # ===================== GEMINI API (Direct API Key) =====================
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # ===================== FACEBOOK OAUTH 2.0 =====================
    FACEBOOK_CLIENT_ID: str = os.getenv("FACEBOOK_CLIENT_ID", "")
    FACEBOOK_CLIENT_SECRET: str = os.getenv("FACEBOOK_CLIENT_SECRET", "")
    FACEBOOK_ACCESS_TOKEN_PATH: str = os.getenv("FACEBOOK_ACCESS_TOKEN_PATH", "facebook_token.json")
    FACEBOOK_PAGE_ID: str = os.getenv("FACEBOOK_PAGE_ID", "")
    INSTAGRAM_BUSINESS_ACCOUNT_ID: str = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID", "")
    FACEBOOK_OAUTH_REDIRECT: str = os.getenv("FACEBOOK_OAUTH_REDIRECT", "http://localhost:8000/api/auth/facebook/callback")
    
    # ===================== LINKEDIN OAUTH 2.0 =====================
    LINKEDIN_CLIENT_ID: str = os.getenv("LINKEDIN_CLIENT_ID", "")
    LINKEDIN_CLIENT_SECRET: str = os.getenv("LINKEDIN_CLIENT_SECRET", "")
    LINKEDIN_ACCESS_TOKEN_PATH: str = os.getenv("LINKEDIN_ACCESS_TOKEN_PATH", "linkedin_token.json")
    LINKEDIN_PERSON_URN: str = os.getenv("LINKEDIN_PERSON_URN", "")
    LINKEDIN_ORG_URN: str = os.getenv("LINKEDIN_ORG_URN", "")
    LINKEDIN_OAUTH_REDIRECT: str = os.getenv("LINKEDIN_OAUTH_REDIRECT", "http://localhost:8000/api/auth/linkedin/callback")
    
    # ===================== GMAIL OAUTH 2.0 =====================
    GMAIL_CREDENTIALS_PATH: str = os.getenv("GMAIL_CREDENTIALS_PATH", "gmail_credentials.json")
    GMAIL_TOKEN_PATH: str = os.getenv("GMAIL_TOKEN_PATH", "gmail_token.pickle")
    GMAIL_FROM_EMAIL: str = os.getenv("GMAIL_FROM_EMAIL", "")
    
    # ===================== BACKEND JWT/BEARER TOKEN AUTH =====================
    # API security with JWT tokens
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production-12345678")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    JWT_REFRESH_EXPIRATION_DAYS: int = 30
    
    # ===================== FRONTEND OAUTH CALLBACK =====================
    # OAuth redirect URIs for frontend
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
    FRONTEND_OAUTH_CALLBACK: str = os.getenv("FRONTEND_OAUTH_CALLBACK", "http://localhost:5173/auth/callback")
    BACKEND_URL: str = os.getenv("BACKEND_URL", "http://localhost:8000")
    
    # ===================== DATABASE & UPLOADS =====================
    DATABASE_URL: str = "sqlite:///./social_posts.db"
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 5 * 1024 * 1024  # 5MB
    ALLOWED_EXTENSIONS: set = {"jpg", "jpeg", "png", "gif", "webp"}
    
    # ===================== DEPRECATED (Replaced by OAuth 2.0) =====================
    # These are maintained for backwards compatibility but should not be used
    FACEBOOK_ACCESS_TOKEN: str = os.getenv("FACEBOOK_ACCESS_TOKEN", "")  # Deprecated
    LINKEDIN_ACCESS_TOKEN: str = os.getenv("LINKEDIN_ACCESS_TOKEN", "")  # Deprecated
    INSTAGRAM_USERNAME: str = os.getenv("INSTAGRAM_USERNAME", "")  # Deprecated
    INSTAGRAM_PASSWORD: str = os.getenv("INSTAGRAM_PASSWORD", "")  # Deprecated
    
    class Config:
        env_file = ".env"

settings = Settings()
