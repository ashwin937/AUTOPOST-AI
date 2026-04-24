"""
Agent API Routes
Handles chat-based posting agent interactions
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import SocialPost, get_db
from content_generator import generate_platform_content
from social_apis import post_to_instagram, post_to_facebook, post_to_linkedin, send_via_gmail, validate_image, describe_image
from agent import get_agent, reset_agent
from config import settings
import os
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/agent", tags=["agent"])

class ChatMessage(BaseModel):
    message: str

@router.post("/chat")
async def agent_chat(msg: ChatMessage):
    """
    Chat with the posting agent
    User sends a message like "Post this to Instagram" or "Schedule for later"
    Agent responds with guidance and next steps
    """
    try:
        agent = get_agent()
        result = agent.process_user_input(msg.message)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload")
async def agent_upload_image(file: UploadFile = File(...)):
    """
    Upload image for the agent to use
    Agent will then ask what to do with it
    """
    try:
        if file.content_type not in ["image/jpeg", "image/png", "image/gif", "image/webp"]:
            raise HTTPException(status_code=400, detail="Invalid image format")
        
        # Create uploads directory
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        
        # Save file
        file_id = str(uuid.uuid4())
        file_extension = file.filename.split('.')[-1]
        file_path = os.path.join(settings.UPLOAD_DIR, f"{file_id}.{file_extension}")
        
        # Write file
        content = await file.read()
        with open(file_path, 'wb') as f:
            f.write(content)
        
        # Validate image
        validation = await validate_image(file_path)
        if not validation["valid"]:
            os.remove(file_path)
            raise HTTPException(status_code=400, detail=validation["error"])
        
        # Get image description
        image_description = await describe_image(file_path)
        
        # Update agent context
        agent = get_agent()
        agent.set_image(file_path)
        
        return {
            "success": True,
            "file_id": file_id,
            "image_path": f"/uploads/{file_id}.{file_extension}",
            "description": image_description,
            "message": f"✅ Image uploaded! ({validation['width']}x{validation['height']}). Now tell me where to post it or how to schedule it."
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/post-now")
async def agent_post_now(db: Session = Depends(get_db)):
    """
    Execute immediate posting based on current agent context
    """
    try:
        agent = get_agent()
        context = agent.get_context()
        
        if not context["has_image"]:
            raise HTTPException(status_code=400, detail="No image uploaded")
        if not context["platforms"]:
            raise HTTPException(status_code=400, detail="No platforms selected")
        
        image_path = context["image_path"]
        
        # Get image description
        image_description = await describe_image(image_path)
        
        # Generate content
        generated_content = generate_platform_content(
            image_description,
            context["platforms"],
            context["tone"]
        )
        
        # Create database entry
        post_id = str(uuid.uuid4())
        db_post = SocialPost(
            id=post_id,
            image_path=image_path,
            original_description=image_description,
            instagram_caption=generated_content.get("instagram_caption"),
            facebook_text=generated_content.get("facebook_text"),
            linkedin_text=generated_content.get("linkedin_text"),
            gmail_subject=generated_content.get("gmail_subject"),
            gmail_body=generated_content.get("gmail_body"),
            status="posting",
            tone=context["tone"]
        )
        db.add(db_post)
        db.commit()
        db.refresh(db_post)
        
        # Post to platforms
        results = {}
        
        if "instagram" in context["platforms"] and generated_content.get("instagram_caption"):
            result = await post_to_instagram(image_path, generated_content["instagram_caption"])
            results["instagram"] = result
            if result["success"]:
                db_post.instagram_posted = True
                db_post.instagram_post_id = result.get("post_id")
        
        if "facebook" in context["platforms"] and generated_content.get("facebook_text"):
            result = await post_to_facebook(image_path, generated_content["facebook_text"])
            results["facebook"] = result
            if result["success"]:
                db_post.facebook_posted = True
                db_post.facebook_post_id = result.get("post_id")
        
        if "linkedin" in context["platforms"] and generated_content.get("linkedin_text"):
            result = await post_to_linkedin(image_path, generated_content["linkedin_text"])
            results["linkedin"] = result
            if result["success"]:
                db_post.linkedin_posted = True
                db_post.linkedin_post_id = result.get("post_id")
        
        if "gmail" in context["platforms"] and generated_content.get("gmail_subject"):
            recipient = context.get("recipient_email")
            if not recipient:
                results["gmail"] = {"success": False, "error": "No recipient email provided"}
            else:
                result = await send_via_gmail(
                    image_path,
                    generated_content["gmail_subject"],
                    generated_content["gmail_body"],
                    recipient
                )
                results["gmail"] = result
                if result["success"]:
                    db_post.gmail_sent = True
                    db_post.gmail_message_id = result.get("message_id")
        
        # Update post status
        if any(r.get("success") for r in results.values()):
            db_post.status = "posted"
            db_post.posted_time = datetime.utcnow()
        else:
            db_post.status = "failed"
        
        db.commit()
        
        # Reset agent for next post
        reset_agent()
        
        return {
            "success": True,
            "post_id": post_id,
            "platforms_posted": [p for p, r in results.items() if r.get("success")],
            "results": results,
            "message": f"✅ Posted to {', '.join([p for p, r in results.items() if r.get('success')])}!"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/schedule")
async def agent_schedule(scheduled_time: str = Form(...), db: Session = Depends(get_db)):
    """
    Schedule post for later time based on agent context
    """
    try:
        agent = get_agent()
        context = agent.get_context()
        
        if not context["has_image"]:
            raise HTTPException(status_code=400, detail="No image uploaded")
        if not context["platforms"]:
            raise HTTPException(status_code=400, detail="No platforms selected")
        
        image_path = context["image_path"]
        
        # Get image description
        image_description = await describe_image(image_path)
        
        # Generate content
        generated_content = generate_platform_content(
            image_description,
            context["platforms"],
            context["tone"]
        )
        
        # Parse datetime
        scheduled_dt = datetime.fromisoformat(scheduled_time.replace('Z', '+00:00'))
        
        # Create database entry
        post_id = str(uuid.uuid4())
        db_post = SocialPost(
            id=post_id,
            image_path=image_path,
            original_description=image_description,
            instagram_caption=generated_content.get("instagram_caption"),
            facebook_text=generated_content.get("facebook_text"),
            linkedin_text=generated_content.get("linkedin_text"),
            gmail_subject=generated_content.get("gmail_subject"),
            gmail_body=generated_content.get("gmail_body"),
            status="scheduled",
            scheduled_time=scheduled_dt,
            tone=context["tone"]
        )
        db.add(db_post)
        db.commit()
        
        # Reset agent for next post
        reset_agent()
        
        return {
            "success": True,
            "post_id": post_id,
            "status": "scheduled",
            "scheduled_time": scheduled_time,
            "platforms": context["platforms"],
            "message": f"✅ Post scheduled for {scheduled_dt.strftime('%Y-%m-%d %H:%M')}"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reset")
async def agent_reset():
    """Reset agent for a new conversation"""
    reset_agent()
    return {
        "success": True,
        "message": "Ready for a new post! What would you like to do?"
    }

@router.get("/status")
async def agent_status():
    """Get current agent context/status"""
    agent = get_agent()
    context = agent.get_context()
    return {
        "has_image": context["has_image"],
        "platforms": context["platforms"],
        "tone": context["tone"],
        "post_type": context["post_type"],
        "ready_to_post": context["has_image"] and context["platforms"] and context["post_type"]
    }
