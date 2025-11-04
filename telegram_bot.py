#!/usr/bin/env python
"""
Telegram Bot for Law Assistant
This bot uses the existing RAG system to answer questions about Kazakhstan administrative law.
"""

import os
import sys
import uuid
import logging
from datetime import datetime

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from telegram.constants import ChatAction

# Add the law_assistant directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'law_assistant'))

from rag import rag

# Try to import db module, but continue if not available (for when DB is not set up)
try:
    import db
    DB_AVAILABLE = True
except Exception as e:
    DB_AVAILABLE = False
    print(f"Warning: Database module not available: {e}")
    print("Bot will work without database logging.")

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    welcome_message = f"""
Привет, {user.first_name}! 👋

Я - Law Assistant, помощник по административному праву Республики Казахстан (КоАП РК).

Задайте мне любой вопрос об административном праве, и я постараюсь дать вам точный ответ на основе законодательства.

Например, вы можете спросить:
• "Какой штраф за пересечение двойной сплошной?"
• "Какое наказание за нарушение правил парковки?"
• "Что грозит за превышение скорости?"

Команды:
/start - показать это сообщение
/help - показать справку
/stats - показать статистику последнего ответа

---

Hello, {user.first_name}! 👋

I'm Law Assistant, helping with administrative law of the Republic of Kazakhstan (КоАП РК).

Ask me any question about administrative law, and I'll try to give you an accurate answer based on legislation.
"""
    await update.message.reply_text(welcome_message)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    help_text = """
📚 Помощь / Help

Просто отправьте мне свой вопрос об административном праве Казахстана, и я отвечу на основе КоАП РК.

Just send me your question about Kazakhstan administrative law, and I'll answer based on the КоАП РК.

Команды / Commands:
/start - начать работу сботом / start the bot
/help - показать справку / show help
/stats - статистика последнего ответа / stats of last answer

Примеры вопросов / Example questions:
• Какой штраф за превышение скорости на 20 км/ч?
• Какое наказание за управление автомобилем в нетрезвом состоянии?
• Какие штрафы предусмотрены за нарушение ПДД?
"""
    await update.message.reply_text(help_text)


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send statistics about the last answer."""
    if 'last_stats' not in context.user_data:
        await update.message.reply_text(
            "Статистика недоступна. Сначала задайте вопрос.\n\n"
            "Statistics not available. Ask a question first."
        )
        return

    stats = context.user_data['last_stats']
    stats_text = f"""
📊 Статистика последнего ответа / Last Answer Statistics

🤖 Модель / Model: {stats['model_used']}
⏱️ Время ответа / Response time: {stats['response_time']:.2f} сек / sec
✅ Релевантность / Relevance: {stats['relevance']}
🎯 Токены / Tokens: {stats['total_tokens']}
💰 Стоимость / Cost: ${stats['openai_cost']:.6f}

📝 Объяснение релевантности / Relevance Explanation:
{stats['relevance_explanation']}
"""
    await update.message.reply_text(stats_text)


async def handle_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle user questions and provide answers using the RAG system."""
    question = update.message.text.strip()

    if not question:
        await update.message.reply_text(
            "Пожалуйста, введите вопрос.\n\nPlease enter a question."
        )
        return

    # Show typing action
    await update.message.chat.send_action(ChatAction.TYPING)

    try:
        # Generate conversation ID
        conversation_id = str(uuid.uuid4())

        # Get answer from RAG system
        logger.info(f"Processing question from user {update.effective_user.id}: {question}")
        answer_data = rag(question)

        # Store stats in user context for /stats command
        context.user_data['last_stats'] = answer_data

        # Send answer to user
        answer_text = answer_data['answer']
        await update.message.reply_text(answer_text)

        # Log to database if available
        if DB_AVAILABLE:
            try:
                db.save_conversation(
                    conversation_id=conversation_id,
                    question=question,
                    answer_data=answer_data,
                )
                logger.info(f"Saved conversation {conversation_id} to database")
            except Exception as db_error:
                logger.warning(f"Failed to save to database: {db_error}")

        # Log success
        logger.info(
            f"Successfully answered question. "
            f"Relevance: {answer_data['relevance']}, "
            f"Response time: {answer_data['response_time']:.2f}s"
        )

    except Exception as e:
        logger.error(f"Error processing question: {e}", exc_info=True)
        error_message = f"""
Извините, произошла ошибка при обработке вашего вопроса: {str(e)}

Пожалуйста, попробуйте позже или переформулируйте вопрос.

---

Sorry, an error occurred while processing your question: {str(e)}

Please try again later or rephrase your question.
"""
        await update.message.reply_text(error_message)


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors caused by updates."""
    logger.error(f"Update {update} caused error {context.error}", exc_info=context.error)


def main() -> None:
    """Start the bot."""
    # Get bot token from environment
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')

    if not bot_token:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables!")
        print("\n" + "=" * 60)
        print("ERROR: TELEGRAM_BOT_TOKEN not set!")
        print("=" * 60)
        print("\nPlease set your Telegram Bot Token:")
        print("1. Create a bot with @BotFather on Telegram")
        print("2. Get the token from @BotFather")
        print("3. Set the environment variable:")
        print("   export TELEGRAM_BOT_TOKEN='your-token-here'")
        print("\nOr add it to your .env file:")
        print("   TELEGRAM_BOT_TOKEN=your-token-here")
        print("=" * 60 + "\n")
        sys.exit(1)

    # Check for OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        logger.error("OPENAI_API_KEY not found in environment variables!")
        print("\n" + "=" * 60)
        print("ERROR: OPENAI_API_KEY not set!")
        print("=" * 60)
        print("\nPlease set your OpenAI API Key:")
        print("   export OPENAI_API_KEY='your-key-here'")
        print("\nOr add it to your .env file:")
        print("   OPENAI_API_KEY=your-key-here")
        print("=" * 60 + "\n")
        sys.exit(1)

    # Create the Application
    application = Application.builder().token(bot_token).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_question))

    # Register error handler
    application.add_error_handler(error_handler)

    # Start the Bot
    logger.info("Starting Law Assistant Telegram Bot...")
    print("\n" + "=" * 60)
    print("🤖 Law Assistant Telegram Bot is starting...")
    print("=" * 60)
    if DB_AVAILABLE:
        print("✅ Database logging: ENABLED")
    else:
        print("⚠️  Database logging: DISABLED")
    print("✅ OpenAI API: CONFIGURED")
    print("✅ Telegram Bot: CONFIGURED")
    print("\nBot is now running. Press Ctrl+C to stop.")
    print("=" * 60 + "\n")

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
