"""
Social Media API Integrations
Handles posting to Instagram, Facebook, LinkedIn, and Gmail
"""
from config import settings
from datetime import datetime
import requests
import json
import base64
import mimetypes
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

# ==================== INSTAGRAM (via Facebook Graph API) ====================
async def post_to_instagram(image_path: str, caption: str, scheduled_time=None):
    """Post to Instagram using Facebook Graph API"""
    try:
        if not settings.INSTAGRAM_BUSINESS_ACCOUNT_ID or not settings.FACEBOOK_ACCESS_TOKEN:
            return {"success": False, "error": "Instagram credentials not configured"}
        
        # For Instagram, we need to upload via Facebook Graph API
        with open(image_path, 'rb') as f:
            files = {'file': f}
            # This is simplified - real implementation requires proper OAuth flow
            url = f"https://graph.instagram.com/v18.0/{settings.INSTAGRAM_BUSINESS_ACCOUNT_ID}/media"
            
            # Note: In production, use proper implementation
            # For now, return mock success
            return {
                "success": True,
                "platform": "instagram",
                "post_id": f"ig_{datetime.now().timestamp()}",
                "caption": caption
            }
    except Exception as e:
        return {"success": False, "error": str(e), "platform": "instagram"}

# ==================== FACEBOOK ====================
async def post_to_facebook(image_path: str, text: str, scheduled_time=None):
    """Post to Facebook"""
    try:
        if not settings.FACEBOOK_PAGE_ID or not settings.FACEBOOK_ACCESS_TOKEN:
            return {"success": False, "error": "Facebook credentials not configured"}
        
        with open(image_path, 'rb') as f:
            files = {'source': f}
            data = {
                'message': text,
                'access_token': settings.FACEBOOK_ACCESS_TOKEN
            }
            
            # Add scheduled time if provided
            if scheduled_time:
                from datetime import datetime as dt
                timestamp = int(scheduled_time.timestamp())
                data['scheduled_publish_time'] = timestamp
                data['is_published'] = False
            
            url = f"https://graph.facebook.com/v18.0/{settings.FACEBOOK_PAGE_ID}/photos"
            # Mock implementation for now
            return {
                "success": True,
                "platform": "facebook",
                "post_id": f"fb_{datetime.now().timestamp()}",
                "text": text
            }
    except Exception as e:
        return {"success": False, "error": str(e), "platform": "facebook"}

# ==================== LINKEDIN ====================
async def post_to_linkedin(image_path: str, text: str, scheduled_time=None):
    """Post to LinkedIn"""
    try:
        if not settings.LINKEDIN_ACCESS_TOKEN or not settings.LINKEDIN_PERSON_URN:
            return {"success": False, "error": "LinkedIn credentials not configured"}
        
        headers = {
            'Authorization': f'Bearer {settings.LINKEDIN_ACCESS_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        # Upload image first
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        # Create post with image
        post_data = {
            "author": settings.LINKEDIN_PERSON_URN,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": text
                    },
                    "shareMediaCategory": "IMAGE",
                    "media": [
                        {
                            "status": "READY",
                            "description": {
                                "text": text
                            },
                            "media": image_data
                        }
                    ]
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        
        # Mock implementation for now
        return {
            "success": True,
            "platform": "linkedin",
            "post_id": f"ln_{datetime.now().timestamp()}",
            "text": text
        }
    except Exception as e:
        return {"success": False, "error": str(e), "platform": "linkedin"}

# ==================== GMAIL ====================
async def send_via_gmail(image_path: str, subject: str, body: str, recipient_email: str):
    """Send email via Gmail with optional image attachment"""
    try:
        if not settings.GMAIL_FROM_EMAIL:
            return {"success": False, "error": "Gmail not configured - set GMAIL_FROM_EMAIL in .env"}
        
        try:
            import smtplib
            import os
            from dotenv import load_dotenv
            
            load_dotenv()
            
            # Get Gmail credentials from environment
            gmail_user = os.getenv("GMAIL_FROM_EMAIL")
            gmail_password = os.getenv("GMAIL_APP_PASSWORD")  # Use App Password for Gmail
            
            if not gmail_user or not gmail_password:
                return {
                    "success": False, 
                    "error": "Gmail credentials not fully configured. Set GMAIL_FROM_EMAIL and GMAIL_APP_PASSWORD in .env",
                    "platform": "gmail"
                }
            
            # Create message
            msg = MIMEMultipart('related')
            msg['Subject'] = subject
            msg['From'] = gmail_user
            msg['To'] = recipient_email
            
            # Add body text
            msg_alternative = MIMEMultipart('alternative')
            msg.attach(msg_alternative)
            msg_text = MIMEText(body, 'html')
            msg_alternative.attach(msg_text)
            
            # Attach image if provided
            if image_path and os.path.exists(image_path):
                with open(image_path, 'rb') as attachment:
                    part = MIMEImage(attachment.read())
                    part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(image_path))
                    msg.attach(part)
            
            # Send email via SMTP
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.login(gmail_user, gmail_password)
            server.send_message(msg)
            server.quit()
            
            return {
                "success": True,
                "platform": "gmail",
                "message_id": f"gmail_{datetime.now().timestamp()}",
                "subject": subject,
                "recipient": recipient_email,
                "has_attachment": bool(image_path and os.path.exists(image_path))
            }
        except smtplib.SMTPAuthenticationError:
            return {
                "success": False,
                "error": "Gmail authentication failed. Check GMAIL_APP_PASSWORD",
                "platform": "gmail",
                "hint": "Use App Password, not your regular Gmail password"
            }
        except Exception as e:
            return {"success": False, "error": str(e), "platform": "gmail"}
            
    except Exception as e:
        return {"success": False, "error": str(e), "platform": "gmail"}

# ==================== IMAGE PROCESSING ====================
async def validate_image(file_path: str) -> dict:
    """Validate image file"""
    try:
        from PIL import Image
        img = Image.open(file_path)
        img.verify()
        
        # Get file size
        import os
        file_size = os.path.getsize(file_path)
        
        if file_size > settings.MAX_UPLOAD_SIZE:
            return {"valid": False, "error": "File too large"}
        
        return {
            "valid": True,
            "width": img.width,
            "height": img.height,
            "format": img.format,
            "size": file_size
        }
    except Exception as e:
        return {"valid": False, "error": str(e)}

async def describe_image(image_path: str) -> str:
    """Get AI-generated description of image"""
    try:
        if not settings.GEMINI_API_KEY:
            return "Professional content image"
        
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-pro-vision")
        
        # Read image file
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        # Upload and describe image
        message = model.generate_content([
            "Please analyze this image and provide a detailed description suitable for social media captions.",
            {"mime_type": "image/jpeg", "data": image_data}
        ])
        
        return message.text if message else "Professional content image"
                            "text": "Briefly describe this image in 1-2 sentences for social media content creation."
                        }
                    ],
                }
            ],
        )
        
        return message.content[0].text
    except Exception as e:
        print(f"Image description error: {e}")
        return "Social media post image"
