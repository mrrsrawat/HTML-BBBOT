from vars import MONGO_URL
from motor.motor_asyncio import AsyncIOMotorClient as MongoCli

mongo = MongoCli(MONGO_URL)
db = mongo.ban           # Database: ban
ban_db = db.ban_db       # Collection: ban_db

async def is_banned(user_id: int) -> bool:
    return await ban_db.find_one({"user_id": user_id}) is not None

async def ban_user_db(user_id: int, name: str, username: str = "N/A"):
    if not await is_banned(user_id):
        await ban_db.insert_one({
            "user_id": user_id,
            "name": name,
            "username": username or "N/A"
        })

async def unban_user_db(user_id: int):
    await ban_db.delete_one({"user_id": user_id})



async def get_ban_list(app):
    banned_users = await ban_db.find().to_list(length=None)
    if not banned_users:
        return "✅ ɴᴏ ᴜsᴇʀs ᴀʀᴇ ʙᴀɴɴᴇᴅ."

    text = f"🚫 ᴛᴏᴛᴀʟ ʙᴀɴɴᴇᴅ ᴜsᴇʀs: {len(banned_users)}\n\n"
    for i, user in enumerate(banned_users, 1):
        try:
            u = await app.get_users(user["user_id"])
            name = u.first_name or "No Name"
            username = f"@{u.username}" if u.username else "No username"
            link = f"[{name}](tg://openmessage?user_id={user['user_id']})"
        except:
            link = "Unknown"
            username = "No username"

        text += f"{i}. {link} | 👤{username} | 🆔`{user['user_id']}`\n\n"

    return text
