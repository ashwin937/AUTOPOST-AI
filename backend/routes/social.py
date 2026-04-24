from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from database import SocialPost, get_db
from content_generator import generate_platform_content, get_mock_content
from social_apis import post_to_instagram, post_to_facebook, post_to_linkedin, send_via_gmail, validate_image, describe_image
from config import settings
import os
import uuid
from datetime import datetime, timedelta
import json
import asyncio

router = APIRouter(prefix="/api", tags=["posts"])

@router.post("/posts/upload")
async def upload_and_generate(
    file: UploadFile = File(...),
    platforms: str = Form(...),
    tone: str = Form(default="professional"),
    recipient_email: str = Form(default=""),
    db: Session = Depends(get_db)
):
    """
    Upload image and generate content for selected platforms
    """
    try:
        # Validate file
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
        
        # Parse platforms
        platform_list = [p.strip().lower() for p in platforms.split(",")]
        
        # Generate content
        generated_content = generate_platform_content(image_description, platform_list, tone)
        
        # Create database entry
        post_id = file_id
        db_post = SocialPost(
            id=post_id,
            image_path=file_path,
            original_description=image_description,
            instagram_caption=generated_content.get("instagram_caption"),
            facebook_text=generated_content.get("facebook_text"),
            linkedin_text=generated_content.get("linkedin_text"),
            gmail_subject=generated_content.get("gmail_subject"),
            gmail_body=generated_content.get("gmail_body"),
            status="draft",
            tone=tone
        )
        db.add(db_post)
        db.commit()
        db.refresh(db_post)
        
        return {
            "success": True,
            "post_id": post_id,
            "image_path": f"/uploads/{file_id}.{file_extension}",
            "description": image_description,
            "platforms": platform_list,
            "generated_content": generated_content,
            "tone": tone
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/posts/{post_id}/post")
async def post_immediately(
    post_id: str,
    platforms: str = Form(...),
    recipient_email: str = Form(default=""),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
):
    """
    Post immediately to selected platforms
    """
    try:
        post = db.query(SocialPost).filter(SocialPost.id == post_id).first()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        platform_list = [p.strip().lower() for p in platforms.split(",")]
        
        # Post to each platform
        results = {}
        
        if "instagram" in platform_list and post.instagram_caption:
            result = await post_to_instagram(post.image_path, post.instagram_caption)
            results["instagram"] = result
            if result["success"]:
                post.instagram_posted = True
                post.instagram_post_id = result.get("post_id")
        
        if "facebook" in platform_list and post.facebook_text:
            result = await post_to_facebook(post.image_path, post.facebook_text)
            results["facebook"] = result
            if result["success"]:
                post.facebook_posted = True
                post.facebook_post_id = result.get("post_id")
        
        if "linkedin" in platform_list and post.linkedin_text:
            result = await post_to_linkedin(post.image_path, post.linkedin_text)
            results["linkedin"] = result
            if result["success"]:
                post.linkedin_posted = True
                post.linkedin_post_id = result.get("post_id")
        
        if "gmail" in platform_list and post.gmail_subject and recipient_email:
            result = await send_via_gmail(post.image_path, post.gmail_subject, post.gmail_body, recipient_email)
            results["gmail"] = result
            if result["success"]:
                post.gmail_sent = True
                post.gmail_message_id = result.get("message_id")
        
        # Update post status
        if any(r.get("success") for r in results.values()):
            post.status = "posted"
            post.posted_time = datetime.utcnow()
        else:
            post.status = "failed"
        
        db.commit()
        
        return {
            "success": True,
            "post_id": post_id,
            "results": results,
            "status": post.status
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/posts/{post_id}/schedule")
async def schedule_post(
    post_id: str,
    platforms: str = Form(...),
    scheduled_time: str = Form(...),
    recipient_email: str = Form(default=""),
    db: Session = Depends(get_db)
):
    """
    Schedule post for later
    """
    try:
        post = db.query(SocialPost).filter(SocialPost.id == post_id).first()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        # Parse datetime
        scheduled_dt = datetime.fromisoformat(scheduled_time.replace('Z', '+00:00'))
        
        post.scheduled_time = scheduled_dt
        post.status = "scheduled"
        db.commit()
        
        return {
            "success": True,
            "post_id": post_id,
            "status": "scheduled",
            "scheduled_time": scheduled_time,
            "platforms": platforms.split(",")
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/posts")
async def list_posts(db: Session = Depends(get_db)):
    """List all posts"""
    posts = db.query(SocialPost).order_by(SocialPost.created_at.desc()).all()
    
    return [
        {
            "id": p.id,
            "image_path": p.image_path,
            "description": p.original_description,
            "status": p.status,
            "scheduled_time": p.scheduled_time,
            "posted_time": p.posted_time,
            "platforms_posted": {
                "instagram": p.instagram_posted,
                "facebook": p.facebook_posted,
                "linkedin": p.linkedin_posted,
                "gmail": p.gmail_sent
            },
            "created_at": p.created_at
        }
        for p in posts
    ]

@router.get("/posts/{post_id}")
async def get_post(post_id: str, db: Session = Depends(get_db)):
    """Get specific post details"""
    post = db.query(SocialPost).filter(SocialPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    return {
        "id": post.id,
        "image_path": post.image_path,
        "description": post.original_description,
        "content": {
            "instagram": post.instagram_caption,
            "facebook": post.facebook_text,
            "linkedin": post.linkedin_text,
            "gmail_subject": post.gmail_subject,
            "gmail_body": post.gmail_body
        },
        "status": post.status,
        "tone": post.tone,
        "scheduled_time": post.scheduled_time,
        "posted_time": post.posted_time,
        "platforms_posted": {
            "instagram": post.instagram_posted,
            "facebook": post.facebook_posted,
            "linkedin": post.linkedin_posted,
            "gmail": post.gmail_sent
        },
        "created_at": post.created_at
    }

@router.delete("/posts/{post_id}")
async def delete_post(post_id: str, db: Session = Depends(get_db)):
    """Delete a post"""
    post = db.query(SocialPost).filter(SocialPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Delete image file
    if post.image_path and os.path.exists(post.image_path):
        os.remove(post.image_path)
    
    db.delete(post)
    db.commit()
    
    return {"success": True, "message": "Post deleted"}

@router.put("/posts/{post_id}/content")
async def update_post_content(
    post_id: str,
    content: dict,
    db: Session = Depends(get_db)
):
    """Update generated content for a post"""
    post = db.query(SocialPost).filter(SocialPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if "instagram_caption" in content:
        post.instagram_caption = content["instagram_caption"]
    if "facebook_text" in content:
        post.facebook_text = content["facebook_text"]
    if "linkedin_text" in content:
        post.linkedin_text = content["linkedin_text"]
    if "gmail_subject" in content:
        post.gmail_subject = content["gmail_subject"]
    if "gmail_body" in content:
        post.gmail_body = content["gmail_body"]
    
    db.commit()
    
    return {"success": True, "message": "Content updated"}
