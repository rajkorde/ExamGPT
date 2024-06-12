import os
import random
from asyncio import CancelledError
from email import message
from tracemalloc import start
from typing import Any, Dict

from loguru import logger
from telegram import (
    KeyboardButton,
    KeyboardButtonPollType,
    Poll,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.constants import ParseMode
from telegram.ext import (
    ApplicationBuilder,
    CallbackContext,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    PollAnswerHandler,
    PollHandler,
    filters,
)

from examgpt.frontend.chatbot.chat_helper import ChatHelper

# chat = ChatHelper()


# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     await context.bot.send_message(
#         chat_id=update.effective_chat.id, text="I'm an exam gpt bot, please talk to me"
#     )

TOTAL_VOTER_COUNT = 3
TOTAL_QUESTION_COUNT = 3


async def exam(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    exam_id = update.message.text
    if not exam_id:
        message = f"Please provide a valid exam id:{exam_id}"
    else:
        message = chat.initialize(exam_id)
        if message is None:
            message = (
                f"This exam id doesn't exist. Please provide a valid exam id: {exam_id}"
            )
        else:
            message = f"Welcome to {exam_id} exam. Ready for a quiz?"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)


# async def longform(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     question = chat.longform()
#     await context.bot.send_message(
#         chat_id=update.effective_chat.id,
#         text="\n".join([question.question, question.answer]),
#     )


# async def mutliple_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     await context.bot.send_message(
#         chat_id=update.effective_chat.id,
#         text="I help with the multiple choice questions",
#     )


# def start_chat2(token: str) -> None:
#     logger.info("Starting Telegram Chatbot")
#     application = ApplicationBuilder().token(token).build()
#     start_handler = CommandHandler("start", start)
#     exam_handler = CommandHandler("exam", exam)
#     longform_handler = CommandHandler("qa", longform)
#     multiple_choice_handler = CommandHandler("mc", mutliple_choice)

#     application.add_handler(start_handler)
#     application.add_handler(exam_handler)
#     application.add_handler(longform_handler)
#     application.add_handler(multiple_choice_handler)

#     application.run_polling()


## Polling code

QUIZZING = 1

answer_keyboard_mc = [["A", "B", "C", "D"]]
start_keyboard_mc = [["Start", "Cancel"]]
answer_markup_mc = ReplyKeyboardMarkup(answer_keyboard_mc, one_time_keyboard=True)
start_markup_mc = ReplyKeyboardMarkup(start_keyboard_mc, one_time_keyboard=True)


async def start_chat_mc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation and ask user for input."""

    # Parse question count and topic here

    question_count: int = TOTAL_QUESTION_COUNT
    chat_id = update.effective_chat.id

    chat_payload = {
        chat_id: {
            "total_question_count": question_count,
            "asked_question_count": 0,
            "correct_answer_count": 0,
            "last_answer": "X",
        }
    }
    # Keep chat related data under chat_id key
    context.bot_data.update(chat_payload)

    question_str = "question" if question_count == 1 else "questions"  # type: ignore
    reply_text = f"Ready for {question_count} multiple choice {question_str}?"
    await update.message.reply_text(
        reply_text,
        # reply_markup=ReplyKeyboardMarkup.from_button(
        #     KeyboardButton("Start")
        # ),
        reply_markup=start_markup_mc,
    )

    return QUIZZING


async def ask_question_mc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation and ask user for input."""

    chat_id = update.effective_chat.id

    # try catch needed here
    chat_payload = context.bot_data[chat_id]
    logger.info(f"{chat_payload=}")
    last_answer = chat_payload["last_answer"]
    user_answer = update.effective_message.text
    logger.info(f"{last_answer}")

    if not last_answer == "X":
        if user_answer == last_answer:
            await update.message.reply_text("Correct!")
            chat_payload["correct_answer_count"] += 1
            context.bot_data.update({chat_id: chat_payload})
        else:
            await update.message.reply_text("Incorrect!")

    logger.info(f"last message: {update.effective_message.text}")

    if chat_payload["asked_question_count"] == chat_payload["total_question_count"]:
        return await completed_mc(update, context)

    question = "When was I born\nA: 1975\nB: 1976\nC: 1974\nD: 1976\n"
    await update.message.reply_text(
        question,
        reply_markup=answer_markup_mc,
    )

    chat_payload["asked_question_count"] += 1
    chat_payload["last_answer"] = "A"

    context.bot_data.update({chat_id: chat_payload})

    return QUIZZING


# async def poll_handler_mc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Handle answer to the poll"""

#     logger.info(update)
#     logger.info(update.poll)
#     if update.poll.is_closed:
#         return
#     poll = update.poll
#     poll_id = poll.id

#     # need try catch here
#     poll_data = context.bot_data.get(poll_id)
#     if not poll_data:
#         raise Exception("Could not find poll data")

#     chat_id = poll_data["chat_id"]
#     message_id = poll_data["message_id"]

#     user_answer = [option.text for option in poll.options if option.voter_count > 0][0]
#     correct_answer = poll.correct_option_id

#     logger.info(f"{user_answer=}")
#     logger.info(f"{correct_answer=}")

#     logger.info(f"{update.poll.total_voter_count=}")
#     logger.info(context.bot_data[chat_id])
#     await context.bot.stop_poll(chat_id, message_id)


# async def poll_answer_handler_mc(
#     update: Update, context: ContextTypes.DEFAULT_TYPE
# ) -> None:
#     # user_answer = [option.text for option in poll.options if option.voter_count > 0][0]
#     # correct_answer = poll.correct_option_id

#     # logger.info(f"{user_answer=}")
#     # logger.info(f"{correct_answer=}")
#     chat_id = update.effective_chat.id

#     update.poll_answer.option_ids
#     update.poll_answer


async def completed_mc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = update.effective_chat.id

    # try catch needed here
    chat_payload = context.bot_data[chat_id]
    correct = chat_payload["correct_answer_count"]
    total = chat_payload["total_question_count"]
    reply_text = f"You got {correct} out of {total} right!"

    await update.message.reply_text(reply_text)

    return ConversationHandler.END


async def cancel_mc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_text = "Quiz Cancelled."
    await update.message.reply_text(reply_text)

    return ConversationHandler.END


def main() -> None:
    token = os.environ["TG_BOT_TOKEN"]

    # QUIZ_STARTED, QUIZZING = range(2)

    mc_handler = ConversationHandler(
        entry_points=[CommandHandler("mc", start_chat_mc)],
        states={
            QUIZZING: [
                MessageHandler(
                    filters.Regex("^Start|A|B|C|D$"),
                    ask_question_mc,
                )
            ]
        },
        fallbacks=[CommandHandler("Cancel", cancel_mc)],
    )

    application = ApplicationBuilder().token(token).build()
    # application.add_handler(PollHandler(receive_quiz_answer))

    application.add_handler(mc_handler)
    # application.add_handler(PollHandler(poll_handler_mc))
    # application.add_handler(PollAnswerHandler(poll_answer_handler_mc))
    # application.add_handler(PollHandler(handle_answer_mc))

    logger.info("Starting App")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
