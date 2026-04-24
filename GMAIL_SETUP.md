# 📧 Gmail Integration Guide

## Overview

AutoPost AI now supports sending emails directly through the AI Agent! The agent can understand natural language commands like:

- "Send an email to john@example.com about this"
- "Mail this to my manager with a professional tone"
- "Email to client@company.com - schedule it for tomorrow"

## Setup Instructions

### Step 1: Enable Gmail

Add these to your `backend/.env` file:

```env
GMAIL_FROM_EMAIL=your_gmail_address@gmail.com
GMAIL_APP_PASSWORD=your_app_password_here
```

### Step 2: Generate Gmail App Password

1. Go to: https://myaccount.google.com/apppasswords
2. Select "Mail" and "Windows Computer" (or your device)
3. Google will generate a 16-character app password
4. Copy this password to `GMAIL_APP_PASSWORD` in `.env`

⚠️ **Important**: Use the App Password, NOT your regular Gmail password!

### Step 3: Verify Configuration

Test by checking if the backend starts without errors:

```bash
cd backend
source venv/bin/activate
python -c "from config import settings; print(f'Gmail: {settings.GMAIL_FROM_EMAIL}')"
```

---

## Features

### 1. AI Agent Email Commands

Chat with the agent to send emails:

```
User: "Send an email to john@example.com about this image"
Agent: "I'll help! What tone would you like? (professional, casual, funny, inspirational)"
User: "professional"
Agent: "Perfect! I'll generate a professional email. Ready to send?"
```

### 2. Auto-Generated Email Content

The agent uses Gemini AI to:
- Generate subject lines
- Create email body content
- Optimize tone and messaging
- Optional image attachments

### 3. Email Endpoints

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
  "message_id": "gmail_1234567890",
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
User: "Send email to team@startup.io with custom subject: Quarterly Update"
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

### "Gmail authentication failed"
- Check that `GMAIL_APP_PASSWORD` is correct (16 characters)
- Use App Password, NOT regular Gmail password
- Regenerate password if needed: https://myaccount.google.com/apppasswords

### "Gmail not configured"
- Verify `GMAIL_FROM_EMAIL` is set in `.env`
- Check `GMAIL_APP_PASSWORD` exists
- Restart backend after adding credentials

### Email not sending
- Verify credentials are correct
- Check recipient email is valid
- Look for error message in logs
- Try with a different recipient to isolate issue

### "No image uploaded"
- For email with attachment: Upload image first, then send
- For email without image: System will send plain email

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

## Security Best Practices

✅ **DO:**
- Use App Password (not regular Gmail password)
- Store credentials in `.env` (not in code)
- Validate recipient email before sending
- Log all email sends for audit trail

❌ **DON'T:**
- Commit `.env` to git (it's in `.gitignore`)
- Share Gmail credentials
- Send sensitive data via unencrypted email
- Use regular Gmail password for app

---

## Support

For issues with Gmail integration:
1. Check `.env` file configuration
2. Review error messages in backend logs
3. Verify Gmail App Password is correct
4. Check recipient email format
5. See Troubleshooting section above

---

**Gmail integration is now part of AutoPost AI's AI Agent!** 🚀

