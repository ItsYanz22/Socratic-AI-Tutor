from supabase import create_client, Client
from app.core.config import settings
import uuid

# This is the ADMIN client, using the SERVICE_ROLE_KEY.
# It can bypass Row Level Security and write to the DB.
supabase_admin_client: Client = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_SERVICE_ROLE_KEY
)


async def create_poc_entry(user_id: str, challenge_id: str, assists: int = 0) -> str | None:
    entry_uuid = str(uuid.uuid4())
    try:
        data, error = await supabase_admin_client.table("proofs").insert({
            "id": entry_uuid,
            "user_id": user_id,
            "challenge_id": challenge_id,
            "assists_used": assists
        }).execute()

        if error:
            print(f"Supabase error: {error}")
            return None

        return entry_uuid
    except Exception as e:
        print(f"Exception in create_poc_entry: {e}")
        return None