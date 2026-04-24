"""
OAuth 2.0 Authentication Routes
Handles OAuth flow for Facebook, LinkedIn, and JWT token management
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import RedirectResponse
import auth
from config import settings

router = APIRouter(prefix="/api/auth", tags=["authentication"])

# ===================== JWT TOKEN ENDPOINTS =====================

@router.post("/tokens/refresh")
async def refresh_token(refresh_token: str):
    """
    Refresh access token using refresh token
    POST /api/auth/tokens/refresh?refresh_token=<token>
    """
    new_token = auth.refresh_access_token(refresh_token)
    if not new_token:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    return {
        "success": True,
        "access_token": new_token,
        "token_type": "bearer"
    }

@router.post("/tokens/verify")
async def verify_token(token: str):
    """
    Verify JWT token validity
    POST /api/auth/tokens/verify?token=<token>
    """
    payload = auth.verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return {
        "success": True,
        "valid": True,
        "payload": payload
    }

# ===================== FACEBOOK OAUTH 2.0 =====================

@router.get("/facebook/authorize")
async def facebook_authorize(state: str = ""):
    """
    Redirect user to Facebook OAuth login
    GET /api/auth/facebook/authorize
    """
    auth_url = auth.get_facebook_auth_url(state)
    return {"success": True, "auth_url": auth_url}

@router.get("/facebook/callback")
async def facebook_callback(code: str = Query(None), state: str = Query(None), error: str = Query(None)):
    """
    Handle Facebook OAuth callback
    GET /api/auth/facebook/callback?code=<code>&state=<state>
    """
    if error:
        raise HTTPException(status_code=400, detail=f"Facebook auth error: {error}")
    
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code not provided")
    
    token_data = auth.exchange_facebook_code(code)
    if not token_data:
        raise HTTPException(status_code=400, detail="Failed to exchange authorization code")
    
    # Create JWT tokens
    access_token = auth.create_access_token({"type": "facebook", "platform": "facebook"})
    refresh_token = auth.create_refresh_token({"type": "facebook", "platform": "facebook"})
    
    return {
        "success": True,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "facebook_data": {
            "access_token": token_data.get('access_token'),
            "token_type": token_data.get('token_type'),
            "expires_in": token_data.get('expires_in')
        }
    }

# ===================== LINKEDIN OAUTH 2.0 =====================

@router.get("/linkedin/authorize")
async def linkedin_authorize(state: str = ""):
    """
    Redirect user to LinkedIn OAuth login
    GET /api/auth/linkedin/authorize
    """
    auth_url = auth.get_linkedin_auth_url(state)
    return {"success": True, "auth_url": auth_url}

@router.get("/linkedin/callback")
async def linkedin_callback(code: str = Query(None), state: str = Query(None), error: str = Query(None)):
    """
    Handle LinkedIn OAuth callback
    GET /api/auth/linkedin/callback?code=<code>&state=<state>
    """
    if error:
        raise HTTPException(status_code=400, detail=f"LinkedIn auth error: {error}")
    
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code not provided")
    
    token_data = auth.exchange_linkedin_code(code)
    if not token_data:
        raise HTTPException(status_code=400, detail="Failed to exchange authorization code")
    
    # Create JWT tokens
    access_token = auth.create_access_token({"type": "linkedin", "platform": "linkedin"})
    refresh_token = auth.create_refresh_token({"type": "linkedin", "platform": "linkedin"})
    
    return {
        "success": True,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "linkedin_data": {
            "access_token": token_data.get('access_token'),
            "expires_in": token_data.get('expires_in')
        }
    }

# ===================== CREDENTIALS STATUS =====================

@router.get("/status/facebook")
async def facebook_status():
    """
    Check Facebook OAuth status
    GET /api/auth/status/facebook
    """
    token = auth.get_facebook_access_token()
    return {
        "platform": "facebook",
        "authenticated": token is not None,
        "has_token": token is not None,
        "page_id": settings.FACEBOOK_PAGE_ID or None,
        "instagram_account": settings.INSTAGRAM_BUSINESS_ACCOUNT_ID or None
    }

@router.get("/status/linkedin")
async def linkedin_status():
    """
    Check LinkedIn OAuth status
    GET /api/auth/status/linkedin
    """
    token = auth.get_linkedin_access_token()
    return {
        "platform": "linkedin",
        "authenticated": token is not None,
        "has_token": token is not None,
        "person_urn": settings.LINKEDIN_PERSON_URN or None,
        "org_urn": settings.LINKEDIN_ORG_URN or None
    }

# ===================== TOKEN REVOCATION =====================

@router.post("/revoke/facebook")
async def revoke_facebook():
    """
    Revoke Facebook token
    POST /api/auth/revoke/facebook
    """
    try:
        import os
        if os.path.exists(settings.FACEBOOK_ACCESS_TOKEN_PATH):
            os.remove(settings.FACEBOOK_ACCESS_TOKEN_PATH)
        return {"success": True, "message": "Facebook token revoked"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Revocation failed: {e}")

@router.post("/revoke/linkedin")
async def revoke_linkedin():
    """
    Revoke LinkedIn token
    POST /api/auth/revoke/linkedin
    """
    try:
        import os
        if os.path.exists(settings.LINKEDIN_ACCESS_TOKEN_PATH):
            os.remove(settings.LINKEDIN_ACCESS_TOKEN_PATH)
        return {"success": True, "message": "LinkedIn token revoked"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Revocation failed: {e}")

