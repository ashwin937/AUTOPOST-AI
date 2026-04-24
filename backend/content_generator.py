import google.generativeai as genai
from config import settings
import json

if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-pro")
else:
    model = None

def generate_platform_content(image_description: str, platforms: list, tone: str = "professional"):
    """
    Generate platform-specific content using Google Gemini
    """
    if not model:
        return get_mock_content(platforms, tone)
    
    platform_prompt = {
        "instagram": "Create an engaging Instagram caption with relevant hashtags. Max 2200 characters. Focus on visual storytelling.",
        "facebook": "Create a Facebook post that encourages engagement. Include relevant hashtags and call-to-action. Max 500 characters.",
        "linkedin": "Create a professional LinkedIn post that provides value and encourages discussion. Max 500 characters. Tone: professional.",
        "gmail": "Create an email subject line and body for sending this image to contacts. Subject should be max 60 chars. Body should be max 500 chars."
    }
    
    prompt = f"""Based on this image description: "{image_description}"

Generate unique, engaging content for these platforms: {', '.join(platforms)}
Tone: {tone}

For each platform, generate the content following these guidelines:
{json.dumps(platform_prompt, indent=2)}

Return a JSON object with keys: instagram_caption, facebook_text, linkedin_text, gmail_subject, gmail_body
Only include keys for the requested platforms.
Make content platform-native and authentic to each channel."""
    
    try:
        response = model.generate_content(prompt)
        content = response.text
        # Parse JSON from response
        import re
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except Exception as e:
        print(f"Gemini API error: {e}")
    
    return get_mock_content(platforms, tone)

def get_mock_content(platforms: list, tone: str = "professional"):
    """Mock content generation for testing"""
    mock_data = {
        "instagram_caption": f"📸 Amazing content! ✨ Check this out! #explore #instagood #content {'#professional' if tone == 'professional' else '#casual'} 🎯",
        "facebook_text": "👍 Don't miss this! Share with your network. Like and comment below! 📱",
        "linkedin_text": "💼 Professional insights on display. Let's connect and discuss! 🚀 #LinkedIn #Professional #Growth",
        "gmail_subject": f"Check This Out - {tone.title()} Content",
        "gmail_body": f"""Hi there,

I wanted to share this with you!

This is a professional piece of content that I think you'd appreciate.

Best regards,
Your Name"""
    }
    
    result = {}
    for platform in platforms:
        if platform == "instagram" and "instagram_caption" in mock_data:
            result["instagram_caption"] = mock_data["instagram_caption"]
        elif platform == "facebook" and "facebook_text" in mock_data:
            result["facebook_text"] = mock_data["facebook_text"]
        elif platform == "linkedin" and "linkedin_text" in mock_data:
            result["linkedin_text"] = mock_data["linkedin_text"]
        elif platform == "gmail" and "gmail_subject" in mock_data:
            result["gmail_subject"] = mock_data["gmail_subject"]
            result["gmail_body"] = mock_data["gmail_body"]
    
    return result
