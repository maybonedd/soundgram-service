import httpx
from fastapi import HTTPException
from core.utils import PlaylistInfo, format_cover_url

class YandexMusicClient:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept": "application/json",
        }

    async def get_playlist_data(self, info: PlaylistInfo) -> dict:
        if info.is_old_format:
            url = f"https://music.yandex.ru/handlers/playlist.jsx?owner={info.owner}&kinds={info.kind}"
        else:
            url = f"https://music.yandex.ru/handlers/playlist.jsx?kinds={info.kind}"
        
        try:
            async with httpx.AsyncClient(headers=self.headers, timeout=10.0, follow_redirects=True) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="Таймаут при запросе к Яндекс Музыке")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise HTTPException(status_code=404, detail="Плейлист не найден или недоступен")
            raise HTTPException(status_code=502, detail=f"Ошибка от Яндекс Музыки: {e.response.status_code}")
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Ошибка при получении данных: {str(e)}")

    def process_tracks(self, raw_data: dict) -> list:
        playlist = raw_data.get("playlist", raw_data)
        tracks = playlist.get("tracks", [])
        processed = []
        
        for item in tracks:
            track = item.get("track") if isinstance(item, dict) and "track" in item else item
            if not isinstance(track, dict) or not track.get("id"):
                continue
            
            album = track.get("albums", [{}])[0]
            album_id = album.get("id", "0")
            artists = [a.get("name") for a in track.get("artists", []) if a.get("name")]
            
            cover_url = None
            if album.get("coverUri"):
                cover_url = format_cover_url(album["coverUri"])
            elif track.get("coverUri"):
                cover_url = format_cover_url(track["coverUri"])
            
            processed.append({
                "title": track.get("title", "Unknown"),
                "artists": artists,
                "cover_url": cover_url,
                "iframe_code": f'<iframe frameborder="0" style="border:none;width:614px;height:244px;" src="https://music.yandex.ru/iframe/album/{album_id}/track/{track["id"]}"></iframe>'
            })
        
        return processed
