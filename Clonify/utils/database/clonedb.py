from Clonify.core.mongo import mongodb, pymongodb
from typing import Optional

cloneownerdb = mongodb.cloneownerdb
clonebotdb = pymongodb.clonebotdb
clonebotnamedb = mongodb.clonebotnamedb


# -------------------------------
# SAVE / GET OWNER
# -------------------------------
async def save_clonebot_owner(bot_id: int, user_id: int):
    await cloneownerdb.insert_one({"bot_id": bot_id, "user_id": user_id})


async def get_clonebot_owner(bot_id: int) -> Optional[int]:
    result = await cloneownerdb.find_one({"bot_id": bot_id})
    return result.get("user_id") if result else None


# -------------------------------
# SAVE / GET BOT USERNAME
# -------------------------------
async def save_clonebot_username(bot_id: int, user_name: str):
    await clonebotnamedb.insert_one({"bot_id": bot_id, "user_name": user_name})


async def get_clonebot_username(bot_id: int) -> Optional[str]:
    result = await clonebotnamedb.find_one({"bot_id": bot_id})
    return result.get("user_name") if result else None


# -------------------------------
# OWNER FETCH (SYNC)
# -------------------------------
def get_owner_id_from_db(bot_id: int) -> Optional[int]:
    bot_data = clonebotdb.find_one({"bot_id": bot_id})
    return bot_data.get("user_id") if bot_data else None


# -------------------------------
# 🚫 PREMIUM REMOVED
# -------------------------------
def check_bot_premium(bot_id: int) -> bool:
    return True


# -------------------------------
# 🤖 ASSISTANT SYSTEM
# -------------------------------
def get_assistant_id(bot_id: int) -> Optional[int]:
    bot = clonebotdb.find_one({"bot_id": bot_id})
    if bot:
        return bot.get("assistant")
    return None


def set_assistant_id(bot_id: int, assistant_id: int):
    clonebotdb.update_one(
        {"bot_id": bot_id},
        {"$set": {"assistant": assistant_id}},
        upsert=True
    )


# -------------------------------
# SUPPORT CHAT / CHANNEL
# -------------------------------
async def get_cloned_support_chat(bot_id: int) -> str:
    bot_details = clonebotdb.find_one({"bot_id": bot_id})
    if bot_details:
        return bot_details.get("support", "No support chat set.")
    return "No support chat set."


async def get_cloned_support_channel(bot_id: int) -> str:
    bot_details = clonebotdb.find_one({"bot_id": bot_id})
    if bot_details:
        return bot_details.get("channel", "No channel set.")
    return "No channel set."


# -------------------------------
# USER CLONE CHECK
# -------------------------------
async def has_user_cloned_any_bot(user_id: int) -> bool:
    cloned_bot = clonebotdb.find_one({"user_id": user_id})
    return True if cloned_bot else False


# -------------------------------
# 🔒 CLONE LIMIT SYSTEM
# -------------------------------
def get_user_clone_count(user_id: int) -> int:
    return clonebotdb.count_documents({"user_id": user_id})


def can_clone_more(user_id: int, limit: int = 2) -> bool:
    return get_user_clone_count(user_id) < limit
