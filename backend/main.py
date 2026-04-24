from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()

from database import engine, Base
from routes import social, agent
from scheduler import run_scheduler

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AutoPost AI - Social Media Auto-Posting Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount uploads directory
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include routers
app.include_router(social.router)
app.include_router(agent.router)

@app.on_event("startup")
async def on_startup():
    print("✅ AutoPost AI Backend Started")
    print("📱 Social Media APIs Ready")
    print("🤖 Google Gemini AI Integration Active")
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
        "message": "AutoPost AI API - Social Media Content Automation",
        "version": "2.0",
        "endpoints": {
            "upload_and_generate": "POST /api/posts/upload",
            "post_immediately": "POST /api/posts/{post_id}/post",
            "schedule_post": "POST /api/posts/{post_id}/schedule",
            "list_posts": "GET /api/posts",
            "get_post": "GET /api/posts/{post_id}",
            "delete_post": "DELETE /api/posts/{post_id}",
            "update_content": "PUT /api/posts/{post_id}/content"
        }
    }

@app.get("/health")
def health():
    return {"status": "ok", "service": "AutoPost AI v2.0"}
