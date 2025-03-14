"""
Server-side handler for Discord account verification.

This is a mockup of what would be implemented on the StudentHub web server
to handle the Discord account verification flow.
"""

import logging
from typing import Optional, Dict

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# In-memory storage for linked accounts: discord_id -> studenthub_user_id
# In a real implementation, this would be stored in a database
linked_accounts: Dict[int, str] = {}

async def verify_discord_link(token: str, studenthub_user_id: str) -> Optional[int]:
    """
    Verify a Discord verification token and link the Discord account to a StudentHub user.
    
    Args:
        token: The one-time verification token
        studenthub_user_id: The StudentHub user ID to link to
        
    Returns:
        Optional[int]: The Discord user ID if verification was successful, None otherwise
    """
    # Import the verification function here to avoid circular imports
    from bot.discord_client import StudentHubBot
    
    try:
        # Verify the token and get the Discord user ID
        discord_user_id = StudentHubBot.verify_token(token)
        
        # Link the Discord user ID to the StudentHub user ID
        linked_accounts[discord_user_id] = studenthub_user_id
        
        logger.info(f"Linked Discord user {discord_user_id} to StudentHub user {studenthub_user_id}")
        
        return discord_user_id
    except ValueError as e:
        logger.error(f"Verification failed: {e}")
        return None

def get_studenthub_user_id(discord_user_id: int) -> Optional[str]:
    """
    Get the StudentHub user ID linked to a Discord user ID.
    
    Args:
        discord_user_id: The Discord user ID
        
    Returns:
        Optional[str]: The StudentHub user ID if linked, None otherwise
    """
    return linked_accounts.get(discord_user_id)

def get_discord_user_id(studenthub_user_id: str) -> Optional[int]:
    """
    Get the Discord user ID linked to a StudentHub user ID.
    
    Args:
        studenthub_user_id: The StudentHub user ID
        
    Returns:
        Optional[int]: The Discord user ID if linked, None otherwise
    """
    for discord_id, sh_user_id in linked_accounts.items():
        if sh_user_id == studenthub_user_id:
            return discord_id
    return None 