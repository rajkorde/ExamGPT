import os

from loguru import logger
from telegram import (
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from examgpt.frontend.chatbot.chat_helper import ChatHelper, CommandArgs, command_parser

chat = ChatHelper()
chat.initialize("innocent-few")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="Welcome to ExamGPT!"
    )


TOTAL_QUESTION_COUNT = 2


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


QUIZZING = 1

answer_keyboard_mc = [["A", "B", "C", "D"]]
start_keyboard_mc = [["Start", "Cancel"]]
answer_markup_mc = ReplyKeyboardMarkup(answer_keyboard_mc, one_time_keyboard=True)
start_markup_mc = ReplyKeyboardMarkup(start_keyboard_mc, one_time_keyboard=True)


async def start_mc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation and ask user for input."""

    # Parse question count and topic here
    if context.args:
        try:
            command = command_parser(context.args)
        except Exception:
            reply_text = (
                "Incorrect format. Correct format is /mc [question_count] [topic]"
            )
            await update.message.reply_text(reply_text)
            return ConversationHandler.END
    else:
        command = CommandArgs(question_count=1, question_topic=None)

    print(f"Question Count:{command.question_count}")
    print(f"Question Topic:{command.question_topic}")

    return ConversationHandler.END

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

    context.bot_data.update(chat_payload)

    question_str = "question" if question_count == 1 else "questions"  # type: ignore
    reply_text = f"Ready for {question_count} multiple choice {question_str}\n/cancel anytime to cancel quiz.?"

    if not update.message:
        logger.warning("Update does not have a message object")
        return await cancel_mc(update, context)

    await update.message.reply_text(
        reply_text,
        reply_markup=start_markup_mc,
    )

    return QUIZZING


async def quiz_mc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation and ask user for input."""

    chat_id = update.effective_chat.id

    # try catch needed here
    chat_payload = context.bot_data[chat_id]
    logger.info(f"{chat_payload=}")
    last_answer = chat_payload["last_answer"]
    user_answer = update.effective_message.text

    if not last_answer == "X":
        if user_answer == last_answer:
            await update.message.reply_text("Correct!")
            chat_payload["correct_answer_count"] += 1
            context.bot_data.update({chat_id: chat_payload})
        else:
            await update.message.reply_text(
                f"Incorrect! The correct answer is {last_answer}"
            )

    if chat_payload["asked_question_count"] == chat_payload["total_question_count"]:
        return await completed_mc(update, context)

    # question = "When was I born\nA: 1975\nB: 1976\nC: 1974\nD: 1976\n"
    # await update.message.reply_text(
    #     question,
    #     reply_markup=answer_markup_mc,
    # )

    multiple_choice_qa = chat.multiple_choice()
    if not multiple_choice_qa:
        logger.error("No multiple choice questions found.")
        return await error(update, context)

    question = multiple_choice_qa.question
    choices = "\n".join([f"{k}: {v}" for k, v in multiple_choice_qa.choices.items()])

    await update.message.reply_text(
        f"{question}\n{choices}",
        reply_markup=answer_markup_mc,
    )

    chat_payload["asked_question_count"] += 1
    chat_payload["last_answer"] = multiple_choice_qa.answer

    context.bot_data.update({chat_id: chat_payload})

    return QUIZZING


async def completed_mc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = update.effective_chat.id

    # try catch needed here
    chat_payload = context.bot_data[chat_id]
    correct = chat_payload["correct_answer_count"]
    total = chat_payload["total_question_count"]
    reply_text = f"You got {correct} out of {total} right!"

    await update.message.reply_text(reply_text, reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


async def cancel_mc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_text = "Quiz Cancelled."
    await update.message.reply_text(reply_text, reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_text = "Something went wrong. Please try again."
    await update.message.reply_text(reply_text, reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def main() -> None:
    token = os.environ["TG_BOT_TOKEN"]

    mc_handler = ConversationHandler(
        entry_points=[CommandHandler("mc", start_mc)],
        states={
            QUIZZING: [
                MessageHandler(filters.Regex("^(Cancel)$"), cancel_mc),
                MessageHandler(
                    filters.Regex("^(Start|A|B|C|D)$") & ~filters.COMMAND,
                    quiz_mc,
                ),
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel_mc)],
    )

    application = ApplicationBuilder().token(token).build()
    application.add_handler(mc_handler)
    application.add_handler(CommandHandler("start", start))

    logger.info("Starting App")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
