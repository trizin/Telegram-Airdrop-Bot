# %% Dependencies
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)
import pymongo
import logging
import os

# %% MONGODB CONNECTION
USERINFO = []
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["airdrop"]
users = mydb["users"]
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
# %% Setting up things
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
updater = Updater(token=BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher

# %% Message Strings
WELCOME_MESSAGE = f"""
Hello, FIRST_NAME LAST_NAME! I am your friendly {COIN_NAME} Airdrop bot
✅Please do the required tasks to be eligible to get airdrop tokens.

🔹1 VINE = {COIN_PRICE}
🔸For Joining - Get {AIRDROP_AMOUNT} {COIN_SYMBOL}
⭐️ For each referral - Get {REFERRAL_REWARD} {COIN_SYMBOL}

📘By Participating you are agreeing to the {COIN_NAME} (Airdrop) Program Terms and Conditions. Please see pinned post for more information.”
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
🔹 Like, retweet pinned post and Tag 3 friends

Website: {WEBSITE_URL}"""

FOLLOW_TWITTER_TEXT = """
🔹 Follow our Twitter page

Submit your Twitter profile link to proceed
"""

SUBMIT_BEP20_TEXT = f"""
**Submit Wallet Address {AIRDROP_NETWORK}**

Please make sure your wallet supports the {AIRDROP_NETWORK}
"""

# %% Functions


def start(update, context):
    reply_keyboard = [['Join Airdrop']]
    user = update.message.from_user
    FIRST_NAME = user["first_name"]
    LAST_NAME = user["last_name"]
    update.message.reply_text(chat_id=update.effective_chat.id, text=WELCOME_MESSAGE.replace("FIRST_NAME", FIRST_NAME).replace("LAST_NAME", LAST_NAME),
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))


def submit_details(update, context):
    update.message.reply_text(chat_id=update.effective_chat.id, text=PROCEED_MESSAGE, reply_markup=ReplyKeyboardMarkup(
        [["Submit Details", "Cancel"]]
    ))
    return PROCEED


def follow_twitter(update, context):
    update.message.reply_text(chat_id=update.effective_chat.id, text=FOLLOW_TWITTER_TEXT, reply_markup=ReplyKeyboardMarkup(
        [["Cancel"]]
    ))
    return FOLLOW_TWITTER


def submit_address(update, context):
    user = update.message.from_user
    USERINFO[user.id].update({"twitter_username": update.message.text})
    update.message.reply_text(chat_id=update.effective_chat.id, text=SUBMIT_BEP20_TEXT, reply_markup=ReplyKeyboardMarkup(
        [["Cancel"]]
    ))
    return SUBMIT_BEP20_TEXT


def end_conversation(update, context):
    user = update.message.from_user
    USERINFO[user.id].update({"bep20": update.message.text})
    USERINFO[user.id].update({"userId": user.id})
    update.message.reply_text(f'Thank you! You will receive airdrop on {AIRDROP_DATE}.')
    users.insert_one(USERINFO[user.id])
    return ConversationHandler.END
    # %% Handlers


def cancel(update: Update, context: CallbackContext) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    update.message.reply_text(
        'Bye! I hope we can talk again some day.', reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


PROCEED, FOLLOW_TWITTER, SUBMIT_ADDRESS = range(3)

conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        PROCEED: [CommandHandler("Join Airdrop", submit_details)],
        FOLLOW_TWITTER: [CommandHandler("Submit Details", follow_twitter)],
        SUBMIT_ADDRESS: [MessageHandler(Filters.text, end_conversation)]
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)

dispatcher.add_handler(conv_handler)

# %% start the bot
updater.start_polling()
updater.idle()
