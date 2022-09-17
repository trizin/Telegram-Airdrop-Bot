import telegram


from telegram import (
    ReplyKeyboardMarkup,
)

from telegram.ext import (
    ConversationHandler,
    Filters,
    MessageHandler,
)
from utils.keyboard import create_markup, get_reply_keyboard_markup
from utils.message_strings import *
from utils.jokes import getJoke
from utils.states import *
from utils import mongo


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


def loopAnswer(update, context):
    user = update.message.from_user
    info = mongo.getUserInfo(user.id)
    message = update.message.text
    reply = ""
    if message == "💰 Balance":
        refbal = "{:,.2f}".format(info["refCount"] * REFERRAL_REWARD)
        if refbal == "":
            refbal = "0"
        reply = BALANCE_TEXT.replace("IARTBALANCE", AIRDROP_AMOUNT).replace(
            "REFERRALBALANCE", refbal
        )

    if message == "ℹ️ Airdrop Info":
        reply = PROCEED_MESSAGE

    if message == "💸 Withdrawal":
        reply = WITHDRAWAL_TEXT

    if message == "🔗 Ref Link":
        reply = f"""
Here is *your referral link*
[https://t.me/{context.bot.username}?start={user.id}](https://t.me/{context.bot.username}?start={user.id})
"""

    if message == "Quit Airdrop":
        update.message.reply_text(
            "Are you sure want to quit the Airdrop? All your data will be deleted",
            reply_markup=create_markup([["YES"], ["NO"]]),
        )
        return SUREWANTTO

    if message == "💾 My Data":
        name = str(info["name"])
        refbal = "{:,.2f}".format(info["refCount"] * REFERRAL_REWARD)
        balance = BALANCE_TEXT.replace("IARTBALANCE", AIRDROP_AMOUNT).replace(
            "REFERRALBALANCE", refbal
        )
        refferals = str(info["refCount"])
        bep20Address = str(info["bep20"])
        twitterUsername = str(info["twitter_username"])
        reply = f"""
Name: {name}
Referrals: {refferals}
{AIRDROP_NETWORK} address: {bep20Address}
Twitter Username: {twitterUsername}
Balance: {balance}
"""
    if reply == "":
        joke = getJoke()
        joke = joke.split("  -")
        reply = f"""
I'm not sure what you meant, but here is a joke for you!
> {joke[0]}
- {joke[1]}
"""
    update.message.reply_text(
        reply,
        reply_markup=get_reply_keyboard_markup(),
        parse_mode=telegram.ParseMode.MARKDOWN,
    )
    return LOOP


def sureWantTo(update, context):
    user = update.message.from_user
    message = update.message.text
    if message == "YES":
        update.message.reply_text("Goodbye!", reply_markup=create_markup([["/start"]]))
        mongo.users.delete_one({"userId": user.id})
        return ConversationHandler.END

    if message == "NO":
        update.message.reply_text(
            "Oh thanks god, I thought I lost you",
            reply_markup=get_reply_keyboard_markup(),
        )
        return LOOP
