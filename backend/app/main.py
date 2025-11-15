from fastapi import FastAPI
from app.api.router import api_router
from fastapi.middleware.cors import CORSMiddleware

# Create the main app instance
app = FastAPI(title="Sahayogi API")

# --- Middleware ---
# This is CRITICAL. It allows our Vercel frontend to talk to this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For now, allow all. We'll lock this down later.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routers ---
# Include the master router
app.include_router(api_router, prefix="/api/v1")

# --- "Hello World" Route ---
@app.get("/", tags=["Health"])
async def read_root():
    return {"status": "Sahayogi API is running!"}