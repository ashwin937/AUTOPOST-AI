"""
AI Agent for processing natural language commands and guiding users through posting workflow.
"""
from anthropic import Anthropic
from config import settings
import json
import re

client = Anthropic() if settings.ANTHROPIC_API_KEY else None

class PostingAgent:
    def __init__(self):
        self.conversation_history = []
        self.current_context = {
            "platforms": [],
            "tone": "professional",
            "has_image": False,
            "image_path": None,
            "post_type": None,  # "immediate" or "scheduled"
            "scheduled_time": None,
            "recipient_email": None
        }
    
    def reset(self):
        """Reset conversation and context for new post"""
        self.conversation_history = []
        self.current_context = {
            "platforms": [],
            "tone": "professional",
            "has_image": False,
            "image_path": None,
            "post_type": None,
            "scheduled_time": None,
            "recipient_email": None
        }
    
    def process_user_input(self, user_message: str) -> dict:
        """
        Process user input and return agent response with actions
        Returns: {
            "response": "Agent message to user",
            "action": "ask_for_image" | "ready_to_post" | "ask_for_schedule" | "confirm_post" | None,
            "context": current_context,
            "next_step": "..."
        }
        """
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # Build system prompt
        system_prompt = f"""You are a helpful social media posting assistant. Your job is to guide users through posting content to social media platforms.

Current Context:
- Selected Platforms: {', '.join(self.current_context['platforms']) if self.current_context['platforms'] else 'None yet'}
- Content Tone: {self.current_context['tone']}
- Has Image: {self.current_context['has_image']}
- Post Type: {self.current_context['post_type'] or 'Not decided yet'}

Your task:
1. Parse the user's intent (do they want to post, schedule, or modify settings?)
2. Ask for missing information (image, platforms, tone, timing)
3. Confirm details before posting
4. Be friendly, concise, and guide them step by step

Guidelines:
- If they mention posting to Instagram, Facebook, LinkedIn, or Gmail, note those platforms
- If they mention "casual", "funny", "professional", "inspirational" - that's the tone
- If they say "now", "immediately", "right away" - that's immediate posting
- If they say "schedule", "later", "tomorrow", "2pm" - that's scheduled posting
- Always ask for image if they haven't provided one yet
- Keep responses short (1-2 sentences max)

Return your response in JSON format:
{{
    "message": "Your response to the user",
    "platforms": ["instagram", "facebook", "linkedin"],  // updated platforms if user mentioned any
    "tone": "professional",  // updated tone if user mentioned any
    "post_type": "immediate",  // "immediate" or "scheduled" if user specified
    "action": "ask_for_image" | "ready_to_post" | "ask_for_schedule" | "confirm" | null,
    "needs_image": true/false,
    "next_step": "User should upload image, Select more platforms, Confirm details, etc"
}}"""
        
        try:
            if client:
                response = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=500,
                    system=system_prompt,
                    messages=self.conversation_history
                )
                agent_response = response.content[0].text
            else:
                # Mock response for testing
                agent_response = self._mock_agent_response(user_message)
            
            # Parse JSON response
            try:
                json_match = re.search(r'\{.*\}', agent_response, re.DOTALL)
                if json_match:
                    parsed = json.loads(json_match.group())
                else:
                    parsed = self._parse_response_to_json(agent_response)
            except json.JSONDecodeError:
                parsed = self._parse_response_to_json(agent_response)
            
            # Update context based on agent response
            if parsed.get("platforms"):
                self.current_context["platforms"] = parsed["platforms"]
            if parsed.get("tone"):
                self.current_context["tone"] = parsed["tone"]
            if parsed.get("post_type"):
                self.current_context["post_type"] = parsed["post_type"]
            
            # Add agent response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": parsed.get("message", agent_response)
            })
            
            return {
                "response": parsed.get("message", agent_response),
                "action": parsed.get("action"),
                "context": self.current_context,
                "needs_image": parsed.get("needs_image", False),
                "next_step": parsed.get("next_step")
            }
        
        except Exception as e:
            print(f"Agent error: {e}")
            return {
                "response": "Sorry, I had trouble processing that. Can you try again?",
                "action": None,
                "context": self.current_context,
                "needs_image": not self.current_context["has_image"],
                "next_step": "Try rephrasing your request"
            }
    
    def _parse_response_to_json(self, response: str) -> dict:
        """Parse natural language response into structured JSON"""
        lower = response.lower()
        
        platforms = []
        if "instagram" in lower:
            platforms.append("instagram")
        if "facebook" in lower:
            platforms.append("facebook")
        if "linkedin" in lower:
            platforms.append("linkedin")
        if "gmail" in lower or "email" in lower:
            platforms.append("gmail")
        
        tone = "professional"
        if "casual" in lower:
            tone = "casual"
        elif "funny" in lower:
            tone = "funny"
        elif "inspirational" in lower:
            tone = "inspirational"
        
        post_type = None
        if "schedule" in lower or "later" in lower:
            post_type = "scheduled"
        elif "now" in lower or "immediately" in lower or "right away" in lower:
            post_type = "immediate"
        
        action = None
        if not self.current_context["has_image"]:
            action = "ask_for_image"
        elif not self.current_context["platforms"]:
            action = "confirm"
        elif post_type == "scheduled" and not self.current_context["post_type"]:
            action = "ask_for_schedule"
        elif self.current_context["platforms"] and self.current_context["has_image"]:
            action = "ready_to_post"
        
        return {
            "message": response,
            "platforms": platforms or self.current_context["platforms"],
            "tone": tone,
            "post_type": post_type,
            "action": action,
            "needs_image": not self.current_context["has_image"],
            "next_step": "Continue the conversation"
        }
    
    def _mock_agent_response(self, user_message: str) -> str:
        """Mock agent response for testing without Claude API"""
        lower = user_message.lower()
        
        if not self.current_context["has_image"]:
            return json.dumps({
                "message": "Great! Do you have a picture you'd like to post?",
                "action": "ask_for_image",
                "platforms": [],
                "tone": "professional",
                "needs_image": True,
                "next_step": "Please upload an image"
            })
        
        if not self.current_context["platforms"]:
            if "instagram" in lower:
                platforms = ["instagram"]
            elif "facebook" in lower:
                platforms = ["facebook"]
            elif "linkedin" in lower:
                platforms = ["linkedin"]
            else:
                platforms = ["instagram", "facebook"]
            
            return json.dumps({
                "message": f"Perfect! I'll post to {', '.join(platforms)}. Ready to post now?",
                "action": "confirm",
                "platforms": platforms,
                "tone": "professional",
                "post_type": "immediate",
                "needs_image": False,
                "next_step": "Confirm to proceed"
            })
        
        return json.dumps({
            "message": "All set! Ready to post to " + ", ".join(self.current_context["platforms"]),
            "action": "ready_to_post",
            "platforms": self.current_context["platforms"],
            "tone": self.current_context["tone"],
            "needs_image": False,
            "next_step": "Proceed with posting"
        })
    
    def set_image(self, image_path: str):
        """Mark that an image has been provided"""
        self.current_context["has_image"] = True
        self.current_context["image_path"] = image_path
    
    def get_context(self) -> dict:
        """Get current context"""
        return self.current_context

# Global agent instance
_agent = PostingAgent()

def get_agent() -> PostingAgent:
    """Get or create agent instance"""
    return _agent

def reset_agent():
    """Reset agent for new conversation"""
    global _agent
    _agent = PostingAgent()
