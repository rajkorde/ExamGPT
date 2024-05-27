from loguru import logger
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

messages = [
    {"role": "system", "content": "You are a helpful assistant that answers questions"}
]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="I'm an exam gpt bot, please talk to me"
    )


def start_chat(token: str) -> None:
    logger.info("Starting Telegram Chatbot")
    application = ApplicationBuilder().token(token).build()
    start_handler = CommandHandler("start", start)

    application.add_handler(start_handler)

    application.run_polling()
