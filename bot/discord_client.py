import discord
from discord.ext import commands
import logging
import os
import secrets
import time
import uuid
import asyncio
from typing import Dict, Tuple

from ai.openai_client import generate_response
from knowledge.gdocs_client import fetch_knowledge

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Token storage: token -> (user_id, expiration_timestamp)
# This is in-memory storage; for production, use a database
token_storage: Dict[str, Tuple[int, float]] = {}
# Token expiration time in seconds (30 minutes)
TOKEN_EXPIRATION = 1800

class StudentHubBot(commands.Bot):
    """
    Discord bot class for StudentHub.
    Handles message commands and interactions.
    """
    
    def __init__(self):
        # Set up intents (make sure to enable these in the Discord Developer Portal)
        intents = discord.Intents.default()
        intents.message_content = True  # Privileged intent
        intents.members = True  # Needed for DM functionality
        
        # Pass intents to the parent constructor
        super().__init__(command_prefix='!', intents=intents)
        
        # Set up token cleanup task
        self.bg_task = None
        
    async def setup_hook(self):
        """Set up slash commands for modern Discord interactions."""
        # Register slash commands - replace guild_id with your test server ID or remove for global commands
        guild_id = os.getenv("TEST_GUILD_ID")
        if guild_id:
            guild = discord.Object(id=int(guild_id))
            self.tree.add_command(discord.app_commands.Command(
                name="link",
                description="Link your Discord account to your StudentHub profile",
                callback=self.link_slash
            ), guild=guild)
        else:
            # Global commands take up to an hour to propagate
            self.tree.add_command(discord.app_commands.Command(
                name="link",
                description="Link your Discord account to your StudentHub profile",
                callback=self.link_slash
            ))
        
        await self.tree.sync()
        
    async def on_ready(self):
        """Called when the bot is ready and connected to Discord."""
        logger.info(f'Logged in as {self.user} (ID: {self.user.id})')
        logger.info(f'Bot is in {len(self.guilds)} guild(s)')
        for guild in self.guilds:
            logger.info(f'- {guild.name} (ID: {guild.id})')
        logger.info('------')
        
        # Register traditional commands
        self.add_commands()
        
        # Start background task to clean expired tokens
        self.bg_task = self.loop.create_task(self.clean_expired_tokens())
        
    def add_commands(self):
        """Add commands to the bot after it's ready."""
        
        @self.command(name="ask")
        async def ask_command(ctx, *, question=""):
            """Ask a question about StudentHub"""
            if not question:
                await ctx.send("Please provide a question. Example: `!ask What channel should I post in?`")
                return
            await self.handle_ask(ctx, question)
            
        @self.command(name="link")
        async def link_command(ctx):
            """Link your Discord account to your StudentHub profile"""
            await self.handle_link(ctx)
    
    async def handle_ask(self, ctx, question):
        """
        Handler for the !ask command.
        Fetches knowledge and generates a response using OpenAI.
        
        Args:
            ctx: The command context
            question: The user's question
        """
        logger.info(f"Received question from {ctx.author}: {question}")
        
        # Let the user know we're processing
        async with ctx.typing():
            try:
                # First, see if we can find relevant information in our knowledge base
                knowledge = await fetch_knowledge(question)
                
                # Generate a response using OpenAI
                response = await generate_response(question, knowledge)
                
                # Send the response back
                await ctx.reply(response)
            except Exception as e:
                logger.error(f"Error processing question: {e}")
                await ctx.reply("I'm sorry, I encountered an error while processing your question. Please try again later.")
        
    async def on_message(self, message):
        """Process incoming messages."""
        # Don't process messages from the bot itself
        if message.author.id == self.user.id:
            return
            
        await self.process_commands(message)
    
    async def handle_link(self, ctx):
        """
        Handler for the !link command.
        Generates a one-time token and sends a verification link to the user.
        
        Args:
            ctx: The command context
        """
        logger.info(f"Received link request from {ctx.author}")
        
        try:
            # Generate a secure token
            token = self.generate_token(ctx.author.id)
            base_url = os.getenv("STUDENTHUB_BASE_URL", "https://studenthub.co")
            verification_link = f"{base_url}/link-discord?token={token}"
            
            # Send a DM to the user with the verification link
            try:
                await ctx.author.send(
                    f"Click the link below to link your Discord account to your StudentHub profile:\n\n"
                    f"{verification_link}\n\n"
                    f"This link will expire in 30 minutes and can only be used once."
                )
                
                # If we're in a guild channel, send a confirmation message
                if ctx.guild:
                    await ctx.reply("I've sent you a DM with a verification link to link your Discord account to StudentHub!")
            except discord.Forbidden:
                # If the user has DMs disabled
                await ctx.reply(
                    "I couldn't send you a DM. Please enable direct messages from server members and try again.\n"
                    "Server Settings > Privacy Settings > Allow direct messages from server members"
                )
        except Exception as e:
            logger.error(f"Error processing link request: {e}")
            await ctx.reply("I'm sorry, I encountered an error while processing your request. Please try again later.")
    
    async def link_slash(self, interaction: discord.Interaction):
        """
        Slash command handler for the /link command.
        Generates a one-time token and sends a verification link to the user.
        
        Args:
            interaction: The interaction object
        """
        logger.info(f"Received slash command link request from {interaction.user}")
        
        try:
            # Generate a secure token
            token = self.generate_token(interaction.user.id)
            base_url = os.getenv("STUDENTHUB_BASE_URL", "https://studenthub.co")
            verification_link = f"{base_url}/link-discord?token={token}"
            
            # Send a DM to the user with the verification link
            try:
                await interaction.user.send(
                    f"Click the link below to link your Discord account to your StudentHub profile:\n\n"
                    f"{verification_link}\n\n"
                    f"This link will expire in 30 minutes and can only be used once."
                )
                
                # Respond to the interaction
                await interaction.response.send_message(
                    "I've sent you a DM with a verification link to link your Discord account to StudentHub!",
                    ephemeral=True  # Only visible to the user who triggered the command
                )
            except discord.Forbidden:
                # If the user has DMs disabled
                await interaction.response.send_message(
                    "I couldn't send you a DM. Please enable direct messages from server members and try again.\n"
                    "Server Settings > Privacy Settings > Allow direct messages from server members",
                    ephemeral=True
                )
        except Exception as e:
            logger.error(f"Error processing slash command link request: {e}")
            await interaction.response.send_message(
                "I'm sorry, I encountered an error while processing your request. Please try again later.",
                ephemeral=True
            )
    
    def generate_token(self, user_id: int) -> str:
        """
        Generates a secure one-time token for account linking.
        
        Args:
            user_id: The Discord user ID to associate with this token
            
        Returns:
            str: A secure token
        """
        # Generate a random token
        token = secrets.token_urlsafe(16)
        
        # Store the token with user ID and expiration timestamp
        expiration = time.time() + TOKEN_EXPIRATION
        token_storage[token] = (user_id, expiration)
        
        logger.info(f"Generated token for user {user_id}, expires at {expiration}")
        return token
    
    @staticmethod
    def verify_token(token: str) -> int:
        """
        Verifies a token and returns the associated user ID if valid.
        
        Args:
            token: The token to verify
            
        Returns:
            int: The Discord user ID associated with the token
            
        Raises:
            ValueError: If the token is invalid or expired
        """
        if token not in token_storage:
            raise ValueError("Invalid token")
            
        user_id, expiration = token_storage[token]
        
        # Check if the token has expired
        if time.time() > expiration:
            # Remove expired token
            del token_storage[token]
            raise ValueError("Token has expired")
            
        # Remove the token (one-time use)
        del token_storage[token]
        
        return user_id
    
    async def notify_account_linked(self, discord_user_id: int, studenthub_user_id: str):
        """
        Notifies a user that their account has been successfully linked.
        
        Args:
            discord_user_id: The Discord user ID
            studenthub_user_id: The StudentHub user ID
        """
        try:
            # Get the user from the ID
            user = await self.fetch_user(discord_user_id)
            
            if user:
                await user.send(
                    f"Your Discord account has been successfully linked to your StudentHub profile!\n\n"
                    f"StudentHub User ID: {studenthub_user_id}\n"
                    f"Discord User ID: {discord_user_id}\n\n"
                    f"You can now use all features that require account linking."
                )
                logger.info(f"Sent account linking confirmation to user {discord_user_id}")
            else:
                logger.error(f"Could not find user with ID {discord_user_id}")
        except Exception as e:
            logger.error(f"Error sending account linking confirmation: {e}")
    
    async def clean_expired_tokens(self):
        """Background task to clean expired tokens."""
        await self.wait_until_ready()
        logger.info("Starting token cleanup task")
        
        while not self.is_closed():
            current_time = time.time()
            
            # Find expired tokens
            expired_tokens = [
                token for token, (_, expiration) in token_storage.items()
                if current_time > expiration
            ]
            
            # Remove expired tokens
            for token in expired_tokens:
                del token_storage[token]
                logger.info(f"Removed expired token {token}")
                
            # Check every 10 minutes
            await asyncio.sleep(600)

def get_discord_bot():
    """Creates and returns the Discord bot instance."""
    bot = StudentHubBot()
    return bot

def run_bot():
    """Runs the Discord bot using the token from environment variables."""
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise ValueError("DISCORD_TOKEN not found in environment variables. Please set it in the .env file.")
    
    logger.info("Starting Discord bot...")
    bot = get_discord_bot()
    bot.run(token, log_handler=None)  # Disable default Discord logging handler 