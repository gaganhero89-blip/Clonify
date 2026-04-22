import asyncio
import importlib

from pyrogram import idle
from pytgcalls.exceptions import NoActiveGroupCall

import config
from Clonify import LOGGER, app, userbot
from Clonify.core.call import PRO
from Clonify.misc import sudo
from Clonify.plugins import ALL_MODULES
from Clonify.utils.database import get_banned_users, get_gbanned
from config import BANNED_USERS
from Clonify.plugins.tools.clone import restart_bots


async def init():
    if not config.STRING1:
        LOGGER(__name__).error(
            "String Session not filled! Please add STRING1 in environment variables."
        )
        exit()

    await sudo()

    try:
        users = await get_gbanned()
        for user_id in users:
            BANNED_USERS.add(user_id)
        users = await get_banned_users()
        for user_id in users:
            BANNED_USERS.add(user_id)
    except Exception:
        pass

    await app.start()

    for module in ALL_MODULES:
        importlib.import_module("Clonify.plugins" + module)
    LOGGER("Clonify.plugins").info("All Features Loaded 🎵")

    await userbot.start()
    await PRO.start()

    try:
        await PRO.stream_call("https://te.legra.ph/file/29f784eb49d230ab62e9e.mp4")
    except NoActiveGroupCall:
        LOGGER("AdamMusicBot").error(
            "Please START your LOG GROUP VOICE CHAT first!\n\nBot Stopping..."
        )
        exit()
    except Exception:
        pass

    await PRO.decorators()
    await restart_bots()

    LOGGER("AdamMusicBot").info(
        "\n╔══════════════════════╗"
        "\n║  🎵  ADAM MUSIC BOT  ║"
        "\n║   Powered by Clonify ║"
        "\n╚══════════════════════╝"
    )

    await idle()
    await app.stop()
    await userbot.stop()
    LOGGER("AdamMusicBot").info("Adam Music Bot stopped.")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(init())
    
