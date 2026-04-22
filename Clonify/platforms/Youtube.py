import asyncio
import os
import re
from typing import Union

import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message

from Clonify.utils.database import is_on_off
from Clonify.utils.formatters import time_to_seconds

cookies_file = f"{os.getcwd()}/cookies/cookies.txt"


async def shell_cmd(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    out, errorz = await proc.communicate()
    if errorz:
        if "unavailable videos are hidden" in (errorz.decode("utf-8")).lower():
            return out.decode("utf-8")
        else:
            return errorz.decode("utf-8")
    return out.decode("utf-8")


# ── yt-dlp options ────────────────────────────────────────────────────────────

def _ydl_opts(extra: dict = None) -> dict:
    """Base yt-dlp options with cookies + Android client (less blocked)."""
    opts = {
        "quiet": True,
        "no_warnings": True,
        "nocheckcertificate": True,
        "geo_bypass": True,
        "source_address": "0.0.0.0",
        "extractor_args": {
            "youtube": {
                "player_client": ["android", "web"],
            }
        },
        "http_headers": {
            "User-Agent": (
                "Mozilla/5.0 (Linux; Android 11; Pixel 5) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.6367.82 Mobile Safari/537.36"
            ),
        },
    }
    # Add cookies if file exists
    if os.path.exists(cookies_file):
        opts["cookiefile"] = cookies_file
    if extra:
        opts.update(extra)
    return opts


def _search_one(query: str) -> dict | None:
    """
    yt-dlp se ek result search karo.
    YouTube URL ho toh directly fetch karo, warna ytsearch use karo.
    """
    is_url = bool(re.match(r"https?://", query))
    search_query = query if is_url else f"ytsearch1:{query}"

    opts = _ydl_opts({"skip_download": True, "noplaylist": True})

    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(search_query, download=False)
        if not info:
            return None
        # Search result list → first entry
        if "entries" in info:
            entries = [e for e in info["entries"] if e]
            if not entries:
                return None
            info = entries[0]
        return info


def _seconds_to_min(seconds: int) -> str:
    """Convert seconds to MM:SS or HH:MM:SS string."""
    if not seconds:
        return "0:00"
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return f"{h}:{m:02}:{s:02}" if h else f"{m}:{s:02}"


class YouTubeAPI:
    def __init__(self):
        self.base     = "https://www.youtube.com/watch?v="
        self.regex    = r"(?:youtube\.com|youtu\.be)"
        self.status   = "https://www.youtube.com/oembed?url="
        self.listbase = "https://youtube.com/playlist?list="
        self.reg      = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    # ── URL helpers ───────────────────────────────────────────────────────────

    async def exists(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        return bool(re.search(self.regex, link))

    async def url(self, message_1: Message) -> Union[str, None]:
        messages = [message_1]
        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)
        text = ""
        offset = None
        length = None
        for message in messages:
            if offset:
                break
            if message.entities:
                for entity in message.entities:
                    if entity.type == MessageEntityType.URL:
                        text = message.text or message.caption
                        offset, length = entity.offset, entity.length
                        break
            elif message.caption_entities:
                for entity in message.caption_entities:
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url
        if offset is None:
            return None
        return text[offset: offset + length]

    # ── Core: details ─────────────────────────────────────────────────────────

    async def details(self, link: str, videoid: Union[bool, str] = None):
        """Returns: title, duration_min, duration_sec, thumbnail, vidid"""
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]

        loop = asyncio.get_event_loop()
        try:
            info = await loop.run_in_executor(None, _search_one, link)
        except Exception as e:
            raise Exception(f"yt-dlp details failed: {e}")

        if not info:
            raise Exception("No results found")

        title        = info.get("title", "Unknown")
        duration_sec = info.get("duration", 0) or 0
        duration_min = _seconds_to_min(duration_sec)
        thumbnail    = info.get("thumbnail", "")
        vidid        = info.get("id", "")

        return title, duration_min, duration_sec, thumbnail, vidid

    # ── title ─────────────────────────────────────────────────────────────────

    async def title(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(None, _search_one, link)
        return info.get("title", "Unknown") if info else "Unknown"

    # ── duration ──────────────────────────────────────────────────────────────

    async def duration(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(None, _search_one, link)
        secs = info.get("duration", 0) if info else 0
        return _seconds_to_min(secs)

    # ── thumbnail ─────────────────────────────────────────────────────────────

    async def thumbnail(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(None, _search_one, link)
        return info.get("thumbnail", "") if info else ""

    # ── track ─────────────────────────────────────────────────────────────────

    async def track(self, link: str, videoid: Union[bool, str] = None):
        """Returns: (track_details dict, vidid)"""
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]

        loop = asyncio.get_event_loop()
        try:
            info = await loop.run_in_executor(None, _search_one, link)
        except Exception as e:
            raise Exception(f"Track fetch failed: {e}")

        if not info:
            raise Exception("No track found")

        duration_sec = info.get("duration", 0) or 0
        vidid        = info.get("id", "")
        track_details = {
            "title":        info.get("title", "Unknown"),
            "link":         info.get("webpage_url", self.base + vidid),
            "vidid":        vidid,
            "duration_min": _seconds_to_min(duration_sec),
            "thumb":        info.get("thumbnail", ""),
        }
        return track_details, vidid

    # ── slider (10 results for inline search) ─────────────────────────────────

    async def slider(
        self,
        link: str,
        query_type: int,
        videoid: Union[bool, str] = None,
    ):
        """Returns: title, duration_min, thumbnail, vidid for result[query_type]"""
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]

        search_query = link if re.match(r"https?://", link) else f"ytsearch10:{link}"
        opts = _ydl_opts({"skip_download": True, "noplaylist": True})

        loop = asyncio.get_event_loop()

        def _fetch():
            with yt_dlp.YoutubeDL(opts) as ydl:
                return ydl.extract_info(search_query, download=False)

        try:
            data = await loop.run_in_executor(None, _fetch)
        except Exception as e:
            raise Exception(f"Slider search failed: {e}")

        entries = data.get("entries", []) if data else []
        entries = [e for e in entries if e]

        # Clamp index
        idx = min(query_type, len(entries) - 1) if entries else 0
        if not entries:
            raise Exception("No slider results")

        result       = entries[idx]
        duration_sec = result.get("duration", 0) or 0
        return (
            result.get("title", "Unknown"),
            _seconds_to_min(duration_sec),
            result.get("thumbnail", ""),
            result.get("id", ""),
        )

    # ── video (direct stream URL) ─────────────────────────────────────────────

    async def video(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]

        cookies_args = ["--cookies", cookies_file] if os.path.exists(cookies_file) else []
        proc = await asyncio.create_subprocess_exec(
            "yt-dlp",
            *cookies_args,
            "-g",
            "-f", "best[height<=?720][width<=?1280]",
            link,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        if stdout:
            return 1, stdout.decode().split("\n")[0]
        return 0, stderr.decode()

    # ── playlist ──────────────────────────────────────────────────────────────

    async def playlist(self, link, limit, user_id, videoid: Union[bool, str] = None):
        if videoid:
            link = self.listbase + link
        if "&" in link:
            link = link.split("&")[0]

        cookies_args = f"--cookies {cookies_file}" if os.path.exists(cookies_file) else ""
        playlist = await shell_cmd(
            f"yt-dlp {cookies_args} -i --get-id --flat-playlist "
            f"--playlist-end {limit} --skip-download {link}"
        )
        try:
            result = [x for x in playlist.split("\n") if x.strip()]
        except Exception:
            result = []
        return result

    # ── formats ───────────────────────────────────────────────────────────────

    async def formats(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]

        opts = _ydl_opts()
        loop = asyncio.get_event_loop()

        def _fetch():
            with yt_dlp.YoutubeDL(opts) as ydl:
                return ydl.extract_info(link, download=False)

        r = await loop.run_in_executor(None, _fetch)
        formats_available = []
        for fmt in (r.get("formats") or []):
            try:
                if "dash" in str(fmt.get("format", "")).lower():
                    continue
                if not all(k in fmt for k in ("format", "filesize", "format_id", "ext", "format_note")):
                    continue
                formats_available.append({
                    "format":      fmt["format"],
                    "filesize":    fmt["filesize"],
                    "format_id":   fmt["format_id"],
                    "ext":         fmt["ext"],
                    "format_note": fmt["format_note"],
                    "yturl":       link,
                })
            except Exception:
                continue
        return formats_available, link

    # ── download ──────────────────────────────────────────────────────────────

    async def download(
        self,
        link: str,
        mystic,
        video: Union[bool, str] = None,
        videoid: Union[bool, str] = None,
        songaudio: Union[bool, str] = None,
        songvideo: Union[bool, str] = None,
        format_id: Union[bool, str] = None,
        title: Union[bool, str] = None,
    ) -> str:
        if videoid:
            link = self.base + link

        loop = asyncio.get_running_loop()
        base_opts = _ydl_opts()

        def audio_dl():
            opts = {
                **base_opts,
                "format": "bestaudio/best",
                "outtmpl": "downloads/%(id)s.%(ext)s",
            }
            with yt_dlp.YoutubeDL(opts) as x:
                info = x.extract_info(link, False)
                xyz  = os.path.join("downloads", f"{info['id']}.{info['ext']}")
                if os.path.exists(xyz):
                    return xyz
                x.download([link])
                return xyz

        def video_dl():
            opts = {
                **base_opts,
                "format": "(bestvideo[height<=?720][width<=?1280][ext=mp4])+(bestaudio[ext=m4a])",
                "outtmpl": "downloads/%(id)s.%(ext)s",
            }
            with yt_dlp.YoutubeDL(opts) as x:
                info = x.extract_info(link, False)
                xyz  = os.path.join("downloads", f"{info['id']}.{info['ext']}")
                if os.path.exists(xyz):
                    return xyz
                x.download([link])
                return xyz

        def song_video_dl():
            opts = {
                **base_opts,
                "format": f"{format_id}+140",
                "outtmpl": f"downloads/{title}",
                "prefer_ffmpeg": True,
                "merge_output_format": "mp4",
            }
            with yt_dlp.YoutubeDL(opts) as x:
                x.download([link])

        def song_audio_dl():
            opts = {
                **base_opts,
                "format": format_id,
                "outtmpl": f"downloads/{title}.%(ext)s",
                "prefer_ffmpeg": True,
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }],
            }
            with yt_dlp.YoutubeDL(opts) as x:
                x.download([link])

        if songvideo:
            await loop.run_in_executor(None, song_video_dl)
            return f"downloads/{title}.mp4"
        elif songaudio:
            await loop.run_in_executor(None, song_audio_dl)
            return f"downloads/{title}.mp3"
        elif video:
            if await is_on_off(1):
                downloaded_file = await loop.run_in_executor(None, video_dl)
                return downloaded_file, True
            else:
                cookies_args = ["--cookies", cookies_file] if os.path.exists(cookies_file) else []
                proc = await asyncio.create_subprocess_exec(
                    "yt-dlp", *cookies_args,
                    "-g", "-f", "best[height<=?720][width<=?1280]",
                    link,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                stdout, stderr = await proc.communicate()
                if stdout:
                    return stdout.decode().split("\n")[0], None
                return None
        else:
            downloaded_file = await loop.run_in_executor(None, audio_dl)
            return downloaded_file, True
    
