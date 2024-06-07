import os
from typing import Any

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
    CommandHandler,
    ContextTypes,
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


async def longform(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    question = chat.longform()
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="\n".join([question.question, question.answer]),
    )


async def mutliple_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="I help with the multiple choice questions",
    )


def start_chat(token: str) -> None:
    logger.info("Starting Telegram Chatbot")
    application = ApplicationBuilder().token(token).build()
    start_handler = CommandHandler("start", start)
    exam_handler = CommandHandler("exam", exam)
    longform_handler = CommandHandler("qa", longform)
    multiple_choice_handler = CommandHandler("mc", mutliple_choice)

    application.add_handler(start_handler)
    application.add_handler(exam_handler)
    application.add_handler(longform_handler)
    application.add_handler(multiple_choice_handler)

    application.run_polling()


## Polling code

TOTAL_VOTER_COUNT = 3


def log(o: Any) -> None:
    logger.info(f"{o=}")
    logger.info(type(o))


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Inform user about what this bot can do"""
    await update.message.reply_text(
        "Please select /poll to get a Poll, /quiz to get a Quiz or /preview"
        " to generate a preview for your poll"
    )


async def poll(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    questions = ["Good", "Really good", "Fantastic", "Great"]

    message = await context.bot.send_poll(
        update.effective_chat.id,
        "How are you?",
        questions,
        is_anonymous=False,
        allows_multiple_answers=True,
    )

    payload = {
        message.poll.id: {
            "questions": questions,
            "message_id": message.message_id,
            "chat_id": update.effective_chat.id,
            "answers": 0,
        }
    }

    context.bot_data.update(payload)


async def receive_poll_answer(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    answer = update.poll_answer
    log(answer)
    answered_poll = context.bot_data[answer.poll_id]
    log(answered_poll)

    try:
        questions = answered_poll["questions"]
    except KeyError:
        logger.warning("Unknown poll")
        return

    selected_options = answer.option_ids
    log(selected_options)
    answer_string = ""

    for question_id in selected_options:
        if question_id != selected_options[-1]:
            answer_string += questions[question_id] + " and "
        else:
            answer_string += questions[question_id]

    log(answer_string)

    await context.bot.send_message(
        answered_poll["chat_id"],
        f"{update.effective_user.mention_html()} feels {answer_string}!",
        parse_mode=ParseMode.HTML,
    )

    answered_poll["answers"] += 1
    if answered_poll["answers"] == TOTAL_VOTER_COUNT:
        await context.bot.stop_poll(
            answered_poll["chat_id"], answered_poll["message_id"]
        )


async def receive_poll(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    "On receiving polls, reply to it by closed poll copying the received poll"
    actual_poll = update.effective_message.poll
    log(actual_poll)
    # Only need to set the question and options, since all other parameters don't matter for
    # a closed poll
    await update.effective_message.reply_poll(
        question=actual_poll.question,
        options=[o.text for o in actual_poll.options],
        is_closed=True,
        reply_markup=ReplyKeyboardRemove(),
    )


async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    "send a predefined poll"
    questions = ["1", "2", "4", "20"]
    message = await update.effective_message.reply_poll(
        question="How many eggs do you need for a cake",
        options=questions,
        type=Poll.QUIZ,
        correct_option_id=2,
    )

    log(message)
    payload = {
        message.poll.id: {
            "chat_id": update.effective_chat.id,
            "message_id": message.id,
        }
    }

    context.bot_data.update(payload)


async def receive_quiz_answer(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    if update.poll.is_closed:
        return
    if update.poll.total_voter_count == TOTAL_VOTER_COUNT:
        try:
            quiz_data = context.bot_data[update.poll.id]
        except KeyError:
            return
        await context.bot.stop_poll(quiz_data["chat_id"], quiz_data["message_id"])


async def preview(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Ask user to create a poll and display a preview of it"""
    # using this without a type lets the user chooses what he wants (quiz or poll)
    button = [[KeyboardButton("Click", request_poll=KeyboardButtonPollType())]]
    message = "Press the button to let the bot generate a preview for your poll"
    await update.effective_message.reply_text(
        message, reply_markup=ReplyKeyboardMarkup(button, one_time_keyboard=True)
    )


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Display a help message"""
    await update.message.reply_text("Use /quiz, /poll or /preview to test this bot.")


def main() -> None:
    token = os.environ["TG_BOT_TOKEN"]
    # start_chat(token)

    application = ApplicationBuilder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("poll", poll))
    application.add_handler(CommandHandler("quiz", quiz))
    application.add_handler(CommandHandler("preview", preview))
    application.add_handler(CommandHandler("help", help_handler))
    application.add_handler(MessageHandler(filters.POLL, receive_poll))
    application.add_handler(PollAnswerHandler(receive_poll_answer))
    application.add_handler(PollHandler(receive_quiz_answer))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
