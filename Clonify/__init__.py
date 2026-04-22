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
#  KEEP-ALIVE — Render "No open ports" fix
#  Threading: import hote hi port open — asyncio wait nahi
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class _Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(
            b"<h2>\xf0\x9f\x8e\xb5 Adam Music Bot is running!</h2>"
        )
    def log_message(self, *a):
        pass


def _run_server():
    port = int(os.environ.get("PORT", 8080))
    HTTPServer(("0.0.0.0", port), _Handler).serve_forever()


threading.Thread(target=_run_server, daemon=True).start()
LOGGER("AdamMusicBot").info("Keep-alive server started ✅")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  BOT INIT
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
