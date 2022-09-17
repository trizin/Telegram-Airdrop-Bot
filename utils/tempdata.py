USERINFO = {}  # holds user information
CAPTCHA_DATA = {}


def updateUserInfo(id, key, value):
    if id not in USERINFO:
        USERINFO[id] = {}
    USERINFO[id][key] = value


def getUserInfo(id):
    if id in USERINFO:
        return USERINFO[id]
    return False


def updateCaptchaData(id, value):
    CAPTCHA_DATA[id] = value


def getCaptchaData(id):
    if id in CAPTCHA_DATA:
        return CAPTCHA_DATA[id]
    return False
