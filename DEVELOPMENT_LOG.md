# StudentHub Discord Bot - Development Log

## Project Setup and Implementation - March 14, 2025

### Initial Project Setup
- Created project directory structure
- Implemented bot modules:
  - Discord client (`bot/discord_client.py`)
  - OpenAI integration (`ai/openai_client.py`)
  - Google Docs knowledge base (`knowledge/gdocs_client.py`)
- Created configuration files:
  - `requirements.txt` with all necessary dependencies
  - `.env.example` for environment variables template

### Dependencies
Added the following major dependencies:
- `discord.py` (v2.3.2) for Discord API integration
- `openai` (v1.3.5) for OpenAI API integration
- `google-api-python-client` for Google Docs access
- `python-dotenv` for environment variable management

### Implementation Details

#### Discord Bot Interface
- Implemented `StudentHubBot` class with:
  - Command handling for `!ask` commands
  - Event handlers for bot initialization
  - Proper error handling and logging
- Set up privileged intents for message content access

#### AI Response Engine
- Integrated OpenAI's Chat API using the modern client approach
- Implemented asynchronous processing to avoid blocking Discord events
- Added system prompts that incorporate knowledge base content
- Set up with GPT-3.5-Turbo model (can be upgraded to GPT-4/GPT-4o)

#### Knowledge Base
- Implemented Google Docs integration for knowledge retrieval
- Added caching to minimize API calls
- Created simple keyword-based search for finding relevant content
- Set up document processing for proper text extraction

### Configuration and Credentials
Set up the following credentials:
- Discord Bot Token
- OpenAI API Key
- Google Cloud Service Account
  - Created JSON credentials file
  - Set up OAuth2 access for Google Docs/Drive APIs
- Google Doc ID for knowledge base

### Troubleshooting
- Fixed environment variable loading issues
- Updated OpenAI client to match current API structure
- Resolved Discord privileged intents configuration
- Fixed API authentication issues

### Future Improvements
Potential enhancements to consider:
- Implement more sophisticated search (embeddings-based)
- Add slash commands for Discord interactions
- Implement conversation memory
- Add feedback mechanism for users
- Set up periodic refreshing of the Google Docs cache

## Running the Bot
1. Ensure all environment variables are set in `.env`
2. Run `python main.py`
3. The bot will log in to Discord and respond to `!ask` commands

## Deployment Notes
- For persistent hosting, consider:
  - Deploying to cloud services (Heroku, AWS, etc.)
  - Using process managers (PM2) for auto-restarts
  - Setting up as a system service for automatic startup

## Current Configuration
- Using OpenAI's GPT-3.5-Turbo model
- Discord command prefix: `!`
- Single Google Doc as knowledge source 

## Account Linking Feature Implementation - March 15, 2025

### Feature Overview
Added the ability for users to link their Discord accounts to their StudentHub profiles using a secure verification flow:

1. User initiates the process with `!link` or `/link` commands
2. Bot generates a secure one-time token and sends a verification link to the user via DM
3. User clicks the link and is directed to the StudentHub website
4. After logging in, the StudentHub website verifies the token and links the accounts
5. Bot sends a confirmation message to the user

### Implementation Details

#### Discord Bot Integration
- Added `!link` command and `/link` slash command
- Implemented secure token generation and storage
- Set up DM system for sending verification links
- Added confirmation messaging

#### Token Management
- Created secure token generation using `secrets` module
- Implemented token storage with expiration times
- Added background task for cleaning up expired tokens
- Set 30-minute expiration time for security

#### Account Verification
- Created verification handler in `web/verification_handler.py`
- Set up token verification process
- Implemented account linking functionality
- Added user notification system for successful links

#### Environment Configuration
- Added `STUDENTHUB_BASE_URL` environment variable
- Added optional `TEST_GUILD_ID` for slash command testing

### Security Considerations
- Tokens are one-time use only and expire after 30 minutes
- Verification links are sent via private DM only
- Token storage is designed to be replaced with a database for production
- Slash commands support ephemeral responses for privacy

### Future Improvements
- Move token storage to a persistent database
- Add rate limiting for token generation
- Implement account unlinking feature
- Add role assignment based on StudentHub profile attributes
- Enhance error handling and retry mechanisms 