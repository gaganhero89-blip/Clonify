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
#  KEEP-ALIVE — Thread mein chalata hai asyncio se pehle
#  Render port scan turant karta hai — isliye pehle open
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class _Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(b"<h2>Clonify Music Bot is running!</h2>")

    def log_message(self, format, *args):
        pass  # suppress logs


def _start_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), _Handler)
    LOGGER("KeepAlive").info(f"Server started on port {port} ✅")
    server.serve_forever()


# Thread mein start — bot startup ka wait nahi karega
_thread = threading.Thread(target=_start_server, daemon=True)
_thread.start()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ORIGINAL — bilkul same
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
