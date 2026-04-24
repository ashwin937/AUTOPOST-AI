from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()

from database import engine, Base
from routes import social, agent, oauth
from scheduler import run_scheduler

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AutoPost AI - Social Media Auto-Posting Platform with OAuth 2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*", "Authorization"],
)

# Mount uploads directory
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include routers
# ✅ NEW: OAuth 2.0 authentication routes
app.include_router(oauth.router)
app.include_router(social.router)
app.include_router(agent.router)

@app.on_event("startup")
async def on_startup():
    print("✅ AutoPost AI Backend Started")
    print("📱 Social Media APIs Ready (OAuth 2.0)")
    print("🤖 Google Gemini AI Integration Active")
    print("🔐 JWT/Bearer Token Authentication Ready")
    # Start scheduler task
    app.state.scheduler_task = asyncio.create_task(run_scheduler())

@app.on_event("shutdown")
async def on_shutdown():
    task = getattr(app.state, 'scheduler_task', None)
    if task and not task.done():
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            print('Scheduler task cancelled')

@app.get("/")
def read_root():
    return {
        "message": "AutoPost AI API - Social Media Content Automation with OAuth 2.0",
        "version": "3.0",
        "features": [
            "AI Content Generation (Gemini)",
            "OAuth 2.0 Facebook/LinkedIn/Gmail",
            "JWT Bearer Token Authentication",
            "Multi-platform Social Media Posting"
        ],
        "endpoints": {
            "authentication": {
                "facebook_auth": "GET /api/auth/facebook/authorize",
                "linkedin_auth": "GET /api/auth/linkedin/authorize",
                "refresh_token": "POST /api/auth/tokens/refresh",
                "verify_token": "POST /api/auth/tokens/verify"
            },
            "posts": {
                "upload_and_generate": "POST /api/posts/upload",
                "post_immediately": "POST /api/posts/{post_id}/post",
                "schedule_post": "POST /api/posts/{post_id}/schedule",
                "list_posts": "GET /api/posts",
                "get_post": "GET /api/posts/{post_id}"
            }
        }
    }

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "AutoPost AI v3.0",
        "auth": "OAuth 2.0 + JWT",
        "ai": "Google Gemini"
    }
