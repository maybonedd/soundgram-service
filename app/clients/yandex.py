import httpx
from fastapi import HTTPException
from core.utils import PlaylistInfo, format_cover_url


class YandexMusicClient:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept-Language": "ru-RU,ru;q=0.9",
        }

    async def get_playlist_data(self, info: PlaylistInfo) -> dict:
        if info.is_old_format:
            url = f"https://music.yandex.ru/handlers/playlist.jsx?owner={info.owner}&kinds={info.kind}"
        else:
            url = f"https://api.music.yandex.by/playlist/{info.kind}?resumestream=false&richtracks=true"

        async with httpx.AsyncClient(headers=self.headers, timeout=10.0) as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
            except Exception:
                raise HTTPException(status_code=502, detail="Ошибка при получении данных от Яндекс Музыки")

    def process_tracks(self, raw_data: dict) -> list:
        root = raw_data.get("playlist", raw_data)
        raw_tracks = root.get("tracks", []) or root.get("volumes", [{}])[0].get("tracks", [])

        processed = []
        for item in raw_tracks:
            t = item.get("track") if isinstance(item, dict) and item.get("track") else item

            if not isinstance(t, dict) or t.get("error") or not t.get("id"):
                continue

            albums = t.get("albums", [])
            album_id = albums[0].get("id") if (albums and isinstance(albums[0], dict)) else "0"
            track_id = t.get("id")

            artists = [a.get("name") for a in t.get("artists", []) if isinstance(a, dict) and a.get("name")]

            processed.append({
                "title": t.get("title", "Unknown"),
                "artists": artists,
                "cover_url": format_cover_url(t.get("ogImage") or t.get("coverUri")),
                "iframe_code": f'<iframe frameborder="0" style="border:none;width:614px;height:244px;" src="https://music.yandex.ru/iframe/album/{album_id}/track/{track_id}"></iframe>'
            })
        return processed
