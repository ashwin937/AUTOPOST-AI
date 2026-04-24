from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import os
from dotenv import load_dotenv
from anthropic import Anthropic
from vector_db import get_similar_posts

load_dotenv()

router = APIRouter()

ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY")
CLAUDE_MODEL = "claude-sonnet-4-20250514"


class GenerateRequest(BaseModel):
    topic: str
    platforms: List[str]
    tone: str


@router.post("/api/generate")
async def generate(req: GenerateRequest) -> Dict[str, List[str]]:
    # fetch similar posts
    similar = get_similar_posts(req.topic, n=3)
    similar_texts = [s['document'] for s in similar]

    prompt_similar = "\n".join([f"- {t}" for t in similar_texts]) if similar_texts else "None"

    system_prompt = (
        "You are an expert social media strategist. Generate engaging platform-optimized content. "
        f"Here are similar posts already created (avoid repetition): {prompt_similar}"
    )

    outputs: Dict[str, List[str]] = {
        "twitter": [],
        "linkedin": [],
        "instagram": []
    }

    # If no API key, return mocked variants to allow local dev
    if not ANTHROPIC_KEY:
        for p in req.platforms:
            variants = [f"{req.topic} — {req.tone} variant {i+1} for {p}" for i in range(3)]
            outputs[p] = variants
        return outputs

    client = Anthropic(api_key=ANTHROPIC_KEY)

    # Build a single prompt that requests 3 variants per platform
    for platform in req.platforms:
        user_message = (
            f"Generate exactly 3 short, distinct caption variants for {platform}.\n"
            f"Tone: {req.tone}\n"
            f"Topic: {req.topic}\n"
            f"Return each variant on a separate line, numbered 1, 2, 3. No additional text."
        )
        try:
            resp = client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=300,
                temperature=0.7,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}]
            )
            text = resp.content[0].text
            # split lines and parse variants
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            variants = []
            for line in lines:
                # remove numbering if present
                cleaned = line.lstrip('0123456789.-) ')
                if cleaned:
                    variants.append(cleaned)
            # fallback if not enough
            while len(variants) < 3:
                variants.append(f"{req.topic} ({platform}) - variant {len(variants)+1}")
            outputs[platform] = variants[:3]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Claude API error: {str(e)}")

    # Ensure all platforms keys exist
    for key in outputs.keys():
        outputs.setdefault(key, [])

    return outputs
