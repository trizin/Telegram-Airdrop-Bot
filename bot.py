import logging

from utils.handlers import *
from utils.handlers import BOT_TOKEN

from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    PicklePersistence,
)


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
persistence = PicklePersistence(filename="conversationbot/conversationbot")
updater = Updater(token=BOT_TOKEN, use_context=True, persistence=persistence)
dispatcher = updater.dispatcher


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


dispatcher.add_handler(CommandHandler("list", getList))
dispatcher.add_handler(CommandHandler("stats", getStats))
dispatcher.add_handler(CommandHandler("bot", setStatus))
dispatcher.add_handler(conv_handler)
# %% start the bot
updater.start_polling()
updater.idle()
