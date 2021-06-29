# %% Dependencies
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, InlineKeyboardMarkup
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
#from dotenv import load_dotenv
# load_dotenv()
USERINFO = {}  # holds user information
# %% ENV VARIABLES
COIN_SYMBOL = os.environ["COIN_SYMBOL"]
COIN_NAME = os.environ["COIN_NAME"]
AIRDROP_AMOUNT = os.environ["AIRDROP_AMOUNT"]
AIRDROP_DATE = os.environ["AIRDROP_DATE"]
BOT_TOKEN = os.environ["BOT_TOKEN"]
AIRDROP_NETWORK = os.environ["AIRDROP_NETWORK"]
REFERRAL_REWARD = os.environ["REFERRAL_REWARD"]
COIN_PRICE = os.environ["COIN_PRICE"]
WEBSITE_URL = os.environ["WEBSITE_URL"]
MONGO_USER = os.environ["MONGO_INITDB_ROOT_USERNAME"]
MONGO_PASSWORD = os.environ["MONGO_INITDB_ROOT_PASSWORD"]

TWITTER_LINKS = os.environ["TWITTER_LINKS"]
TELEGRAM_LINKS = os.environ["TELEGRAM_LINKS"]

TWITTER_LINKS = TWITTER_LINKS.split(",")
TELEGRAM_LINKS = TELEGRAM_LINKS.split(",")
TWITTER_LINKS = "\n".join(TWITTER_LINKS)
TELEGRAM_LINKS = "\n".join(TELEGRAM_LINKS)

# %% MONGODB CONNECTION
CONNECTION_STRING = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@mongodb:27017/?authSource=admin"
myclient = pymongo.MongoClient(CONNECTION_STRING)
mydb = myclient["airdrop"]
users = mydb["users"]
# %% Setting up things
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
print(BOT_TOKEN)
persistence = PicklePersistence(filename='conversationbot/conversationbot')
updater = Updater(token=BOT_TOKEN, use_context=True, persistence=persistence)
dispatcher = updater.dispatcher

# %% Message Strings
WELCOME_MESSAGE = f"""
Hello, NAME! I am your friendly {COIN_NAME} Airdrop bot
✅Please do the required tasks to be eligible to get airdrop tokens.

🔹1 {COIN_SYMBOL} = {COIN_PRICE}
🔸For Joining - Get {AIRDROP_AMOUNT} {COIN_SYMBOL}
⭐️ For each referral - Get {REFERRAL_REWARD} {COIN_SYMBOL}

📘By Participating you are agreeing to the {COIN_NAME} (Airdrop) Program Terms and Conditions. Please see pinned post for more information.
Click "Join Airdrop" to proceed"""
tasks = ""

PROCEED_MESSAGE = f"""
⭐️ 1 {COIN_SYMBOL} = {COIN_PRICE}

🔹 Total to earn per participant (if you complete all the tasks) = {AIRDROP_AMOUNT} {COIN_SYMBOL}
🔹 Per referral = {REFERRAL_REWARD} {COIN_SYMBOL}

📢 Airdrop Rules

✏️ Mandatory Tasks:
🔹 Join our telegram channels
🔹 Follow our Twitter page
NOTE: Users found Cheating would be disqualified & banned immediately.

Airdrop Date: {AIRDROP_DATE}

Website: {WEBSITE_URL}"""

MAKE_SURE_TELEGRAM = f"""
Do no forget to join our Telegram channel
{TELEGRAM_LINKS}
"""

FOLLOW_TWITTER_TEXT = f"""
🔹 Follow our Twitter page
{TWITTER_LINKS}
Submit your Twitter username link to proceed
"""

SUBMIT_BEP20_TEXT = f"""
*Submit Wallet Address {AIRDROP_NETWORK}*

Please make sure your wallet supports the *{AIRDROP_NETWORK}*
"""

JOINED = f"""
Thank you!
Rewards would be sent out automatically to your {AIRDROP_NETWORK} address on the {AIRDROP_DATE}

*Don't forget to:*
🔸 Stay in the telegram channels
🔸 Follow all the social media channels for the updates

Your personal referral link: (+{REFERRAL_REWARD} {COIN_SYMBOL} for each referral)
REPLACEME
"""

WITHDRAWAL_TEXT = f"""
Withdrawals would be sent out automatically to your {AIRDROP_NETWORK} address on the {AIRDROP_DATE}
NOTE: Users found Cheating would be disqualified & banned immediately."""

BALANCE_TEXT = """
IART Airdrop Balance: IARTBALANCE
Referral Balance: REFERRALBALANCE
"""

# %% Functions
PROCEED, FOLLOW_TELEGRAM, FOLLOW_TWITTER, SUBMIT_ADDRESS, END_CONVERSATION, LOOP, SUREWANTTO = range(7)


def getUserInfo(id):
    user = ""
    for x in users.find({"userId": id}):
        user = x
        if "refCount" not in user:
            user["refCount"] = 0
            user["refList"] = []
    return user


def start(update, context):
    user = update.message.from_user
    print(update.message)
    refferal = update.message.text.replace("/start", "").strip()
    USERINFO[user.id] = {}
    if refferal != "" and refferal != user.id:
        USERINFO[user.id]["ref"] = refferal
        print("Using refferal")
    else:
        USERINFO[user.id]["ref"] = False

    NAME = getName(user)
    update.message.reply_text(text=WELCOME_MESSAGE.replace("NAME", NAME),
                              reply_markup=ReplyKeyboardMarkup([['Join Airdrop']]), parse_mode=telegram.ParseMode.MARKDOWN)

    if(getUserInfo(user.id) != ""):
        update.message.reply_text(text="It seems like you have already joined!", reply_markup=reply_keyboard)
        return LOOP

    return PROCEED


def submit_details(update, context):
    update.message.reply_text(text=PROCEED_MESSAGE, parse_mode=telegram.ParseMode.MARKDOWN, reply_markup=ReplyKeyboardMarkup(
        [["Submit Details"], ["Cancel"]]
    ))
    return FOLLOW_TELEGRAM


def follow_telegram(update, context):
    update.message.reply_text(text=MAKE_SURE_TELEGRAM, parse_mode=telegram.ParseMode.MARKDOWN, reply_markup=ReplyKeyboardMarkup(
        [["Done"], ["Cancel"]]
    ))

    return FOLLOW_TWITTER


def follow_twitter(update, context):
    update.message.reply_text(text=FOLLOW_TWITTER_TEXT, parse_mode=telegram.ParseMode.MARKDOWN, reply_markup=ReplyKeyboardMarkup(
        [["Cancel"]]
    ))
    return SUBMIT_ADDRESS


def submit_address(update, context):
    user = update.message.from_user
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
    USERINFO[user.id].update({"bep20": update.message.text})
    USERINFO[user.id].update({"userId": user.id})
    USERINFO[user.id].update({"chatId": update.effective_chat.id})
    USERINFO[user.id].update({"name": getName(user)})
    USERINFO[user.id].update({"username": user.username})
    print(USERINFO[user.id])
    users.insert_one(USERINFO[user.id])
    url = f"https://t.me/{context.bot.username}?start={user.id}"

    # check refferal
    if USERINFO[user.id]["ref"] != False:
        refferal = USERINFO[user.id]["ref"]
        info = getUserInfo(refferal)
        if info != "":
            if str(user.id) in info["refList"]:
                info["refCount"] += 1
                info["refList"].append(str(user.id))
                users.update({"userId": refferal}, info)
                print("Updated refferal")

    update.message.reply_text(JOINED.replace("REPLACEME", url), reply_markup=ReplyKeyboardMarkup(reply_keyboard))
    return LOOP
    # %% Handlers


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
            'Oh thanks god, I thought I lost you', reply_markup=reply_keyboard
        )
        return LOOP


def cancel(update: Update, context: CallbackContext) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    update.message.reply_text(
        'Goodbye!', reply_markup=ReplyKeyboardMarkup([['/start']])
    )
    return ConversationHandler.END


def loopAnswer(update, context):
    user = update.message.from_user
    info = getUserInfo(user.id)
    print(info)
    message = update.message.text
    reply = ""
    if(message == "Balance"):
        refbal = str(info["refCount"]*REFERRAL_REWARD)
        if(refbal == ""):
            refbal = "0"
        reply = BALANCE_TEXT.replace("IARTBALANCE", AIRDROP_AMOUNT).replace("REFERRALBALANCE", refbal)

    if(message == "Airdrop Info"):
        reply = PROCEED_MESSAGE

    if(message == "Withdrawal"):
        reply = WITHDRAWAL_TEXT

    if(message == "Ref Link"):
        reply = f"""
Here is your referral link:
https://t.me/{context.bot.username}?start={user.id}
"""

    if(message == "Quit Airdrop"):
        update.message.reply_text("Are you sure want to delete all the data and quit the Airdrop?", reply_markup=ReplyKeyboardMarkup([['YES'], ['NO']]))
        return SUREWANTTO

    if(message == "My Data"):
        name = str(info["name"])
        balance = BALANCE_TEXT.replace("IARTBALANCE", AIRDROP_AMOUNT).replace("REFERRALBALANCE", str(info["refCount"]*REFERRAL_REWARD*1))
        refferals = str(info["refCount"])
        bep20Address = str(info["bep20"])
        twitterUsername = str(info["twitter_username"])
        reply = f"""
Name: {name}
Referrals: {refferals}
{AIRDROP_NETWORK} address: {bep20Address}
Twitter Username: {twitterUsername}
"""
    update.message.reply_text(reply, reply_markup=ReplyKeyboardMarkup(reply_keyboard))
    return LOOP


# %% Start bot
reply_keyboard = [
    ["Balance", "Airdrop Info"],
    ["Withdrawal", "Ref Link"],
    ["My Data", "Quit Airdrop"]
]

cancelHandler = MessageHandler(Filters.regex('^Cancel$'), cancel)
conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        PROCEED: [MessageHandler(Filters.regex('^Join Airdrop$'), submit_details), cancelHandler],
        FOLLOW_TELEGRAM: [MessageHandler(Filters.regex('^Submit Details$'), follow_telegram), cancelHandler],
        FOLLOW_TWITTER: [MessageHandler(Filters.regex('^Done$'), follow_twitter), cancelHandler],
        SUBMIT_ADDRESS: [cancelHandler, MessageHandler(Filters.text, submit_address)],
        END_CONVERSATION: [cancelHandler, MessageHandler(Filters.regex('^0x[a-fA-F0-9]{40}$'), end_conversation)],
        LOOP: [MessageHandler(
            Filters.regex('^(Balance|Airdrop Info|Withdrawal|Ref Link|My Data|Quit Airdrop)$'), loopAnswer
        )],
        SUREWANTTO: [MessageHandler(Filters.regex('^(YES|NO)$'), sureWantTo)]
    },
    fallbacks=[CommandHandler('cancel', cancel)],
    name="main",
    persistent=True,
)

dispatcher.add_handler(conv_handler)

# %% start the bot
updater.start_polling()
updater.idle()
