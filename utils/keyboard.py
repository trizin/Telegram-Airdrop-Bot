from telegram import (
    ReplyKeyboardMarkup,
    Update,
)

REPLY_KEYBOARD = [
    ["💰 Balance", "ℹ️ Airdrop Info"],
    ["💸 Withdrawal", "🔗 Ref Link"],
    ["💾 My Data", "Quit Airdrop"],
]


def create_markup(buttons):
    return ReplyKeyboardMarkup(buttons)


def get_reply_keyboard_markup():
    return ReplyKeyboardMarkup(REPLY_KEYBOARD)
