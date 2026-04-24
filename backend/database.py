from sqlalchemy import create_engine, Column, String, DateTime, Integer, Boolean, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config import settings

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class SocialPost(Base):
    __tablename__ = "social_posts"
    
    id = Column(String, primary_key=True, index=True)
    image_path = Column(String)
    original_description = Column(Text)
    
    # Generated content per platform
    instagram_caption = Column(Text, nullable=True)
    facebook_text = Column(Text, nullable=True)
    linkedin_text = Column(Text, nullable=True)
    gmail_subject = Column(String, nullable=True)
    gmail_body = Column(Text, nullable=True)
    
    # Post status
    status = Column(String, default="draft")  # draft, scheduled, posted, failed
    scheduled_time = Column(DateTime, nullable=True)
    posted_time = Column(DateTime, nullable=True)
    
    # Platform posting status
    instagram_posted = Column(Boolean, default=False)
    facebook_posted = Column(Boolean, default=False)
    linkedin_posted = Column(Boolean, default=False)
    gmail_sent = Column(Boolean, default=False)
    
    # API response IDs
    instagram_post_id = Column(String, nullable=True)
    facebook_post_id = Column(String, nullable=True)
    linkedin_post_id = Column(String, nullable=True)
    gmail_message_id = Column(String, nullable=True)
    
    # Engagement metrics
    instagram_likes = Column(Integer, default=0)
    instagram_comments = Column(Integer, default=0)
    facebook_likes = Column(Integer, default=0)
    facebook_shares = Column(Integer, default=0)
    linkedin_likes = Column(Integer, default=0)
    linkedin_comments = Column(Integer, default=0)
    
    # Metadata
    tags = Column(String, nullable=True)
    tone = Column(String, default="professional")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
