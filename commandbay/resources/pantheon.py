
from fastapi import APIRouter, HTTPException, status
import os

pantheon_router = APIRouter()

BAN_FILE = "banned_users.txt"


def get_banned_users() -> list[str]:
    """Read the banned users from the text file (if it exists)."""
    if not os.path.exists(BAN_FILE):
        return []
    with open(BAN_FILE, "r", encoding="utf-8") as f:
        # Return list of non-empty stripped lines
        return [line.strip() for line in f if line.strip()]


@pantheon_router.put("/ban/{username}", status_code=status.HTTP_201_CREATED)
def ban_user(username: str):
    """
    Ban a user by adding them to the banned_users.txt file.
    If the user is already banned (case-insensitive), do nothing extra.
    """
    banned_users = get_banned_users()

    # Check if this username is already in the banned list (case-insensitive)
    lowercased_banned = [u.lower() for u in banned_users]
    if username.lower() in lowercased_banned:
        # The user is already banned. PUT is idempotent, so we return success.
        return {"message": f"'{username}' is already banned."}

    # If not present, append the new username to the file
    with open(BAN_FILE, "a", encoding="utf-8") as f:
        f.write(username + "\n")

    return {"message": f"User '{username}' has been banned."}


@pantheon_router.get("/ban")
def list_banned_users():
    """
    Returns the list of banned usernames.
    """
    return get_banned_users()
