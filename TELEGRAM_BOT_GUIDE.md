# Telegram Bot Guide

This guide will help you set up and run the Law Assistant Telegram Bot.

## Overview

The Telegram bot allows users to ask questions about Kazakhstan administrative law (КоАП РК) directly through Telegram. It uses the existing RAG (Retrieval-Augmented Generation) system to provide accurate answers based on the legal database.

## Features

- 🤖 **Interactive Q&A**: Users can ask questions in natural language
- 📊 **Statistics**: View detailed statistics about answers (relevance, tokens, cost)
- 💾 **Database Logging**: Optionally logs conversations to PostgreSQL (if configured)
- 🌐 **Bilingual**: Supports both Russian and English
- ⚡ **Real-time**: Shows typing indicator while processing

## Prerequisites

Before running the Telegram bot, you need:

1. **Python 3.11** installed
2. **Pipenv** for dependency management
3. **OpenAI API Key** - Get it from https://platform.openai.com/api-keys
4. **Telegram Bot Token** - Get it from [@BotFather](https://t.me/BotFather) on Telegram

## Step-by-Step Setup

### 1. Create Your Telegram Bot

1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Send `/newbot` command
3. Follow the instructions:
   - Choose a name for your bot (e.g., "Law Assistant")
   - Choose a username for your bot (must end in 'bot', e.g., "kazakh_law_assistant_bot")
4. Copy the bot token provided by BotFather (looks like: `123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ`)

### 2. Install Dependencies

```bash
# Install pipenv if not already installed
pip install pipenv

# Install all dependencies including python-telegram-bot
pipenv install
```

### 3. Configure API Keys

Edit the `.env` file and add your keys:

```bash
# OpenAI API Key (REQUIRED)
OPENAI_API_KEY=sk-your-actual-openai-key-here

# Telegram Bot Token (REQUIRED)
TELEGRAM_BOT_TOKEN=123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ
```

Alternatively, you can set environment variables directly:

```bash
export OPENAI_API_KEY='sk-your-actual-openai-key-here'
export TELEGRAM_BOT_TOKEN='123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ'
```

### 4. Run the Bot

#### Option A: Using pipenv (Recommended)

```bash
pipenv run python telegram_bot.py
```

#### Option B: Using pipenv shell

```bash
pipenv shell
python telegram_bot.py
```

#### Option C: Direct Python (make sure dependencies are installed)

```bash
python telegram_bot.py
```

### 5. Test Your Bot

1. Open Telegram
2. Search for your bot by username (e.g., @kazakh_law_assistant_bot)
3. Click "Start" or send `/start`
4. Try asking a question, for example:
   - "Какой штраф за пересечение двойной сплошной?"
   - "Какое наказание за превышение скорости?"

## Bot Commands

- `/start` - Start the bot and see welcome message
- `/help` - Show help information
- `/stats` - Show statistics about your last answer

## Testing Without Full Setup

If you want to test the RAG system before setting up the Telegram bot, use the terminal test script:

```bash
pipenv run python terminal_test.py
```

This allows you to test questions directly in your terminal.

## Architecture

```
User Message (Telegram)
    ↓
telegram_bot.py
    ↓
rag.py (RAG System)
    ↓
├── ingest.py (Load & Index Data)
│   └── minsearch.py (TF-IDF Search)
└── OpenAI API (GPT-4o-mini)
    ↓
Answer → User (Telegram)
    ↓
db.py (Optional: Store in PostgreSQL)
```

## Database Integration (Optional)

The bot can optionally log conversations to PostgreSQL:

1. **Start PostgreSQL** (if using Docker):
   ```bash
   docker-compose up postgres
   ```

2. **Initialize Database**:
   ```bash
   pipenv shell
   cd law_assistant
   export POSTGRES_HOST=localhost
   python db_prep.py
   ```

3. **Run the bot** - it will automatically detect and use the database

If the database is not available, the bot will still work but won't log conversations.

## Troubleshooting

### Bot doesn't respond

1. **Check if bot is running**: You should see "Bot is now running" in the terminal
2. **Check API keys**: Make sure both `OPENAI_API_KEY` and `TELEGRAM_BOT_TOKEN` are set correctly
3. **Check bot token**: Verify the token with @BotFather using `/mybots`

### "TELEGRAM_BOT_TOKEN not set" error

- Make sure you've set the token in `.env` file or as an environment variable
- If using `.env`, make sure the file is in the project root directory
- Try setting it directly: `export TELEGRAM_BOT_TOKEN='your-token'`

### "OPENAI_API_KEY not set" error

- Make sure you've set the OpenAI key in `.env` file or as an environment variable
- Get a new key from https://platform.openai.com/api-keys
- Verify you have credits in your OpenAI account

### Import errors

- Run `pipenv install` to install all dependencies
- Make sure you're using Python 3.11: `python --version`

### "Database module not available" warning

- This is normal if you haven't set up PostgreSQL
- The bot will work without database logging
- To enable database logging, follow the "Database Integration" steps above

## Cost Estimation

The bot uses OpenAI's GPT-4o-mini model:

- **Input**: $0.00015 per 1K tokens
- **Output**: $0.0006 per 1K tokens

Typical question costs approximately **$0.001 - $0.005** per answer.

You can see the exact cost of each answer using the `/stats` command.

## Security Best Practices

1. **Never commit** your `.env` file with real API keys
2. **Use environment variables** in production
3. **Rotate keys** regularly
4. **Monitor usage** in OpenAI dashboard
5. **Set spending limits** in your OpenAI account

## Advanced Configuration

### Change the Model

Edit `telegram_bot.py` and modify the `rag()` call:

```python
# Default: gpt-4o-mini
answer_data = rag(question)

# Use GPT-4o instead
answer_data = rag(question, model="gpt-4o")
```

### Customize Responses

Edit `law_assistant/rag.py` to modify:
- `prompt_template`: The system prompt
- `search()`: Adjust boost weights for different fields
- `evaluate_relevance()`: Customize relevance evaluation

### Add More Commands

Add new command handlers in `telegram_bot.py`:

```python
async def your_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Your response")

# Register the handler
application.add_handler(CommandHandler("yourcommand", your_command))
```

## Production Deployment

For production deployment:

1. **Use a process manager**: systemd, supervisor, or pm2
2. **Set up monitoring**: Track errors and uptime
3. **Use webhooks** instead of polling for better performance
4. **Deploy on a VPS**: DigitalOcean, AWS, or similar
5. **Set up logging**: Rotate logs and monitor errors
6. **Add rate limiting**: Prevent abuse

Example systemd service:

```ini
[Unit]
Description=Law Assistant Telegram Bot
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/Law-RAG-pet-project
Environment="OPENAI_API_KEY=your-key"
Environment="TELEGRAM_BOT_TOKEN=your-token"
ExecStart=/usr/local/bin/pipenv run python telegram_bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

## Support

If you encounter issues:

1. Check the bot logs in the terminal
2. Verify all environment variables are set
3. Test with `terminal_test.py` first
4. Check OpenAI API status: https://status.openai.com/
5. Check Telegram Bot API status: https://t.me/BotNews

## License

This bot is part of the Law Assistant project. See the main README.md for license information.
