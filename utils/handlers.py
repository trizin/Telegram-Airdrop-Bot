import telegram


from telegram import (
    ReplyKeyboardMarkup,
)

from telegram.ext import (
    ConversationHandler,
    Filters,
    MessageHandler,
)
from utils.bot_status import get_bot_status, set_bot_status
from utils.keyboard import create_markup, get_reply_keyboard_markup
from utils.message_strings import *
from utils.jokes import getJoke
from utils.states import *
from utils import mongo

from multicolorcaptcha import CaptchaGenerator
from bson.json_util import dumps
from utils.tempdata import (
    getCaptchaData,
    getUserInfo,
    updateCaptchaData,
    updateUserInfo,
)


def submit_details(update, context):
    update.message.reply_text(
        text=PROCEED_MESSAGE, parse_mode=telegram.ParseMode.MARKDOWN
    )
    update.message.reply_text(
        text='Please click on "Submit Details" to proceed',
        parse_mode=telegram.ParseMode.MARKDOWN,
        reply_markup=create_markup([["Submit Details"], ["Cancel"]]),
    )
    return FOLLOW_TELEGRAM


def follow_twitter(update, context):
    update.message.reply_text(
        text=FOLLOW_TWITTER_TEXT, parse_mode=telegram.ParseMode.MARKDOWN
    )
    update.message.reply_text(
        text="Type in *your Twitter username* to proceed",
        parse_mode=telegram.ParseMode.MARKDOWN,
        reply_markup=create_markup([["Cancel"]]),
    )
    return SUBMIT_ADDRESS


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


def getName(user):
    first = user["first_name"]
    last = user["last_name"]
    if last == None:
        last = ""
    if first == None:
        first = ""
    return str(first + " " + last).strip()


def checkCaptcha(update, context):
    user = update.message.from_user
    text = update.message.text

    if getCaptchaData(user.id) != text:
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
        updateCaptchaData(user.id, True)
        return PROCEED


def generateCaptcha(update, context):
    user = update.message.from_user
    CAPCTHA_SIZE_NUM = 2
    generator = CaptchaGenerator(CAPCTHA_SIZE_NUM)
    captcha = generator.gen_captcha_image(difficult_level=3)
    image = captcha["image"]
    characters = captcha["characters"]
    updateCaptchaData(user.id, characters)
    filename = f"{user.id}.png"
    image.save(filename, "png")
    photo = open(filename, "rb")
    update.message.reply_photo(photo)
    update.message.reply_text("Please type in the numbers on the image")
    return CAPTCHASTATE


def submit_address(update, context):
    user = update.message.from_user
    if getUserInfo(user.id) == False:
        return startAgain(update, context)

    updateUserInfo(user.id, "twitter_username", update.message.text.strip())
    update.message.reply_text(
        text=SUBMIT_BEP20_TEXT,
        parse_mode=telegram.ParseMode.MARKDOWN,
        reply_markup=create_markup([["Cancel"]]),
    )
    return END_CONVERSATION


def start(update, context):
    user = update.message.from_user
    updateCaptchaData(user.id, False)

    refferal = update.message.text.replace("/start", "").strip()
    if refferal != "" and refferal != user.id and "ref" not in getUserInfo(user.id):
        updateUserInfo(user.id, "ref", refferal)
        print("Using refferal")
    else:
        updateUserInfo(user.id, "ref", False)

    NAME = getName(user)

    if mongo.getUserInfo(user.id) != "":
        update.message.reply_text(
            text="It seems like you have already joined!",
            reply_markup=get_reply_keyboard_markup(),
        )
        return LOOP

    count = mongo.users.count()
    if count >= MAX_USERS:
        return maxNumberReached(update, context)

    if get_bot_status() == "STOPPED":
        return botStopped(update, context)

    if get_bot_status() == "PAUSED":
        return botPaused(update, context)

    if CAPTCHA_ENABLED == "YES" and getCaptchaData(user.id) != True:
        return generateCaptcha(update, context)
    else:
        update.message.reply_text(
            text=WELCOME_MESSAGE.replace("NAME", NAME),
            reply_markup=create_markup([["🚀 Join Airdrop"]]),
            parse_mode=telegram.ParseMode.MARKDOWN,
        )
    return PROCEED


def end_conversation(update, context):
    user = update.message.from_user
    if getUserInfo(user.id) == False:
        return startAgain(update, context)

    updateUserInfo(user.id, "bep20", update.message.text.strip())
    updateUserInfo(user.id, "chatId", update.effective_chat.id)
    updateUserInfo(user.id, "userId", user.id)
    updateUserInfo(user.id, "name", getName(user))
    updateUserInfo(user.id, "username", user.username)
    mongo.users.insert_one(getUserInfo(user.id))
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


# Admin commands
def getList(update, context):
    user = update.message.from_user
    if user.username != ADMIN_USERNAME:
        return
    list = mongo.users.find({})

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
    list = mongo.users.find({})
    refes = mongo.users.find({"ref": {"$ne": False}}).count()
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


# ----------------
