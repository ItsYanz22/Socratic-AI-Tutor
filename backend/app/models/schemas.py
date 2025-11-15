from pydantic import BaseModel

# --- Socratic Tutor Models ---
class TutorRequest(BaseModel):
    prompt: str

class TutorResponse(BaseModel):
    response: str