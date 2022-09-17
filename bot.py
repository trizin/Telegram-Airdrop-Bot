import telegram
import logging

from utils import mongo
from utils.bot_status import get_bot_status, set_bot_status
from utils.env import *
from utils.message_strings import *
from utils.mongo import users
from utils.keyboard import create_markup, get_reply_keyboard_markup
from utils.handlers import *
from utils.states import *

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
            reply_markup=create_markup([["🚀 Join Airdrop"]]),
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
            reply_markup=get_reply_keyboard_markup(),
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
            reply_markup=create_markup([["🚀 Join Airdrop"]]),
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


def submit_address(update, context):
    user = update.message.from_user
    if not user.id in USERINFO:
        return startAgain(update, context)
    USERINFO[user.id].update({"twitter_username": update.message.text.strip()})
    update.message.reply_text(
        text=SUBMIT_BEP20_TEXT,
        parse_mode=telegram.ParseMode.MARKDOWN,
        reply_markup=create_markup([["Cancel"]]),
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
        reply_markup=get_reply_keyboard_markup(),
    )
    return LOOP


# %% Start bot

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


dispatcher.add_handler(CommandHandler("list", getList))
dispatcher.add_handler(CommandHandler("stats", getStats))
dispatcher.add_handler(CommandHandler("bot", setStatus))
dispatcher.add_handler(conv_handler)
# %% start the bot
updater.start_polling()
updater.idle()
