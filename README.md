# StudentHub Discord Bot

An AI-powered Discord bot designed to assist members of the StudentHub Discord server by answering questions and providing guidance about the server and StudentHub. The bot also enables account linking between Discord users and their StudentHub profiles.

## Features

- Answers questions about StudentHub and the Discord server
- Guides users on where to post different types of inquiries
- Pulls knowledge from Google Docs as a knowledge base
- Uses OpenAI's API for natural language responses
- Account linking between Discord and StudentHub profiles

## Implementation Summary

The StudentHub Discord Bot consists of four main components:

1. **Discord Bot Interface** (`bot/discord_client.py`):
   - Handles Discord events and command processing
   - Processes the `!ask` command from users
   - Manages bot permissions and communication
   - Provides account linking with one-time verification tokens

2. **AI Response Engine** (`ai/openai_client.py`):
   - Integrates with OpenAI's Chat API (GPT-3.5-Turbo model)
   - Generates natural language responses to user queries
   - Incorporates knowledge base context into prompts

3. **Knowledge Base** (`knowledge/gdocs_client.py`):
   - Retrieves content from Google Docs via the Google API
   - Implements simple keyword-based search for relevant information
   - Maintains a cache to reduce API calls

4. **Account Verification** (`web/verification_handler.py`):
   - Handles the verification process for account linking
   - Verifies one-time tokens and links accounts
   - Provides utility functions for account management

For a detailed development log, check [DEVELOPMENT_LOG.md](./DEVELOPMENT_LOG.md).

## Setup

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill in your credentials:
   ```
   cp .env.example .env
   ```
4. Set up Google API credentials (see below)
5. Run the bot:
   ```
   python main.py
   ```

## Environment Variables

The following environment variables need to be set in the `.env` file:

- `DISCORD_TOKEN`: Your Discord bot token
- `OPENAI_API_KEY`: Your OpenAI API key
- `GOOGLE_API_CREDENTIALS`: Path to your Google API credentials JSON file
- `GOOGLE_DOC_IDS`: Comma-separated list of Google Doc IDs to use as knowledge base
- `STUDENTHUB_BASE_URL`: Base URL for your StudentHub website (for account linking)
- `TEST_GUILD_ID`: (Optional) Discord server ID for testing slash commands

## Google API Setup

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable the Google Drive API and Google Docs API
4. Create credentials (OAuth 2.0 client ID)
5. Download the credentials JSON file and save it
6. Reference the path to this file in your `.env` file

## Discord Bot Setup

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Navigate to the "Bot" tab and click "Add Bot"
4. Under "Privileged Gateway Intents", enable:
   - Message Content Intent
   - Server Members Intent
5. Copy the bot token and add it to your `.env` file
6. Use the OAuth2 URL Generator to generate an invite link with the following permissions:
   - Read Messages/View Channels
   - Send Messages
   - Embed Links
   - Attach Files
   - Read Message History
   - Add Reactions
7. Invite the bot to your server using the generated link

## Usage

### Asking Questions

In the Discord server, use the `!ask` command followed by your question:

```
!ask What channel should I post my homework question in?
```

### Linking Accounts

To link your Discord account to your StudentHub profile, use either the `!link` command or the `/link` slash command:

```
!link
```

or

```
/link
```

The bot will send you a DM with a one-time verification link. Click the link to go to the StudentHub website, log in (if not already logged in), and complete the account linking process.

## Project Structure

- `main.py`: Entry point for the bot
- `bot/`: Discord bot implementation
- `ai/`: OpenAI integration
- `knowledge/`: Google Docs knowledge base integration
- `web/`: Web-related functionality, including account verification
- `DEVELOPMENT_LOG.md`: Detailed development history and implementation notes

## Deployment

For production deployment, consider:
- Using a process manager like PM2 to ensure the bot stays running
- Setting up the bot as a system service
- Deploying to a cloud service
- Setting up proper monitoring and logging
- Using a database for storing tokens and linked accounts

## Security Considerations

- Tokens are one-time use only and expire after 30 minutes
- Verification links are sent via private DM only
- Token storage is designed to be replaced with a database for production
- Slash commands support ephemeral responses for privacy

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT 