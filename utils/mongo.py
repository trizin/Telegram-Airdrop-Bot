import pymongo
from utils.env import MONGO_USER, MONGO_PASSWORD, MONGO_IP, MONGO_PORT


CONNECTION_STRING = (
    f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_IP}:{MONGO_PORT}/?authSource=admin"
)


myclient = pymongo.MongoClient(CONNECTION_STRING)
mydb = myclient["airdrop"]
users = mydb["users"]
users.create_index(
    [("ref", pymongo.TEXT)], name="search_index", default_language="english"
)
users.create_index("userId")


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
