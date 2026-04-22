import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from Clonify.core.bot import PRO
from Clonify.core.dir import dirr
from Clonify.core.git import git
from Clonify.core.userbot import Userbot
from Clonify.misc import dbb, heroku
from pyrogram import Client
from SafoneAPI import SafoneAPI
from .logging import LOGGER


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  KEEP-ALIVE — Import hote hi port open ho jaata hai
#  Threading use kiya — asyncio/bot ka wait nahi karta
#  Render port scan: import → thread start → port open ✅
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class _KeepAliveHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Clonify Music Bot is running!")

    def log_message(self, format, *args):
        pass  # Suppress HTTP logs


def _run_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), _KeepAliveHandler)
    LOGGER("KeepAlive").info(f"Server started on port {port} ✅")
    server.serve_forever()


# Immediately start in background thread
_server_thread = threading.Thread(target=_run_server, daemon=True)
_server_thread.start()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ORIGINAL — bilkul same, koi change nahi
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

dirr()
git()
dbb()
heroku()

app      = PRO()
api      = SafoneAPI()
userbot  = Userbot()

from .platforms import *

Apple      = AppleAPI()
Carbon     = CarbonAPI()
SoundCloud = SoundAPI()
Spotify    = SpotifyAPI()
Resso      = RessoAPI()
Telegram   = TeleAPI()
YouTube    = YouTubeAPI()
