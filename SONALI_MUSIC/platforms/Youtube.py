import asyncio
import os
import re
from typing import Union
import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from py_yt import VideosSearch, Playlist
from SONALI_MUSIC.utils.formatters import time_to_seconds
import aiohttp
from SONALI_MUSIC import LOGGER

API_URL = "https://shrutibots.site"
DOWNLOAD_DIR = "downloads"


async def download_song(link: str) -> str:

    video_id = link.split('v=')[-1].split('&')[0] if 'v=' in link else link

    if not video_id or len(video_id) < 3:
        return None

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    file_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.mp3")

    if os.path.exists(file_path):
        return file_path

    try:

        async with aiohttp.ClientSession() as session:

            params = {"url": video_id, "type": "audio"}

            async with session.get(
                f"{API_URL}/download",
                params=params,
                timeout=aiohttp.ClientTimeout(total=7)
            ) as response:

                if response.status != 200:
                    return None

                data = await response.json()

                token = data.get("download_token")

                if not token:
                    return None

                stream_url = f"{API_URL}/stream/{video_id}?type=audio&token={token}"

                async with session.get(stream_url, timeout=aiohttp.ClientTimeout(total=300)) as file_response:

                    if file_response.status == 302:

                        redirect_url = file_response.headers.get('Location')

                        async with session.get(redirect_url) as final:

                            if final.status != 200:
                                return None

                            with open(file_path, "wb") as f:
                                async for chunk in final.content.iter_chunked(16384):
                                    f.write(chunk)

                    elif file_response.status == 200:

                        with open(file_path, "wb") as f:
                            async for chunk in file_response.content.iter_chunked(16384):
                                f.write(chunk)

                    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                        return file_path

    except Exception:

        if os.path.exists(file_path):
            os.remove(file_path)

        return None


async def download_video(link: str) -> str:

    video_id = link.split('v=')[-1].split('&')[0] if 'v=' in link else link

    if not video_id or len(video_id) < 3:
        return None

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    file_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.mp4")

    if os.path.exists(file_path):
        return file_path

    try:

        async with aiohttp.ClientSession() as session:

            params = {"url": video_id, "type": "video"}

            async with session.get(
                f"{API_URL}/download",
                params=params,
                timeout=aiohttp.ClientTimeout(total=7)
            ) as response:

                if response.status != 200:
                    return None

                data = await response.json()

                token = data.get("download_token")

                if not token:
                    return None

                stream_url = f"{API_URL}/stream/{video_id}?type=video&token={token}"

                async with session.get(stream_url, timeout=aiohttp.ClientTimeout(total=600)) as file_response:

                    if file_response.status == 302:

                        redirect_url = file_response.headers.get('Location')

                        async with session.get(redirect_url) as final:

                            if final.status != 200:
                                return None

                            with open(file_path, "wb") as f:
                                async for chunk in final.content.iter_chunked(16384):
                                    f.write(chunk)

                    elif file_response.status == 200:

                        with open(file_path, "wb") as f:
                            async for chunk in file_response.content.iter_chunked(16384):
                                f.write(chunk)

                    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                        return file_path

    except Exception:

        if os.path.exists(file_path):
            os.remove(file_path)

        return None


class YouTubeAPI:

    def __init__(self):

        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.listbase = "https://youtube.com/playlist?list="


    async def exists(self, link: str, videoid: Union[bool, str] = None):

        if videoid:
            link = self.base + link

        return bool(re.search(self.regex, link))


    async def details(self, link: str, videoid: Union[bool, str] = None):

        if videoid:
            link = self.base + link

        if "&" in link:
            link = link.split("&")[0]

        results = VideosSearch(link, limit=1)

        data = (await results.next()).get("result")

        if not data:
            return None, None, 0, None, None

        r = data[0]

        title = r.get("title")
        duration_min = r.get("duration")
        vidid = r.get("id")

        thumbnail = f"https://img.youtube.com/vi/{vidid}/hqdefault.jpg"

        duration_sec = int(time_to_seconds(duration_min)) if duration_min else 0

        return title, duration_min, duration_sec, thumbnail, vidid


    async def thumbnail(self, link: str, videoid: Union[bool, str] = None):

        if videoid:
            link = self.base + link

        results = VideosSearch(link, limit=1)

        data = (await results.next()).get("result")

        if data:

            vidid = data[0].get("id")

            return f"https://img.youtube.com/vi/{vidid}/hqdefault.jpg"


    async def track(self, link: str, videoid: Union[bool, str] = None):

        if videoid:
            link = self.base + link

        results = VideosSearch(link, limit=1)

        data = (await results.next()).get("result")

        if not data:
            return None, None

        r = data[0]

        vidid = r.get("id")

        track = {

            "title": r.get("title"),
            "link": r.get("link"),
            "vidid": vidid,
            "duration_min": r.get("duration"),
            "thumb": f"https://img.youtube.com/vi/{vidid}/hqdefault.jpg"

        }

        return track, vidid
