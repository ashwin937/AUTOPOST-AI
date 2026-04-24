"""
Background scheduler: checks for scheduled posts and posts them when due.
Runs as an asyncio task started from main.py startup event.
"""
import asyncio
from datetime import datetime, timezone
from database import SessionLocal, SocialPost
from social_apis import post_to_instagram, post_to_facebook, post_to_linkedin, send_via_gmail

async def _process_post(post):
    results = {}
    try:
        if post.instagram_caption:
            res = await post_to_instagram(post.image_path, post.instagram_caption)
            results['instagram'] = res
            if res.get('success'):
                post.instagram_posted = True
                post.instagram_post_id = res.get('post_id')
        if post.facebook_text:
            res = await post_to_facebook(post.image_path, post.facebook_text, scheduled_time=None)
            results['facebook'] = res
            if res.get('success'):
                post.facebook_posted = True
                post.facebook_post_id = res.get('post_id')
        if post.linkedin_text:
            res = await post_to_linkedin(post.image_path, post.linkedin_text)
            results['linkedin'] = res
            if res.get('success'):
                post.linkedin_posted = True
                post.linkedin_post_id = res.get('post_id')
        # For Gmail, we don't auto-send unless recipient exists in the record (not stored by default)
        # This scheduler will not send Gmail unless post.gmail_subject exists and there is a stored recipient_email attribute
        if getattr(post, 'recipient_email', None) and post.gmail_subject:
            res = await send_via_gmail(post.image_path, post.gmail_subject, post.gmail_body, post.recipient_email)
            results['gmail'] = res
            if res.get('success'):
                post.gmail_sent = True
                post.gmail_message_id = res.get('message_id')

        if any(r.get('success') for r in results.values()):
            post.status = 'posted'
            post.posted_time = datetime.utcnow()
        else:
            post.status = 'failed'
    except Exception as e:
        print(f"Error posting scheduled post {post.id}: {e}")
        post.status = 'failed'

    return results

async def run_scheduler(poll_interval_seconds: int = 60):
    """Main scheduler loop. Polls DB every poll_interval_seconds and posts scheduled items."""
    print("🔁 Scheduler started, polling every {}s".format(poll_interval_seconds))
    while True:
        try:
            now = datetime.now(timezone.utc)
            db = SessionLocal()
            try:
                due = db.query(SocialPost).filter(
                    SocialPost.status == 'scheduled',
                    SocialPost.scheduled_time <= now
                ).all()
                if due:
                    print(f"Found {len(due)} scheduled posts due at {now.isoformat()}")
                for post in due:
                    try:
                        results = await _process_post(post)
                        db.add(post)
                        db.commit()
                        print(f"Processed scheduled post {post.id}: {results}")
                    except Exception as e:
                        print(f"Failed to process post {post.id}: {e}")
                        try:
                            post.status = 'failed'
                            db.add(post)
                            db.commit()
                        except Exception:
                            db.rollback()
            finally:
                db.close()
        except Exception as e:
            print(f"Scheduler loop error: {e}")
        await asyncio.sleep(poll_interval_seconds)
