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


# --- THIS IS THE NEW FUNCTION YOU NEED TO ADD ---
async def log_snippet_request(user_id: str, challenge_id: str):
    """
    Logs an "assist" event to the assist_logs table.
    """
    entry_uuid = str(uuid.uuid4())
    try:
        # We use the same 'data, error' syntax as your function above
        # This assumes you have created the 'assist_logs' table in Supabase
        data, error = await supabase_admin_client.table("assist_logs").insert({
            "id": entry_uuid,
            "user_id": user_id,
            "challenge_id": challenge_id,
            "type": "snippet"  # We log that this was a 'snippet' assist
        }).execute()

        if error:
            print(f"Error logging snippet request: {error}")
        else:
            print(f"Logged snippet assist for user {user_id}")

    except Exception as e:
        print(f"Exception in log_snippet_request: {e}")