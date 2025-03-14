import os
import logging
from openai import OpenAI
import asyncio
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get API key from environment
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    logger.warning("OPENAI_API_KEY not found in environment variables. OpenAI functionality will not work.")

async def generate_response(question: str, knowledge: Optional[str] = None) -> str:
    """
    Generate a response to a user's question using OpenAI's API.
    
    Args:
        question: The user's question
        knowledge: Optional knowledge context from Google Docs
        
    Returns:
        A string response to the question
    """
    try:
        # Check if we have a valid API key
        if not api_key:
            return "Error: OpenAI API key is not properly configured. Please check your .env file."
            
        # Create a system prompt that explains the bot's purpose and includes knowledge if available
        system_message = {
            "role": "system", 
            "content": "You are StudentHub Assistant, a helpful AI that provides information about the StudentHub Discord server. Your goal is to assist users in finding the right channels for their questions and understanding server guidelines."
        }
        
        # Add context from knowledge base if available
        if knowledge:
            system_message["content"] += f"\n\nHere is some relevant information about StudentHub that might help with answering:\n{knowledge}"
        
        # Create the user message
        user_message = {
            "role": "user",
            "content": question
        }
        
        # Run the API call in a thread to avoid blocking
        return await asyncio.to_thread(
            _call_openai_api,
            messages=[system_message, user_message]
        )
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        return f"I'm sorry, I encountered an error while generating a response: {str(e)}"

def _call_openai_api(messages):
    """
    Call the OpenAI API synchronously.
    
    Args:
        messages: The messages to send to the API
        
    Returns:
        The generated text response
    """
    try:
        # Create a client with the API key - no additional parameters to avoid conflicts
        # with different versions of the openai library
        client = OpenAI(
            api_key=api_key,
            # No proxies or other additional parameters that might cause compatibility issues
        )
        
        # Make the API call
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Can use gpt-4o if available in your account
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        
        # Extract and return the response
        return completion.choices[0].message.content
    except Exception as e:
        logger.error(f"Error calling OpenAI API: {e}")
        raise 