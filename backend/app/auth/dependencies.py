from fastapi import Depends, HTTPException, status, Request
from supabase import create_client, Client
from app.core.config import settings
from fastapi.security import OAuth2PasswordBearer

# This client is just for validating tokens. It uses the public 'anon' key.
supabase_auth_client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)

# This tells FastAPI to look for a token in the "Authorization" header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token") # We don't have a /token route, this is just for config

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        # supabase.auth.get_user() validates the JWT
        user_response = supabase_auth_client.auth.get_user(token)
        user = user_response.user
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user")
        return user
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")