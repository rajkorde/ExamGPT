import sys
from pathlib import Path

root_path = str(Path(__file__).parent.parent.parent.parent)
if root_path not in sys.path:
    sys.path.append(root_path)

print(sys.path)

from loguru import logger  # noqa: E402
from telegram import Update  # noqa: E402
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes  # noqa: E402

from examgpt.frontend.chatbot.chat_helper import ChatHelper  # noqa: E402
from examgpt.storage.files import FileStorage  # noqa: E402


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="I'm an exam gpt bot, please talk to me"
    )


async def longform(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="I help with longform questions"
    )


async def mutliple_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="I help with the multiple choice questions",
    )


def start_chat(token: str) -> None:
    # Instantiate all needed classes

    # chat_helper = ChatHelper(FileStorage("Temp"))

    logger.info("Starting Telegram Chatbot")
    application = ApplicationBuilder().token(token).build()
    start_handler = CommandHandler("start", start)
    longform_handler = CommandHandler("qa", longform)
    multiple_choice_handler = CommandHandler("mc", mutliple_choice)

    application.add_handler(start_handler)
    application.add_handler(longform_handler)
    application.add_handler(multiple_choice_handler)

    application.run_polling()
