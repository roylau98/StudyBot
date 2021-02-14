from telegram import (
    ReplyKeyboardRemove,
    Update,
    Bot,
)
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
    CallbackQueryHandler,
)
from database import DataBase
import logging
global G_QUESTION_INPUT, G_MOD_INPUT, questions, BOT, G_MOD_INDEX_INPUT, G_ANSWER_INPUT

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
) # Enable logging

BOT = Bot("TOKEN")
logger = logging.getLogger(__name__)
BUTTON, QUESTION, QUESTION1, QUESTION2, ASSIST, ASSIST1, ASSIST2 = range(7)


def start(update: Update, context: CallbackContext) -> None:

    update.message.reply_text(
        "Hey there! I'm Professor tortoise, "
        "here to help connect you with fellow students. \n"
        "If you ever want to stop our conversation, "
        "please type /cancel to stop this conversation.\n\n"
        "So, are you here to ask questions or here to assist others? \n "
        "Type '/question' or '/assist' ",
        reply_markup=ReplyKeyboardRemove(),
    )
    return BUTTON


def button(update: Update, context: CallbackContext) -> None:
    text_input = update.message.text

    if text_input == "/question\n":
        return QUESTION

    if text_input == "/assist\n":
        update.message.reply_text(
            "Thank you for assisting others! These modules currently have unanswered questions.",
            reply_markup=ReplyKeyboardRemove(),
        )
        return ASSIST


def question(update: Update, context: CallbackContext) -> int:

    update.message.reply_text(
        "For starters, could you let us know which module your question is from?\n"
        "For example: type out 'CZ1107' or 'CB1131' and ensure it is in upper-case",
        reply_markup=ReplyKeyboardRemove(),
    )
    return QUESTION1


def question1(update: Update, context: CallbackContext) -> int:

    user = update.message.from_user
    global G_MOD_INPUT
    G_MOD_INPUT = update.message.text
    db.add_users(user.username, G_MOD_INPUT)
    update.message.reply_text(
        "What question do you need help with?",
    )
    return QUESTION2


def question2(update: Update, context: CallbackContext) -> int:

    global G_QUESTION_INPUT
    G_QUESTION_INPUT = update.message.text
    chat_ID = str(update.message.chat_id)

    update.message.reply_text(
        "Thanks for the question!\n"
        "We will reply to you once someone answers your question!\n"
    )
    db.add_questions(chat_ID, G_QUESTION_INPUT, G_MOD_INPUT)
    return ConversationHandler.END


def assist(update: Update, context: CallbackContext) -> int:

    update.message.reply_text(
        "You've chosen to answer the questions.\n\n "
        "Here are the list of questions sorted by their modules.",
        reply_markup=ReplyKeyboardRemove(),
    )
    global questions
    questions = db.filter_questions_unanswered()
    string = ""

    for mods in questions:
        string = string + mods + "\n"
        question_List = questions[mods]
        for i in range(1, len(question_List) + 1):
            string += str(i) + ":" + question_List[i - 1] + "\n"

    update.message.reply_text(string)
    update.message.reply_text(
        "Which question do you require help with? \n"
        "Reply in this format mods-index (e.g. CZ1107-1)"
    )
    return ASSIST1


def assist1(update: Update, context: CallbackContext) -> int:

    global G_MOD_INDEX_INPUT
    G_MOD_INDEX_INPUT = str(update.message.text)
    splitString = G_MOD_INDEX_INPUT.split("-")
    idx = int(splitString[-1])

    try:
        G_MOD_INDEX_INPUT = questions[splitString[0]][idx - 1]
        print(G_MOD_INDEX_INPUT)
        update.message.reply_text("Okay! What's your answer?")
        return ASSIST2

    except (KeyError, IndexError):
        update.message.reply_text("Please enter a valid format!")
        return ASSIST1


def assist2(update: Update, context: CallbackContext) -> int:

    global G_ANSWER_INPUT
    G_ANSWER_INPUT = str(update.message.text)
    db.add_answer(G_MOD_INDEX_INPUT, G_ANSWER_INPUT)
    chat_ID_reply = db.search_answer(G_MOD_INDEX_INPUT)
    BOT.sendMessage(chat_id=chat_ID_reply, text=G_ANSWER_INPUT)

    update.message.reply_text(
        "Alright, got it! Thanks",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


# if users enters /cancel command
def cancel(update: Update, context: CallbackContext) -> int:

    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        "Good-bye! Hope this was of some help to you! :-)",
        reply_markup=ReplyKeyboardRemove(),
    )

    return ConversationHandler.END


def main():
    updater = Updater("TOKEN")

    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            BUTTON: [MessageHandler(Filters.text & ~Filters.command, button)],
            QUESTION: [MessageHandler(Filters.text & ~Filters.command, question)],
            QUESTION1: [MessageHandler(Filters.text & ~Filters.command, question1)],
            QUESTION2: [MessageHandler(Filters.text & ~Filters.command, question2)],
            ASSIST: [MessageHandler(Filters.text & ~Filters.command, assist)],
            ASSIST1: [MessageHandler(Filters.text & ~Filters.command, assist1)],
            ASSIST2: [MessageHandler(Filters.text & ~Filters.command, assist2)],
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            CommandHandler("question", question),
            CommandHandler("assist", assist),
        ],
    )

    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(CallbackQueryHandler(button))

    # Start the Bot
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    db = DataBase("Questions.db")
    main()
    db.close_connection()
