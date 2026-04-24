# 📧 Gmail Integration Guide (OAuth 2.0)

## Overview

AutoPost AI now supports sending emails through the AI Agent using **OAuth 2.0 authentication**. The agent can understand natural language commands like:

- "Send an email to john@example.com about this"
- "Mail this to my manager with a professional tone"
- "Email to client@company.com - with subject line"

## Setup Instructions

### Step 1: Create Google Cloud Project

1. Go to: https://console.cloud.google.com/
2. Click "Create Project" and name it "AutoPost AI"
3. Wait for project to be created

### Step 2: Enable Gmail API

1. In Google Cloud Console, search for "Gmail API"
2. Click on "Gmail API"
3. Click "ENABLE"
4. Go to "Credentials" (left sidebar)
5. Click "Create Credentials" → "OAuth 2.0 Client ID"
6. Choose "Desktop application"
7. Download the JSON file (this is your credentials file)

### Step 3: Add Credentials to Project

1. Download the credentials JSON file from Google Cloud Console
2. Save it to: `backend/gmail_credentials.json`
3. Add to `backend/.env`:
   ```env
   GMAIL_FROM_EMAIL=your_gmail@gmail.com
   GMAIL_CREDENTIALS_PATH=gmail_credentials.json
   GMAIL_TOKEN_PATH=gmail_token.pickle
   ```

### Step 4: First-Time Authentication

1. Run backend for the first time with Gmail configured:
   ```bash
   cd backend
   source venv/bin/activate
   pip install -r requirements.txt
   python -m uvicorn main:app --reload
   ```

2. When you send the first email, a browser window will open
3. Sign in with your Gmail account
4. Grant permissions to AutoPost AI
5. The token will be saved to `gmail_token.pickle`
6. Future emails will use this token (no interaction needed)

---

## Features

### 1. AI Agent Email Commands

Chat with the agent to send emails:

```
User: "Send email to john@example.com about this image"
Agent: "I'll help! What tone would you like? (professional, casual, funny, inspirational)"
User: "professional"
Agent: "Perfect! I'll generate a professional email. Ready to send?"
```

### 2. OAuth 2.0 Security

✅ **Secure**: User grants permission explicitly
✅ **No passwords stored**: Uses OAuth tokens instead
✅ **Revokable**: User can revoke access anytime
✅ **Scoped**: Only has permission to send emails (not read/delete)

### 3. Auto-Generated Email Content

The agent uses Gemini AI to:
- Generate subject lines
- Create email body content
- Optimize tone and messaging
- Optional image attachments

### 4. Email Endpoints

**Send Email via Agent:**
```bash
POST /api/agent/send-email
Content-Type: multipart/form-data

recipient_email: john@example.com
subject: "Project Update"  # Optional - AI generates if empty
custom_body: "..."  # Optional - AI generates if empty
```

**Example Response:**
```json
{
  "success": true,
  "message_id": "18f9e8c7e4c5a2b1d9",
  "recipient": "john@example.com",
  "subject": "Check out this amazing content!",
  "message": "✅ Email sent successfully to john@example.com!"
}
```

---

## AI Agent Workflow

### For Email Actions:

1. **User says**: "Send email to jane@company.com"
   - Agent detects email action
   - Agent asks for image (if not uploaded yet)

2. **User uploads image**
   - Agent analyzes image
   - Asks for tone preference

3. **User specifies tone**: "professional"
   - Agent prepares email
   - Generates subject and body content

4. **Agent sends confirmation**
   - Shows email content preview
   - Awaits approval

5. **Email sent**
   - Agent records in database
   - Returns confirmation

---

## Natural Language Examples

### Example 1: Simple Email
```
User: "Email this to support@company.com"
Agent: "What tone? (professional/casual/funny/inspirational)"
User: "professional"
Agent: "✅ Email sent!"
```

### Example 2: Custom Message
```
User: "Send email to team@startup.io with subject: Quarterly Update"
Agent: Uses provided subject, generates body
Result: "✅ Email sent to team@startup.io"
```

### Example 3: With Specific Tone
```
User: "Mail this to clients with a funny tone"
Agent: Detects funny tone, generates humorous subject + body
Result: "✅ Email sent with funny tone!"
```

---

## Troubleshooting

### "Credentials file not found"
- Ensure `gmail_credentials.json` is in `backend/` directory
- Check file path in `.env`: `GMAIL_CREDENTIALS_PATH=gmail_credentials.json`

### "OAuth window didn't open"
- First email requires browser interaction
- Look for console message with authentication URL
- Visit URL manually if popup doesn't appear

### "Invalid grant - token expired"
- Delete `gmail_token.pickle` to reset
- Next email will prompt for re-authentication

### "Gmail API not enabled"
- Go to https://console.cloud.google.com/apis/library
- Search "Gmail API"
- Click "ENABLE" if not already enabled

### Email not sending after authentication
- Verify recipient email is valid
- Check console for error messages
- Ensure Gmail account has capacity to send

---

## Advanced Features

### 1. Email with Image Attachment
```bash
# Upload image first
POST /api/agent/upload
multipart/form-data: file

# Then send email (image auto-attached)
POST /api/agent/send-email
recipient_email: john@example.com
```

### 2. Custom Email Templates
You can provide custom subject/body:
```bash
POST /api/agent/send-email
recipient_email: jane@company.com
subject: "Custom Subject Line"
custom_body: "Custom HTML body content"
```

### 3. Email Records
All sent emails are stored in the database with:
- Recipient email
- Subject line
- Body content
- Timestamp
- Image attachment info

### 4. Revoking Access

If you want to revoke access:
1. Go to: https://myaccount.google.com/permissions
2. Find "AutoPost AI"
3. Click "Remove access"
4. Delete `gmail_token.pickle`
5. Next email will require re-authentication

---

## Security Best Practices

✅ **DO:**
- Store credentials JSON securely
- Add `.env` and `*.pickle` to `.gitignore` (already done)
- Use limited OAuth scopes (only send emails)
- Delete token file if you switch Gmail accounts
- Review permissions regularly

❌ **DON'T:**
- Share credentials JSON file
- Commit `.env` to git
- Use app passwords (use OAuth instead)
- Store tokens in public locations
- Share token files

---

## Environment Variables

```env
# Gmail Configuration
GMAIL_FROM_EMAIL=your_gmail@gmail.com
GMAIL_CREDENTIALS_PATH=gmail_credentials.json
GMAIL_TOKEN_PATH=gmail_token.pickle
```

### What Each Variable Means:

| Variable | Purpose | Example |
|----------|---------|---------|
| `GMAIL_FROM_EMAIL` | Email to send from | user@gmail.com |
| `GMAIL_CREDENTIALS_PATH` | Location of OAuth credentials | gmail_credentials.json |
| `GMAIL_TOKEN_PATH` | Location to save refresh token | gmail_token.pickle |

---

## API Reference

### Chat with Agent (Detect Email Intent)
```bash
POST /api/agent/chat
{
  "message": "Send email to john@example.com about this"
}
```

### Send Email
```bash
POST /api/agent/send-email
Content-Type: multipart/form-data

recipient_email=john@example.com
subject=optional_subject
custom_body=optional_body
```

### Upload Image (For Email Attachment)
```bash
POST /api/agent/upload
Content-Type: multipart/form-data

file=<image_file>
```

---

## Support

For issues with Gmail integration:
1. Check `.env` configuration
2. Verify OAuth credentials file exists
3. Check browser console for auth URL if popup doesn't open
4. Review error messages in backend logs
5. See Troubleshooting section above

---

## Files Reference

- `backend/social_apis.py` - Gmail OAuth 2.0 implementation
- `backend/routes/agent.py` - Email endpoint
- `backend/.env` - Configuration (not committed)
- `backend/gmail_credentials.json` - OAuth credentials (not committed)
- `backend/gmail_token.pickle` - Refresh token (not committed, auto-generated)

---

**Gmail OAuth 2.0 is now integrated into AutoPost AI's AI Agent!** 🚀



