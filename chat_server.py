import os
import random
from asyncio import CancelledError
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


def start_chat2(token: str) -> None:
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
    logger.info(answer)
    answered_poll = context.bot_data[answer.poll_id]
    logger.info(answered_poll)

    try:
        questions = answered_poll["questions"]
    except KeyError:
        logger.warning("Unknown poll")
        return

    selected_options = answer.option_ids
    logger.info(selected_options)
    answer_string = ""

    for question_id in selected_options:
        if question_id != selected_options[-1]:
            answer_string += questions[question_id] + " and "
        else:
            answer_string += questions[question_id]

    logger.info(answer_string)

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
    logger.info(actual_poll)
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
        question="How many eggs do you need for a cake?",
        options=questions,
        type=Poll.QUIZ,
        correct_option_id=2,
    )

    logger.info(update.poll)
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
    logger.info(update.poll)
    # logger.info(context.bot_data)
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


CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)

reply_keyboard = [
    ["Age", "Favourite colour"],
    ["Number of siblings", "Something else..."],
    ["Done"],
]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


def facts_to_str(user_data: Dict[str, str]) -> str:
    """Helper function for formatting the gathered user info."""
    facts = [f"{key} - {value}" for key, value in user_data.items()]
    return "\n".join(facts).join(["\n", "\n"])


async def start_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation and ask user for input."""
    await update.message.reply_text(
        "Hi! My name is Doctor Botter. I will hold a more complex conversation with you. "
        "Why don't you tell me something about yourself?",
        reply_markup=markup,
    )

    return CHOOSING


async def regular_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Ask the user for info about the selected predefined choice."""
    text = update.message.text
    context.user_data["choice"] = text
    await update.message.reply_text(
        f"Your {text.lower()}? Yes, I would love to hear about that!"
    )

    return TYPING_REPLY


async def custom_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Ask the user for a description of a custom category."""
    await update.message.reply_text(
        'Alright, please send me the category first, for example "Most impressive skill"'
    )

    return TYPING_CHOICE


async def received_information(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Store info provided by user and ask for the next category."""
    user_data = context.user_data
    text = update.message.text
    category = user_data["choice"]
    user_data[category] = text
    del user_data["choice"]

    await update.message.reply_text(
        "Neat! Just so you know, this is what you already told me:"
        f"{facts_to_str(user_data)}You can tell me more, or change your opinion"
        " on something.",
        reply_markup=markup,
    )

    return CHOOSING


async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Display the gathered info and end the conversation."""
    user_data = context.user_data
    if "choice" in user_data:
        del user_data["choice"]

    await update.message.reply_text(
        f"I learned these facts about you: {facts_to_str(user_data)}Until next time!",
        reply_markup=ReplyKeyboardRemove(),
    )

    user_data.clear()
    return ConversationHandler.END


async def start_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation and ask user for input."""
    Question = """Who is the prime minister of India?\n"""
    await update.message.reply_text(
        "Hi! My name is Doctor Botter. I will hold a more complex conversation with you. "
        "Why don't you tell me something about yourself?",
        reply_markup=markup,
    )

    return CHOOSING


# GENDER, PHOTO, LOCATION, BIO = range(4)


# async def start_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Starts the conversation and asks the user about their gender."""
#     reply_keyboard = [["Boy", "Girl", "Other"]]

#     await update.message.reply_text(
#         "Hi! My name is Professor Bot. I will hold a conversation with you. "
#         "Send /cancel to stop talking to me.\n\n"
#         "Are you a boy or a girl?",
#         reply_markup=ReplyKeyboardMarkup(
#             reply_keyboard,
#             one_time_keyboard=True,
#             input_field_placeholder="Boy or Girl?",
#         ),
#     )

#     return GENDER


# async def gender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Stores the selected gender and asks for a photo."""
#     user = update.message.from_user
#     logger.info("Gender of %s: %s", user.first_name, update.message.text)
#     await update.message.reply_text(
#         "I see! Please send me a photo of yourself, "
#         "so I know what you look like, or send /skip if you don't want to.",
#         reply_markup=ReplyKeyboardRemove(),
#     )

#     return PHOTO
#     return PHOTO


# async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     user = update.message.from_user
#     photo_file = await update.message.photo[-1].get_file()
#     await photo_file.download_to_drive("user_photo.jpg")
#     logger.info("Photo of %s: %s", user.first_name, "user_photo.jpg")
#     await update.message.reply_text(
#         "Gorgeous! Now, send me your location please, or send /skip if you don't want to."
#     )

#     return LOCATION


# async def skip_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Skips the photo and asks for a location."""
#     user = update.message.from_user
#     logger.info("User %s did not send a photo.", user.first_name)
#     await update.message.reply_text(
#         "I bet you look great! Now, send me your location please, or send /skip."
#     )

#     return LOCATION


# async def location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Stores the location and asks for some info about the user."""
#     user = update.message.from_user
#     user_location = update.message.location
#     logger.info(
#         "Location of %s: %f / %f",
#         user.first_name,
#         user_location.latitude,
#         user_location.longitude,
#     )
#     await update.message.reply_text(
#         "Maybe I can visit you sometime! At last, tell me something about yourself."
#     )

#     return BIO


# async def skip_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Skips the location and asks for info about the user."""
#     user = update.message.from_user
#     logger.info("User %s did not send a location.", user.first_name)
#     await update.message.reply_text(
#         "You seem a bit paranoid! At last, tell me something about yourself."
#     )

#     return BIO


# async def bio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Stores the info about the user and ends the conversation."""
#     user = update.message.from_user
#     logger.info("Bio of %s: %s", user.first_name, update.message.text)
#     await update.message.reply_text("Thank you! I hope we can talk again some day.")

#     return ConversationHandler.END


# async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Cancels and ends the conversation."""
#     user = update.message.from_user
#     logger.info("User %s canceled the conversation.", user.first_name)
#     await update.message.reply_text(
#         "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
#     )

#     return ConversationHandler.END

ASK_QUESTION, HANDLE_ANSWER, COMPLETED = range(3)

answer_keyboard_mc = [["A", "B", "C", "D"]]
start_keyboard_mc = [["Start"]]
answer_markup_mc = ReplyKeyboardMarkup(answer_keyboard_mc, one_time_keyboard=True)
start_markup_mc = ReplyKeyboardMarkup(start_keyboard_mc, one_time_keyboard=True)


async def start_chat_mc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation and ask user for input."""

    question_count = TOTAL_QUESTION_COUNT

    context.user_data["total_question_count"] = question_count
    context.user_data["asked_question_count"] = 0
    context.user_data["correct_answer_count"] = 0
    question_str = "question" if question_count == 1 else "questions"
    reply_text = f"Ready for {question_count} multiple choice {question_str}?"

    await update.message.reply_text(
        reply_text,
        # reply_markup=ReplyKeyboardMarkup.from_button(
        #     KeyboardButton("Start")
        # ),
        reply_markup=start_markup_mc,
    )

    return ASK_QUESTION


async def ask_question_mc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation and ask user for input."""

    question = "When was I born\nA: 1975\nB: 1976\nC: 1974\nD: 1976\n"
    await update.message.reply_text(
        question,
        # reply_markup=ReplyKeyboardMarkup.from_button(
        #     KeyboardButton("Start")
        # ),
        reply_markup=answer_markup_mc,
    )

    return HANDLE_ANSWER


async def handle_answer_mc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation and ask user for input."""

    context.user_data["asked_question_count"] += 1

    is_correct = random.choice([True, False])
    if is_correct:
        reply_text = "Correct!"
        context.user_data["correct_answer_count"] += 1
    else:
        reply_text = "Incorrect!"
    await update.message.reply_text(
        reply_text,
        # reply_markup=ReplyKeyboardMarkup.from_button(
        #     KeyboardButton("Start")
        # ),
        # reply_markup=answer_markup_mc
    )
    if (
        context.user_data["asked_question_count"]
        == context.user_data["total_question_count"]
    ):
        state = await completed_mc(update, context)

    else:
        state = await ask_question_mc(update, context)
    return state


async def completed_mc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    correct = context.user_data["correct_answer_count"]
    total = context.user_data["total_question_count"]
    reply_text = f"You got {correct} out of {total} right!"
    await update.message.reply_text(reply_text)

    return ConversationHandler.END


async def cancel_mc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_text = "Quiz Cancelled."
    await update.message.reply_text(reply_text)

    return ConversationHandler.END


# States for the conversation
TEST_CHOOSING, TEST_TYPING_REPLY = range(2)


async def test_start(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Hi! I'm a bot. What's your name?")
    return CHOOSING


async def test_choosing(update: Update, context: CallbackContext):
    user_data = context.user_data
    user_data["choice"] = update.message.text
    await update.message.reply_text(f'Nice to meet you, {user_data["choice"]}!')

    # Immediately transition to TYPING_REPLY state and perform an action
    return test_typing_reply(update, context)


async def test_typing_reply(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Please type your reply.")

    # Immediately execute some action on state change without waiting for user input
    do_something_immediate()

    return TYPING_REPLY


def do_something_immediate():
    print("Action performed immediately on state change!")


async def test_received_information(update: Update, context: CallbackContext) -> int:
    user_data = context.user_data
    text = update.message.text
    user_data["reply"] = text
    await update.message.reply_text(f"I received your reply: {text}")
    return ConversationHandler.END


async def test_cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Conversation cancelled.")
    return ConversationHandler.END


def main() -> None:
    token = os.environ["TG_BOT_TOKEN"]
    # start_chat(token)

    # mc_handler = ConversationHandler(
    #     entry_points=[CommandHandler("start_mc", start_mc)],
    # )

    # conv_handler = ConversationHandler(
    #     entry_points=[CommandHandler("start_chat", start_chat)],
    #     states={
    #         GENDER: [MessageHandler(filters.Regex("^(Boy|Girl|Other)$"), gender)],
    #         PHOTO: [
    #             MessageHandler(filters.PHOTO, photo),
    #             CommandHandler("skip", skip_photo),
    #         ],
    #         LOCATION: [
    #             MessageHandler(filters.LOCATION, location),
    #             CommandHandler("skip", skip_location),
    #         ],
    #         BIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, bio)],
    #     },
    #     fallbacks=[CommandHandler("cancel", cancel)],
    # )

    # conv_handler = ConversationHandler(
    #     entry_points=[CommandHandler("start_chat", start_chat)],
    #     states={
    #         CHOOSING: [
    #             MessageHandler(
    #                 filters.Regex("^(Age|Favourite colour|Number of siblings)$"),
    #                 regular_choice,
    #             ),
    #             MessageHandler(filters.Regex("^Something else...$"), custom_choice),
    #         ],
    #         TYPING_CHOICE: [
    #             MessageHandler(
    #                 filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")),
    #                 regular_choice,
    #             )
    #         ],
    #         TYPING_REPLY: [
    #             MessageHandler(
    #                 filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")),
    #                 received_information,
    #             )
    #         ],
    #     },
    #     fallbacks=[MessageHandler(filters.Regex("^Done$"), done)],
    # )

    ASK_QUESTION, HANDLE_ANSWER, COMPLETED = range(3)

    mc_handler = ConversationHandler(
        entry_points=[CommandHandler("start_chat_mc", start_chat_mc)],
        states={
            ASK_QUESTION: [
                MessageHandler(
                    filters.Regex("^Start$") | (filters.TEXT & ~(filters.COMMAND)),
                    ask_question_mc,
                )
            ],
            HANDLE_ANSWER: [
                MessageHandler(filters.Regex("^A|B|C|D$"), handle_answer_mc)
            ],
            COMPLETED: [
                MessageHandler(
                    (filters.TEXT & ~(filters.COMMAND)),
                    completed_mc,
                )
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_mc)],
    )

    test_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("test_start", test_start)],
        states={
            TEST_CHOOSING: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, test_choosing)
            ],
            TEST_TYPING_REPLY: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, test_received_information
                )
            ],
        },
        fallbacks=[CommandHandler("cancel", test_cancel)],
    )

    application = ApplicationBuilder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("poll", poll))
    application.add_handler(CommandHandler("quiz", quiz))
    application.add_handler(CommandHandler("preview", preview))
    application.add_handler(CommandHandler("help", help_handler))
    application.add_handler(MessageHandler(filters.POLL, receive_poll))
    application.add_handler(PollAnswerHandler(receive_poll_answer))
    application.add_handler(PollHandler(receive_quiz_answer))
    application.add_handler(mc_handler)
    application.add_handler(test_conv_handler)

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
