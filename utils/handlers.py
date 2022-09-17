import telegram


from telegram import (
    ReplyKeyboardMarkup,
)

from telegram.ext import (
    ConversationHandler,
    Filters,
    MessageHandler,
)
from utils.keyboard import create_markup
from utils.message_strings import *
from utils.states import *


def maxNumberReached(update, context):
    update.message.reply_text(
        "Hey! Thanks for your interest, but it seems that the maximum number of users has been reached."
    )
    return ConversationHandler.END


def botStopped(update, context):
    update.message.reply_text(
        "The airdrop has been completed. Thanks for you interest."
    )
    return ConversationHandler.END


def botPaused(update, context):
    update.message.reply_text(
        "The airdrop has been temporarily paused, please try again later",
        reply_markup=ReplyKeyboardMarkup([["/start"]]),
    )
    return ConversationHandler.END


def follow_telegram(update, context):
    update.message.reply_text(
        text=MAKE_SURE_TELEGRAM, parse_mode=telegram.ParseMode.MARKDOWN
    )
    update.message.reply_text(
        text='Please click on "Done" to proceed',
        parse_mode=telegram.ParseMode.MARKDOWN,
        reply_markup=create_markup([["Done"], ["Cancel"]]),
    )

    return FOLLOW_TWITTER


def cancel(update, context) -> int:
    """Cancels and ends the conversation."""
    update.message.reply_text("Goodbye!", reply_markup=create_markup([["/start"]]))
    return ConversationHandler.END


def startAgain(update, context) -> int:
    """Cancels and ends the conversation."""
    update.message.reply_text(
        "An error occured, please start the bot again.",
        reply_markup=create_markup([["/start"]]),
    )
    return ConversationHandler.END


cancelHandler = MessageHandler(Filters.regex("^Cancel$"), cancel)
