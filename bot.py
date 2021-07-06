# %% Dependencies
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, InlineKeyboardMarkup
from bson.json_util import dumps
from multicolorcaptcha import CaptchaGenerator
from jokes import getJoke
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
    PicklePersistence,
)
from telegram.utils import helpers
import telegram
import pymongo
import logging
import os
import pickle
# from dotenv import load_dotenv
# load_dotenv()
USERINFO = {}  # holds user information
CAPTCHA_DATA = {}
# %% ENV VARIABLES
COIN_SYMBOL = os.environ["COIN_SYMBOL"]
COIN_NAME = os.environ["COIN_NAME"]
AIRDROP_AMOUNT = os.environ["AIRDROP_AMOUNT"]
AIRDROP_AMOUNT = "{:,.2f}".format(float(AIRDROP_AMOUNT))
AIRDROP_DATE = os.environ["AIRDROP_DATE"]
BOT_TOKEN = os.environ["BOT_TOKEN"]
AIRDROP_NETWORK = os.environ["AIRDROP_NETWORK"]
REFERRAL_REWARD = float(os.environ["REFERRAL_REWARD"])
COIN_PRICE = os.environ["COIN_PRICE"]
WEBSITE_URL = os.environ["WEBSITE_URL"]
MONGO_USER = os.environ["MONGO_INITDB_ROOT_USERNAME"]
MONGO_PASSWORD = os.environ["MONGO_INITDB_ROOT_PASSWORD"]
MONGO_IP = os.environ["MONGO_INITDB_IP"]
MONGO_PORT = os.environ["MONGO_INITDB_PORT"]
EXPLORER_URL = os.environ["EXPLORER_URL"]
ADMIN_USERNAME = os.environ["ADMIN_USERNAME"]

TWITTER_LINKS = os.environ["TWITTER_LINKS"]
TELEGRAM_LINKS = os.environ["TELEGRAM_LINKS"]
MAX_USERS = int(os.environ["MAX_USERS"])
MAX_REFS = int(os.environ["MAX_REFS"])
CAPTCHA_ENABLED = os.environ["CAPTCHA_ENABLED"]

TWITTER_LINKS = TWITTER_LINKS.split(",")
TELEGRAM_LINKS = TELEGRAM_LINKS.split(",")
TWITTER_LINKS = "\n".join(TWITTER_LINKS)
TELEGRAM_LINKS = "\n".join(TELEGRAM_LINKS)
STATUS_PATH = "./conversationbot/botconfig.p"
if os.path.exists(STATUS_PATH):
    BOT_STATUS = {}
    pickle.load(open(STATUS_PATH, "rb"))
else:
    BOT_STATUS = {"status": "ON"}

# %% MONGODB CONNECTION
CONNECTION_STRING = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_IP}:{MONGO_PORT}/?authSource=admin"
myclient = pymongo.MongoClient(CONNECTION_STRING)
mydb = myclient["airdrop"]
users = mydb["users"]
users.create_index([('ref', pymongo.TEXT)], name='search_index', default_language='english')
users.create_index("userId")
# %% Setting up things
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
print(BOT_TOKEN)
persistence = PicklePersistence(filename='conversationbot/conversationbot')
updater = Updater(token=BOT_TOKEN, use_context=True, persistence=persistence)
dispatcher = updater.dispatcher

# %% Message Strings
if(COIN_PRICE == "0"):
    SYMBOL = ""
else:
    SYMBOL = f"\n⭐️ 1 {COIN_SYMBOL} = {COIN_PRICE}"
if(EXPLORER_URL != ""):
    EXPLORER_URL = f"\nContract: {EXPLORER_URL}"
if(WEBSITE_URL != ""):
    WEBSITE_URL = f"\nWebsite: {WEBSITE_URL}"
WELCOME_MESSAGE = f"""
Hello, NAME! I am your friendly {COIN_NAME} Airdrop bot
{SYMBOL}
🔸For Joining - Get {AIRDROP_AMOUNT} {COIN_SYMBOL}
⭐️ For each referral - Get {"{:,.2f}".format(REFERRAL_REWARD)} {COIN_SYMBOL}

📘By Participating you are agreeing to the {COIN_NAME} (Airdrop) Program Terms and Conditions. Please see pinned post for more information.
Click "🚀 Join Airdrop" to proceed"""
tasks = ""

PROCEED_MESSAGE = f"""
🔹 Airdrop Reward = *{AIRDROP_AMOUNT} {COIN_SYMBOL}*
🔹 Extra reward per referral = *{"{:,.2f}".format(REFERRAL_REWARD)} {COIN_SYMBOL}* (max {MAX_REFS}){SYMBOL}

📢 Airdrop Rules

✏️ Mandatory Tasks:
- Join our telegram channels
- Follow our Twitter page

NOTE: Users found Cheating would be disqualified & banned immediately.

Airdrop Date: *{AIRDROP_DATE}*{EXPLORER_URL}
{WEBSITE_URL}
"""

MAKE_SURE_TELEGRAM = f"""
Do no forget to join our Telegram channel
{TELEGRAM_LINKS}
"""

FOLLOW_TWITTER_TEXT = f"""
🔹 Follow our Twitter page
{TWITTER_LINKS}
"""


SUBMIT_BEP20_TEXT = f"""
Type in *your Wallet Address*

Please make sure your wallet supports the *{AIRDROP_NETWORK}*
"""

JOINED = f"""
Thank you!
Rewards would be sent out automatically to your {AIRDROP_NETWORK} address on the {AIRDROP_DATE}

Don't forget to:
🔸 Stay in the telegram channels
🔸 Follow all the social media channels for the updates

Your personal referral link (+{"{:,.2f}".format(REFERRAL_REWARD)} {COIN_SYMBOL} for each referral)
REPLACEME
"""

WITHDRAWAL_TEXT = f"""
Withdrawals would be sent out automatically to your {AIRDROP_NETWORK} address on the {AIRDROP_DATE}
NOTE: Users found Cheating would be disqualified & banned immediately."""

BALANCE_TEXT = f"""
{COIN_NAME} Airdrop Balance: *IARTBALANCE*
Referral Balance: *REFERRALBALANCE*
"""

# %% Functions


def setBotStatus(status):
    BOT_STATUS["status"] = status
    pickle.dump(BOT_STATUS, open(STATUS_PATH, "wb"))


def getUserInfo(id):
    user = ""
    for x in users.find({"userId": id}):
        user = x
        refs = users.find({"ref": str(id)})
        user["refCount"] = refs.count()
        # if "refCount" not in user:
        # user["refCount"] = 0
        # user["refList"] = []
    return user


def maxNumberReached(update, context):
    update.message.reply_text("Hey! Thanks for your interest but it seems like the maximum amount of users has been reached.")
    return ConversationHandler.END


def botStopped(update, context):
    update.message.reply_text("The airdrop has been completed. Thanks for you interest.")
    return ConversationHandler.END


def botPaused(update, context):
    update.message.reply_text("The airdrop has been temporarily paused, please try again later", reply_markup=ReplyKeyboardMarkup([["/start"]]))
    return ConversationHandler.END


def checkCaptcha(update, context):
    user = update.message.from_user
    text = update.message.text

    if CAPTCHA_DATA[user.id] != text:
        update.message.reply_text("Invalid captcha!")
        return generateCaptcha(update, context)
    else:
        NAME = getName(user)
        update.message.reply_text(text="Correct!",
                                  parse_mode=telegram.ParseMode.MARKDOWN)
        update.message.reply_text(text=WELCOME_MESSAGE.replace("NAME", NAME),
                                  reply_markup=ReplyKeyboardMarkup([['🚀 Join Airdrop']]), parse_mode=telegram.ParseMode.MARKDOWN)
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

    if(getUserInfo(user.id) != ""):
        update.message.reply_text(text="It seems like you have already joined!", reply_markup=ReplyKeyboardMarkup(reply_keyboard))
        return LOOP

    count = users.count()
    if(count >= MAX_USERS):
        return maxNumberReached(update, context)

    if(BOT_STATUS["status"] == "STOPPED"):
        return botStopped(update, context)

    if(BOT_STATUS["status"] == "PAUSED"):
        return botPaused(update, context)

    if(CAPTCHA_ENABLED == "YES" and CAPTCHA_DATA[user.id] != True):
        return generateCaptcha(update, context)
    else:
        update.message.reply_text(text=WELCOME_MESSAGE.replace("NAME", NAME),
                                  reply_markup=ReplyKeyboardMarkup([['🚀 Join Airdrop']]), parse_mode=telegram.ParseMode.MARKDOWN)
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
    update.message.reply_text(text=PROCEED_MESSAGE, parse_mode=telegram.ParseMode.MARKDOWN)
    update.message.reply_text(text="Please click on \"Submit Details\" to proceed", parse_mode=telegram.ParseMode.MARKDOWN, reply_markup=ReplyKeyboardMarkup(
        [["Submit Details"], ["Cancel"]]
    ))
    return FOLLOW_TELEGRAM


def follow_telegram(update, context):
    update.message.reply_text(text=MAKE_SURE_TELEGRAM, parse_mode=telegram.ParseMode.MARKDOWN)
    update.message.reply_text(text="Please click on \"Done\" to proceed", parse_mode=telegram.ParseMode.MARKDOWN, reply_markup=ReplyKeyboardMarkup(
        [["Done"], ["Cancel"]]
    ))

    return FOLLOW_TWITTER


def follow_twitter(update, context):
    update.message.reply_text(text=FOLLOW_TWITTER_TEXT, parse_mode=telegram.ParseMode.MARKDOWN)
    update.message.reply_text(text="Type in *your Twitter username* to proceed", parse_mode=telegram.ParseMode.MARKDOWN, reply_markup=ReplyKeyboardMarkup(
        [["Cancel"]]
    ))
    return SUBMIT_ADDRESS


def submit_address(update, context):
    user = update.message.from_user
    if not user.id in USERINFO:
        return startAgain(update, context)
    USERINFO[user.id].update({"twitter_username": update.message.text.strip()})
    update.message.reply_text(text=SUBMIT_BEP20_TEXT, parse_mode=telegram.ParseMode.MARKDOWN, reply_markup=ReplyKeyboardMarkup(
        [["Cancel"]]
    ))
    return END_CONVERSATION


def getName(user):
    first = user["first_name"]
    last = user["last_name"]
    if(last == None):
        last = ""
    if(first == None):
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

    update.message.reply_text(JOINED.replace("REPLACEME", url), reply_markup=ReplyKeyboardMarkup(reply_keyboard))
    return LOOP


def getRandomJoke():
    return getJoke()


def sureWantTo(update, context):
    user = update.message.from_user
    message = update.message.text
    print(message)
    if(message == "YES"):
        update.message.reply_text(
            'Goodbye!', reply_markup=ReplyKeyboardMarkup([['/start']])
        )
        users.delete_one({"userId": user.id})
        return ConversationHandler.END

    if(message == "NO"):
        update.message.reply_text(
            'Oh thanks god, I thought I lost you', reply_markup=ReplyKeyboardMarkup(reply_keyboard)
        )
        return LOOP


def cancel(update: Update, context: CallbackContext) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    update.message.reply_text(
        'Goodbye!', reply_markup=ReplyKeyboardMarkup([['/start']])
    )
    return ConversationHandler.END


def startAgain(update: Update, context: CallbackContext) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    update.message.reply_text(
        'An error occured, please start the bot again.', reply_markup=ReplyKeyboardMarkup([['/start']])
    )
    return ConversationHandler.END


def loopAnswer(update, context):
    user = update.message.from_user
    info = getUserInfo(user.id)
    print(info)
    message = update.message.text
    reply = ""
    if(message == "💰 Balance"):
        refbal = "{:,.2f}".format(info["refCount"]*REFERRAL_REWARD)
        if(refbal == ""):
            refbal = "0"
        reply = BALANCE_TEXT.replace("IARTBALANCE", AIRDROP_AMOUNT).replace("REFERRALBALANCE", refbal)

    if(message == "ℹ️ Airdrop Info"):
        reply = PROCEED_MESSAGE

    if(message == "💸 Withdrawal"):
        reply = WITHDRAWAL_TEXT

    if(message == "🔗 Ref Link"):
        reply = f"""
Here is *your referral link*
[https://t.me/{context.bot.username}?start={user.id}](https://t.me/{context.bot.username}?start={user.id})
"""

    if(message == "Quit Airdrop"):
        update.message.reply_text("Are you sure want to quit the Airdrop? All your data will be deleted", reply_markup=ReplyKeyboardMarkup([['YES'], ['NO']]))
        return SUREWANTTO

    if(message == "💾 My Data"):
        name = str(info["name"])
        refbal = "{:,.2f}".format(info["refCount"]*REFERRAL_REWARD)
        balance = BALANCE_TEXT.replace("IARTBALANCE", AIRDROP_AMOUNT).replace("REFERRALBALANCE", refbal)
        refferals = str(info["refCount"])
        bep20Address = str(info["bep20"])
        twitterUsername = str(info["twitter_username"])
        reply = f"""
Name: {name}
Referrals: {refferals}
{AIRDROP_NETWORK} address: {bep20Address}
Twitter Username: {twitterUsername}
"""
    if(reply == ""):
        joke = getRandomJoke()
        joke = joke.split("  -")
        reply = f"""
I'm not sure what you meant, but here is a joke for you!
> {joke[0]}
- {joke[1]}
"""
    update.message.reply_text(reply, reply_markup=ReplyKeyboardMarkup(reply_keyboard), parse_mode=telegram.ParseMode.MARKDOWN)
    return LOOP


# %% Start bot
reply_keyboard = [
    ["💰 Balance", "ℹ️ Airdrop Info"],
    ["💸 Withdrawal", "🔗 Ref Link"],
    ["💾 My Data", "Quit Airdrop"]
]
PROCEED, FOLLOW_TELEGRAM, FOLLOW_TWITTER, SUBMIT_ADDRESS, END_CONVERSATION, LOOP, SUREWANTTO, CAPTCHASTATE = range(8)
cancelHandler = MessageHandler(Filters.regex('^Cancel$'), cancel)
states = {
    PROCEED: [MessageHandler(Filters.regex('^🚀 Join Airdrop$'), submit_details), cancelHandler],
    FOLLOW_TELEGRAM: [MessageHandler(Filters.regex('^Submit Details$'), follow_telegram), cancelHandler],
    FOLLOW_TWITTER: [MessageHandler(Filters.regex('^Done$'), follow_twitter), cancelHandler],
    SUBMIT_ADDRESS: [cancelHandler, MessageHandler(Filters.text, submit_address)],
    END_CONVERSATION: [cancelHandler, MessageHandler(Filters.regex('^0x[a-fA-F0-9]{40}$'), end_conversation)],
    LOOP: [MessageHandler(
        Filters.text, loopAnswer
    )],
    SUREWANTTO: [MessageHandler(Filters.regex('^(YES|NO)$'), sureWantTo)],
    CAPTCHASTATE: [MessageHandler(Filters.text, checkCaptcha)]
}


conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states=states,
    fallbacks=[],
    name="main",
    persistent=True,
)


# %% Admin commands
def getList(update, context):
    user = update.message.from_user
    if(user.username != ADMIN_USERNAME):
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
    if(user.username != ADMIN_USERNAME):
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
    if(user.username != ADMIN_USERNAME):
        return
    arg = context.args[0]
    if(arg == "stop"):
        setBotStatus("STOPPED")
        update.message.reply_text("Airdrop stopped")
    if(arg == "pause"):
        setBotStatus("PAUSED")
        update.message.reply_text("Airdrop paused")
    if(arg == "start"):
        setBotStatus("ON")
        update.message.reply_text("Airdrop started")


dispatcher.add_handler(CommandHandler("list", getList))
dispatcher.add_handler(CommandHandler("stats", getStats))
dispatcher.add_handler(CommandHandler("bot", setStatus))
dispatcher.add_handler(conv_handler)
# %% start the bot
updater.start_polling()
updater.idle()
