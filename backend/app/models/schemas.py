from pydantic import BaseModel
from typing import List, Dict, Any

# --- Socratic Tutor Models ---
class TutorRequest(BaseModel):
    prompt: str
    # This UPGRADE is critical for the AI's memory
    chat_history: List[Dict[str, Any]] = []

class TutorResponse(BaseModel):
    response: str

# --- NEW SNIPPET MODELS ---
class SnippetRequest(BaseModel):
    challenge_id: str

class SnippetResponse(BaseModel):
    snippet: str