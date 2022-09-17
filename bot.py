import telegram
import logging
import pickle

from utils import mongo
from utils.bot_status import get_bot_status, set_bot_status
from utils.env import *
from utils.message_strings import *
from utils.mongo import users

from telegram import (
    ReplyKeyboardMarkup,
    Update,
)
from bson.json_util import dumps
from multicolorcaptcha import CaptchaGenerator
from utils.jokes import getJoke
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    PicklePersistence,
)


USERINFO = {}  # holds user information
CAPTCHA_DATA = {}


# %% Setting up things
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
persistence = PicklePersistence(filename="conversationbot/conversationbot")
updater = Updater(token=BOT_TOKEN, use_context=True, persistence=persistence)
dispatcher = updater.dispatcher


def maxNumberReached(update, context):
    update.message.reply_text(
        "Hey! Thanks for your interest but it seems like the maximum amount of users has been reached."
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


def checkCaptcha(update, context):
    user = update.message.from_user
    text = update.message.text

    if CAPTCHA_DATA[user.id] != text:
        update.message.reply_text("Invalid captcha!")
        return generateCaptcha(update, context)
    else:
        NAME = getName(user)
        update.message.reply_text(
            text="Correct!", parse_mode=telegram.ParseMode.MARKDOWN
        )
        update.message.reply_text(
            text=WELCOME_MESSAGE.replace("NAME", NAME),
            reply_markup=ReplyKeyboardMarkup([["🚀 Join Airdrop"]]),
            parse_mode=telegram.ParseMode.MARKDOWN,
        )
        CAPTCHA_DATA[user.id] = True
        return PROCEED


def start(update, context):
    user = update.message.from_user
    CAPTCHA_DATA[user.id] = False
    if not user.id in USERINFO:
        USERINFO[user.id] = {}

    refferal = update.message.text.replace("/start", "").strip()
    if refferal != "" and refferal != user.id and "ref" not in USERINFO[user.id]:
        USERINFO[user.id]["ref"] = refferal
        print("Using refferal")
    else:
        USERINFO[user.id]["ref"] = False

    NAME = getName(user)

    if mongo.getUserInfo(user.id) != "":
        update.message.reply_text(
            text="It seems like you have already joined!",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard),
        )
        return LOOP

    count = users.count()
    if count >= MAX_USERS:
        return maxNumberReached(update, context)

    if get_bot_status() == "STOPPED":
        return botStopped(update, context)

    if get_bot_status() == "PAUSED":
        return botPaused(update, context)

    if CAPTCHA_ENABLED == "YES" and CAPTCHA_DATA[user.id] != True:
        return generateCaptcha(update, context)
    else:
        update.message.reply_text(
            text=WELCOME_MESSAGE.replace("NAME", NAME),
            reply_markup=ReplyKeyboardMarkup([["🚀 Join Airdrop"]]),
            parse_mode=telegram.ParseMode.MARKDOWN,
        )
    return PROCEED


def generateCaptcha(update, context):
    user = update.message.from_user
    CAPCTHA_SIZE_NUM = 2
    generator = CaptchaGenerator(CAPCTHA_SIZE_NUM)
    captcha = generator.gen_captcha_image(difficult_level=3)
    image = captcha["image"]
    characters = captcha["characters"]
    CAPTCHA_DATA[user.id] = characters
    filename = f"{user.id}.png"
    image.save(filename, "png")
    photo = open(filename, "rb")
    update.message.reply_photo(photo)
    update.message.reply_text("Please type in the numbers on the image")
    return CAPTCHASTATE


def submit_details(update, context):
    update.message.reply_text(
        text=PROCEED_MESSAGE, parse_mode=telegram.ParseMode.MARKDOWN
    )
    update.message.reply_text(
        text='Please click on "Submit Details" to proceed',
        parse_mode=telegram.ParseMode.MARKDOWN,
        reply_markup=ReplyKeyboardMarkup([["Submit Details"], ["Cancel"]]),
    )
    return FOLLOW_TELEGRAM


def follow_telegram(update, context):
    update.message.reply_text(
        text=MAKE_SURE_TELEGRAM, parse_mode=telegram.ParseMode.MARKDOWN
    )
    update.message.reply_text(
        text='Please click on "Done" to proceed',
        parse_mode=telegram.ParseMode.MARKDOWN,
        reply_markup=ReplyKeyboardMarkup([["Done"], ["Cancel"]]),
    )

    return FOLLOW_TWITTER


def follow_twitter(update, context):
    update.message.reply_text(
        text=FOLLOW_TWITTER_TEXT, parse_mode=telegram.ParseMode.MARKDOWN
    )
    update.message.reply_text(
        text="Type in *your Twitter username* to proceed",
        parse_mode=telegram.ParseMode.MARKDOWN,
        reply_markup=ReplyKeyboardMarkup([["Cancel"]]),
    )
    return SUBMIT_ADDRESS


def submit_address(update, context):
    user = update.message.from_user
    if not user.id in USERINFO:
        return startAgain(update, context)
    USERINFO[user.id].update({"twitter_username": update.message.text.strip()})
    update.message.reply_text(
        text=SUBMIT_BEP20_TEXT,
        parse_mode=telegram.ParseMode.MARKDOWN,
        reply_markup=ReplyKeyboardMarkup([["Cancel"]]),
    )
    return END_CONVERSATION


def getName(user):
    first = user["first_name"]
    last = user["last_name"]
    if last == None:
        last = ""
    if first == None:
        first = ""
    return str(first + " " + last).strip()


def end_conversation(update, context):
    user = update.message.from_user
    if not user.id in USERINFO:
        return startAgain(update, context)
    USERINFO[user.id].update({"bep20": update.message.text})
    USERINFO[user.id].update({"userId": user.id})
    USERINFO[user.id].update({"chatId": update.effective_chat.id})
    USERINFO[user.id].update({"name": getName(user)})
    USERINFO[user.id].update({"username": user.username})
    print(USERINFO[user.id])
    users.insert_one(USERINFO[user.id])
    url = f"https://t.me/{context.bot.username}?start={user.id}"

    # check refferal
    # if USERINFO[user.id]["ref"] != False:
    # refferal = USERINFO[user.id]["ref"]
    # info = getUserInfo(int(refferal))
    # print("Referall step 1")
    # print(refferal)
    # print(info)
    # if info != "":
    # if str(user.id) in info["refList"]:
    # info["refCount"] += 1
    # info["refList"].append(str(user.id))
    # users.update({"userId": refferal}, info)
    # print("Updated refferal")

    update.message.reply_text(
        JOINED.replace("REPLACEME", url),
        reply_markup=ReplyKeyboardMarkup(reply_keyboard),
    )
    return LOOP


def getRandomJoke():
    return getJoke()


def sureWantTo(update, context):
    user = update.message.from_user
    message = update.message.text
    print(message)
    if message == "YES":
        update.message.reply_text(
            "Goodbye!", reply_markup=ReplyKeyboardMarkup([["/start"]])
        )
        users.delete_one({"userId": user.id})
        return ConversationHandler.END

    if message == "NO":
        update.message.reply_text(
            "Oh thanks god, I thought I lost you",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard),
        )
        return LOOP


def cancel(update: Update) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    update.message.reply_text(
        "Goodbye!", reply_markup=ReplyKeyboardMarkup([["/start"]])
    )
    return ConversationHandler.END


def startAgain(update: Update) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    update.message.reply_text(
        "An error occured, please start the bot again.",
        reply_markup=ReplyKeyboardMarkup([["/start"]]),
    )
    return ConversationHandler.END


def loopAnswer(update, context):
    user = update.message.from_user
    info = mongo.getUserInfo(user.id)
    print(info)
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
            reply_markup=ReplyKeyboardMarkup([["YES"], ["NO"]]),
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
"""
    if reply == "":
        joke = getRandomJoke()
        joke = joke.split("  -")
        reply = f"""
I'm not sure what you meant, but here is a joke for you!
> {joke[0]}
- {joke[1]}
"""
    update.message.reply_text(
        reply,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard),
        parse_mode=telegram.ParseMode.MARKDOWN,
    )
    return LOOP


# %% Start bot
reply_keyboard = [
    ["💰 Balance", "ℹ️ Airdrop Info"],
    ["💸 Withdrawal", "🔗 Ref Link"],
    ["💾 My Data", "Quit Airdrop"],
]
(
    PROCEED,
    FOLLOW_TELEGRAM,
    FOLLOW_TWITTER,
    SUBMIT_ADDRESS,
    END_CONVERSATION,
    LOOP,
    SUREWANTTO,
    CAPTCHASTATE,
) = range(8)
cancelHandler = MessageHandler(Filters.regex("^Cancel$"), cancel)
states = {
    PROCEED: [
        MessageHandler(Filters.regex("^🚀 Join Airdrop$"), submit_details),
        cancelHandler,
    ],
    FOLLOW_TELEGRAM: [
        MessageHandler(Filters.regex("^Submit Details$"), follow_telegram),
        cancelHandler,
    ],
    FOLLOW_TWITTER: [
        MessageHandler(Filters.regex("^Done$"), follow_twitter),
        cancelHandler,
    ],
    SUBMIT_ADDRESS: [cancelHandler, MessageHandler(Filters.text, submit_address)],
    END_CONVERSATION: [
        cancelHandler,
        MessageHandler(Filters.regex("^0x[a-fA-F0-9]{40}$"), end_conversation),
    ],
    LOOP: [MessageHandler(Filters.text, loopAnswer)],
    SUREWANTTO: [MessageHandler(Filters.regex("^(YES|NO)$"), sureWantTo)],
    CAPTCHASTATE: [MessageHandler(Filters.text, checkCaptcha)],
}


conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states=states,
    fallbacks=[],
    name="main",
    persistent=True,
)


# %% Admin commands
def getList(update, context):
    user = update.message.from_user
    if user.username != ADMIN_USERNAME:
        return
    list = users.find({})

    with open("users.json", "w") as file:
        file.write("[")
        for document in list:
            file.write(dumps(document))
            file.write(",")
        file.write("]")
    with open("users.json", "r") as file:
        update.message.reply_document(document=file, filename="list.json")


def getStats(update, context):
    user = update.message.from_user
    if user.username != ADMIN_USERNAME:
        return
    list = users.find({})
    refes = users.find({"ref": {"$ne": False}}).count()
    reply = f"""
Currently there are *{list.count()} users* joined the airdrop!
Currently there are *{refes} users* joined by referrals
A total of *{"{:,.2f}".format(float(AIRDROP_AMOUNT.replace(",",""))*list.count())} {COIN_SYMBOL}* will be distributed as participation rewards
A total of *{"{:,.2f}".format(REFERRAL_REWARD*refes)} {COIN_SYMBOL}* referral rewards will be distributed
"""
    update.message.reply_text(reply, parse_mode=telegram.ParseMode.MARKDOWN)


def setStatus(update, context):
    user = update.message.from_user
    if user.username != ADMIN_USERNAME:
        return
    arg = context.args[0]
    if arg == "stop":
        set_bot_status("STOPPED")
        update.message.reply_text("Airdrop stopped")
    if arg == "pause":
        set_bot_status("PAUSED")
        update.message.reply_text("Airdrop paused")
    if arg == "start":
        set_bot_status("ON")
        update.message.reply_text("Airdrop started")


dispatcher.add_handler(CommandHandler("list", getList))
dispatcher.add_handler(CommandHandler("stats", getStats))
dispatcher.add_handler(CommandHandler("bot", setStatus))
dispatcher.add_handler(conv_handler)
# %% start the bot
updater.start_polling()
updater.idle()
