# 🔐 OAuth 2.0 Comprehensive Setup Guide

AutoPost AI now supports **complete OAuth 2.0 authentication** for all social media platforms and backend API security. This guide covers setting up OAuth 2.0 for Facebook, LinkedIn, Gmail, and JWT Bearer tokens for API authentication.

## 📋 Table of Contents

1. [Overview](#overview)
2. [Facebook OAuth 2.0](#facebook-oauth-20)
3. [LinkedIn OAuth 2.0](#linkedin-oauth-20)
4. [Gmail OAuth 2.0](#gmail-oauth-20)
5. [JWT/Bearer Token Authentication](#jwtbearer-token-authentication)
6. [Frontend Integration](#frontend-integration)
7. [API Endpoints Reference](#api-endpoints-reference)
8. [Troubleshooting](#troubleshooting)
9. [Security Best Practices](#security-best-practices)

---

## Overview

### OAuth 2.0 Benefits

| Feature | OAuth 2.0 | Previous (API Keys) |
|---------|----------|-------------------|
| **Security** | ✅ High - No passwords stored | ⚠️ Medium - Keys in config |
| **User Control** | ✅ Easy revocation | ❌ Manual token management |
| **Token Expiry** | ✅ Automatic refresh | ❌ No expiration |
| **Industry Standard** | ✅ Yes | ❌ Custom approach |
| **Future-proof** | ✅ Scalable | ❌ Limited |

### Supported Platforms

- ✅ **Facebook** - OAuth 2.0 authorization code flow
- ✅ **LinkedIn** - OAuth 2.0 authorization code flow
- ✅ **Gmail** - OAuth 2.0 with InstalledAppFlow
- ✅ **Backend API** - JWT Bearer token authentication

---

## Facebook OAuth 2.0

### Step 1: Create Facebook App

1. Go to [Facebook Developers](https://developers.facebook.com)
2. Click "My Apps" → "Create App"
3. Select "Consumer" as app type
4. Fill in app details:
   - **App Name**: AutoPost AI
   - **App Contact Email**: your_email@example.com
   - **Agree to terms** → Create App

### Step 2: Enable Facebook Login & Permissions

1. From your app dashboard, add products:
   - Search for "Facebook Login"
   - Click "Set Up"
2. Configure OAuth Redirect URIs:
   - Go to Settings → Basic
   - Copy **App ID** (FACEBOOK_CLIENT_ID)
   - Copy **App Secret** (FACEBOOK_CLIENT_SECRET)

### Step 3: Add Instagram Graph API

1. In app dashboard, add product: "Instagram Graph API"
2. Go to Roles → Testers
3. Add your Instagram Business Account
4. Accept invitation to access page

### Step 4: Configure in AutoPost AI

1. Update `backend/.env`:
```bash
FACEBOOK_CLIENT_ID=your_facebook_app_id_here
FACEBOOK_CLIENT_SECRET=your_facebook_app_secret_here
FACEBOOK_PAGE_ID=your_facebook_page_id
INSTAGRAM_BUSINESS_ACCOUNT_ID=your_instagram_business_account_id
FACEBOOK_OAUTH_REDIRECT=http://localhost:8000/api/auth/facebook/callback
```

2. First time authorization:
```bash
# Call this endpoint in browser or frontend
GET http://localhost:8000/api/auth/facebook/authorize

# Browser will redirect to Facebook login
# After authorization, you'll be redirected to callback with code
# Token will be saved to backend/facebook_token.json
```

### Step 5: Test Facebook Integration

```javascript
// From frontend
fetch('http://localhost:8000/api/auth/facebook/authorize')
  .then(r => r.json())
  .then(data => window.location.href = data.auth_url)
```

---

## LinkedIn OAuth 2.0

### Step 1: Create LinkedIn App

1. Go to [LinkedIn Developers](https://www.linkedin.com/developers/apps)
2. Click "Create app"
3. Fill in:
   - **App name**: AutoPost AI
   - **LinkedIn Page**: Choose or create
   - **App logo**: Upload image
   - **Legal agreement**: Accept
4. Create app

### Step 2: Get Credentials

1. Go to app "Auth" tab
2. Copy **Client ID** (LINKEDIN_CLIENT_ID)
3. Copy **Client Secret** (LINKEDIN_CLIENT_SECRET)
4. Under "Authorized redirect URLs", add:
   ```
   http://localhost:8000/api/auth/linkedin/callback
   ```
5. Request access to:
   - Sign In with LinkedIn
   - Share on LinkedIn

### Step 3: Get Your LinkedIn Person URN

```bash
# Make LinkedIn API call to get your person URN
curl -X GET https://api.linkedin.com/v2/me \
  -H "Authorization: Bearer {access_token}"

# Response will include your person URN
# Example: urn:li:person:AbcDeFgHiJ
```

### Step 4: Configure in AutoPost AI

1. Update `backend/.env`:
```bash
LINKEDIN_CLIENT_ID=your_linkedin_app_id
LINKEDIN_CLIENT_SECRET=your_linkedin_app_secret
LINKEDIN_PERSON_URN=urn:li:person:your_person_id
LINKEDIN_OAUTH_REDIRECT=http://localhost:8000/api/auth/linkedin/callback
```

2. First time authorization:
```bash
GET http://localhost:8000/api/auth/linkedin/authorize
```

---

## Gmail OAuth 2.0

Gmail OAuth 2.0 setup is covered in **GMAIL_SETUP.md**. Key points:

1. Enable Gmail API in Google Cloud
2. Create OAuth 2.0 credentials (Desktop app)
3. Download and save to `backend/gmail_credentials.json`
4. First email triggers browser auth
5. Token saved to `backend/gmail_token.pickle`

See `GMAIL_SETUP.md` for detailed instructions.

---

## JWT/Bearer Token Authentication

### Overview

AutoPost AI backend uses JWT (JSON Web Tokens) for API authentication. All authenticated endpoints require a Bearer token.

### Token Types

#### Access Token
- **Lifetime**: 24 hours (configurable)
- **Use**: Authenticate API requests
- **Header**: `Authorization: Bearer {access_token}`

#### Refresh Token
- **Lifetime**: 30 days (configurable)
- **Use**: Get new access token when expired
- **Endpoint**: `POST /api/auth/tokens/refresh`

### JWT Configuration

In `backend/.env`:
```bash
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
JWT_REFRESH_EXPIRATION_DAYS=30
```

⚠️ **IMPORTANT**: Change `JWT_SECRET_KEY` in production!

### OAuth Token Exchange

When user completes OAuth (Facebook/LinkedIn):

```json
{
  "success": true,
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "facebook_data": {
    "access_token": "facebook_access_token",
    "expires_in": 5183944
  }
}
```

### Using Bearer Token

```javascript
// Add to all API requests
fetch('http://localhost:8000/api/posts', {
  headers: {
    'Authorization': `Bearer ${access_token}`
  }
})
```

### Refresh Token Flow

```javascript
// When access token expires
fetch('http://localhost:8000/api/auth/tokens/refresh?refresh_token=' + refresh_token, {
  method: 'POST'
})
.then(r => r.json())
.then(data => {
  // Update access token
  localStorage.setItem('access_token', data.access_token)
})
```

---

## Frontend Integration

### React Example

```javascript
// frontend/src/pages/Settings.jsx

import { useState } from 'react'

export function OAuthSettings() {
  const [tokens, setTokens] = useState({
    facebook: null,
    linkedin: null,
    gmail: null
  })

  const handleFacebookAuth = async () => {
    const response = await fetch('http://localhost:8000/api/auth/facebook/authorize')
    const data = await response.json()
    window.location.href = data.auth_url
  }

  const handleLinkedInAuth = async () => {
    const response = await fetch('http://localhost:8000/api/auth/linkedin/authorize')
    const data = await response.json()
    window.location.href = data.auth_url
  }

  const checkStatus = async () => {
    const facebook = await fetch('http://localhost:8000/api/auth/status/facebook')
      .then(r => r.json())
    const linkedin = await fetch('http://localhost:8000/api/auth/status/linkedin')
      .then(r => r.json())
    
    console.log('Facebook authenticated:', facebook.authenticated)
    console.log('LinkedIn authenticated:', linkedin.authenticated)
  }

  return (
    <div className="settings">
      <h1>OAuth 2.0 Settings</h1>
      
      <button onClick={handleFacebookAuth}>Connect Facebook</button>
      <button onClick={handleLinkedInAuth}>Connect LinkedIn</button>
      <button onClick={checkStatus}>Check Status</button>
    </div>
  )
}
```

### Frontend API Wrapper

```javascript
// frontend/src/api.js

const API_BASE = 'http://localhost:8000'

// Store tokens in localStorage
let accessToken = localStorage.getItem('access_token')
let refreshToken = localStorage.getItem('refresh_token')

export async function apiCall(endpoint, options = {}) {
  // Add Bearer token to all requests
  if (accessToken) {
    options.headers = {
      ...options.headers,
      'Authorization': `Bearer ${accessToken}`
    }
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers
    },
    ...options
  })

  // If token expired (401), refresh it
  if (response.status === 401 && refreshToken) {
    const newTokenResponse = await fetch(
      `${API_BASE}/api/auth/tokens/refresh?refresh_token=${refreshToken}`,
      { method: 'POST' }
    )
    const data = await newTokenResponse.json()
    
    if (data.access_token) {
      accessToken = data.access_token
      localStorage.setItem('access_token', accessToken)
      
      // Retry original request with new token
      return apiCall(endpoint, options)
    }
  }

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`)
  }

  return await response.json()
}
```

---

## API Endpoints Reference

### Authentication

#### Facebook OAuth

```
GET /api/auth/facebook/authorize
- Returns: { auth_url: "https://www.facebook.com/v18.0/dialog/oauth?..." }

GET /api/auth/facebook/callback?code=CODE&state=STATE
- Handles OAuth callback
- Returns: { access_token, refresh_token, facebook_data }

GET /api/auth/status/facebook
- Returns: { authenticated: bool, has_token: bool, page_id, instagram_account }

POST /api/auth/revoke/facebook
- Revokes and deletes Facebook token
```

#### LinkedIn OAuth

```
GET /api/auth/linkedin/authorize
- Returns: { auth_url: "https://www.linkedin.com/oauth/v2/authorization?..." }

GET /api/auth/linkedin/callback?code=CODE&state=STATE
- Handles OAuth callback
- Returns: { access_token, refresh_token, linkedin_data }

GET /api/auth/status/linkedin
- Returns: { authenticated: bool, has_token: bool, person_urn, org_urn }

POST /api/auth/revoke/linkedin
- Revokes and deletes LinkedIn token
```

#### JWT Tokens

```
POST /api/auth/tokens/refresh?refresh_token=TOKEN
- Refreshes access token
- Returns: { access_token, token_type: "bearer" }

POST /api/auth/tokens/verify?token=TOKEN
- Verifies token validity
- Returns: { valid: bool, payload: {...} }
```

---

## Troubleshooting

### "Client ID or Secret missing"

**Problem**: OAuth endpoints return error about missing credentials

**Solution**:
1. Check `.env` file has all required variables
2. Restart backend: `python -m uvicorn main:app --reload`
3. Verify credentials from Facebook/LinkedIn developer console

### "Redirect URI mismatch"

**Problem**: OAuth authorization fails with redirect URI error

**Solution**:
1. Go to Facebook/LinkedIn developer settings
2. Verify "Authorized redirect URIs" exactly match:
   - Facebook: `http://localhost:8000/api/auth/facebook/callback`
   - LinkedIn: `http://localhost:8000/api/auth/linkedin/callback`
3. Include protocol (`http://`) and exact path

### "Token expired" when posting

**Problem**: Post fails with token expiry error

**Solution**:
1. Delete token file (facebook_token.json or linkedin_token.json)
2. Re-authorize via OAuth flow
3. Or implement token refresh logic in posting code

### "CSRF state mismatch"

**Problem**: OAuth callback fails with state validation error

**Solution**:
1. Ensure cookies are enabled
2. Don't modify URL state parameter
3. Clear browser cache and retry

---

## Security Best Practices

### ✅ DO

- ✅ Use HTTPS in production (not just HTTP)
- ✅ Store JWT_SECRET_KEY securely (use environment variable)
- ✅ Rotate JWT_SECRET_KEY periodically
- ✅ Use refresh token rotation (refresh token expires after use)
- ✅ Validate tokens before accessing protected resources
- ✅ Log authentication events for audit trail
- ✅ Revoke tokens when user logs out

### ❌ DON'T

- ❌ Hardcode secrets in code
- ❌ Commit .env file to git
- ❌ Use same JWT_SECRET_KEY across environments
- ❌ Store passwords anywhere
- ❌ Share OAuth credentials
- ❌ Use weak JWT_SECRET_KEY
- ❌ Skip token validation on backend

### Environment Variables

```bash
# .env (development only)
JWT_SECRET_KEY=your-dev-secret-key

# Production (use strong, random key)
JWT_SECRET_KEY=$(openssl rand -hex 32)  # Generate secure key
```

### Token Expiration Strategy

```python
# Recommended settings
JWT_EXPIRATION_HOURS = 1      # Access token: 1 hour
JWT_REFRESH_EXPIRATION_DAYS = 30  # Refresh token: 30 days
```

This forces users to refresh frequently, preventing long-term token compromise.

---

## Migration from API Keys

### Before (Deprecated)

```bash
# Old way - credentials in config
FACEBOOK_ACCESS_TOKEN=eABC123...
LINKEDIN_ACCESS_TOKEN=AQFfGH123...
```

### After (OAuth 2.0)

```bash
# New way - OAuth client credentials
FACEBOOK_CLIENT_ID=123456789
FACEBOOK_CLIENT_SECRET=abc123def456
LINKEDIN_CLIENT_ID=123456789
LINKEDIN_CLIENT_SECRET=abc123def456
```

### Update Checklist

- [ ] Update `.env` with OAuth credentials
- [ ] Delete old access token entries
- [ ] Update `config.py` with new OAuth settings
- [ ] Test OAuth authorization flow
- [ ] Update frontend to use Bearer tokens
- [ ] Verify posting still works
- [ ] Delete old token files

---

## Support & Further Resources

### Documentation

- [Facebook OAuth 2.0](https://developers.facebook.com/docs/facebook-login/web)
- [LinkedIn OAuth 2.0](https://docs.microsoft.com/en-us/linkedin/shared/authentication/authentication)
- [Gmail OAuth 2.0](GMAIL_SETUP.md)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8949)

### Useful Tools

- [JWT Decoder](https://jwt.io) - Decode and inspect JWT tokens
- [OAuth 2.0 Playground](https://www.oauth.com/playground/) - Test OAuth flows
- [Postman](https://www.postman.com) - API testing tool

---

**Last Updated**: April 24, 2026  
**Version**: AutoPost AI v3.0  
**Status**: ✅ Production Ready

