# %% Dependencies
from telegram.ext import Updater, CommandHandler
import logging
import os
# %% ENV VARIABLES
COIN_SYMBOL = os.environ["COIN_SYMBOL"]
COIN_NAME = os.environ["COIN_NAME"]
AIRDROP_AMOUNT = os.environ["AIRDROP_AMOUNT"]
AIRDROP_DATE = os.environ["AIRDROP_DATE"]
BOT_TOKEN = os.environ["BOT_TOKEN"]
AIRDROP_NETWORK = os.environ["AIRDROP_NETWORK"]
REFERRAL_REWARD = os.environ["REFERRAL_REWARD"]
COIN_PRICE = os.environ["COIN_PRICE"]

# %% Setting up things
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
updater = Updater(token=BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher

# %% Message Strings
WELCOME_MESSAGE = f"""
Hello, /** */! I am your friendly {COIN_NAME} Airdrop bot
✅Please do the required tasks to be eligible to get airdrop tokens.

🔹1 VINE = {COIN_PRICE}
🔸For Joining - Get {AIRDROP_AMOUNT} {COIN_SYMBOL}
⭐️ For each referral - Get {REFERRAL_REWARD} {COIN_SYMBOL}

📘By Participating you are agreeing to the {COIN_NAME} (Airdrop) Program Terms and Conditions. Please see pinned post for more information.”
Click "Join Airdrop" to proceed"""

# %% Functions


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=WELCOME_MESSAGE)

# %% Handlers


start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

# %% start the bot
updater.start_polling()
