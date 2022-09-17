import os
import pickle

from utils.env import STATUS_PATH


BOT_STATUS = {}
if os.path.exists(STATUS_PATH):
    pickle.load(open(STATUS_PATH, "rb"))
else:
    BOT_STATUS = {"status": "ON"}


def get_bot_status():
    return BOT_STATUS["status"]


def set_bot_status(status):
    BOT_STATUS["status"] = status
    pickle.dump(BOT_STATUS, open(STATUS_PATH, "wb"))
