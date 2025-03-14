import os
import logging
from dotenv import load_dotenv
from bot.discord_client import run_bot
import sys

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("bot.log")
    ]
)
logger = logging.getLogger(__name__)

def main():
    """
    Main entry point for the StudentHub Discord Bot.
    Loads environment variables and starts the bot.
    """
    # Load environment variables from .env file
    load_dotenv()
    
    logger.info("Starting StudentHub Discord Bot")
    
    # Print environment variables for debugging (without showing actual values)
    logger.info("Environment variables:")
    logger.info(f"DISCORD_TOKEN: {'Set' if os.getenv('DISCORD_TOKEN') else 'Not set'}")
    logger.info(f"OPENAI_API_KEY: {'Set' if os.getenv('OPENAI_API_KEY') else 'Not set'}")
    logger.info(f"GOOGLE_API_CREDENTIALS: {'Set' if os.getenv('GOOGLE_API_CREDENTIALS') else 'Not set'}")
    logger.info(f"GOOGLE_DOC_IDS: {'Set' if os.getenv('GOOGLE_DOC_IDS') else 'Not set'}")
    logger.info(f"STUDENTHUB_BASE_URL: {'Set' if os.getenv('STUDENTHUB_BASE_URL') else 'Not set'}")
    logger.info(f"TEST_GUILD_ID: {'Set' if os.getenv('TEST_GUILD_ID') else 'Not set (global slash commands)'}")
    
    # Validate required environment variables
    required_vars = ["DISCORD_TOKEN", "OPENAI_API_KEY", "GOOGLE_API_CREDENTIALS", "GOOGLE_DOC_IDS", "STUDENTHUB_BASE_URL"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please set these variables in your .env file")
        exit(1)
    
    # Check if Google API Credentials file exists
    creds_path = os.getenv("GOOGLE_API_CREDENTIALS")
    if not os.path.exists(creds_path):
        logger.error(f"Google API credentials file not found at: {creds_path}")
        logger.error("Please check the path in your .env file")
        exit(1)
    
    # Start the bot
    try:
        logger.info("Running bot...")
        run_bot()
    except Exception as e:
        logger.error(f"Error running bot: {e}")
        exit(1)

if __name__ == "__main__":
    main() 