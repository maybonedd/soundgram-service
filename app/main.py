import sys
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import RedirectResponse

sys.path.append(str(Path(__file__).parent))

from core.utils import parse_yandex_url
from clients.yandex import YandexMusicClient
from schemas.playlist import PlaylistResponse

app = FastAPI(title="SOUNDGRAM API")
yandex_client = YandexMusicClient()


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")


@app.get("/api/v1/playlist", response_model=PlaylistResponse)
async def get_playlist(url: str = Query(..., example="https://music.yandex.ru/playlists/1060")):
    try:
        info = parse_yandex_url(url)
        raw_data = await yandex_client.get_playlist_data(info)

        playlist_root = raw_data.get("playlist", raw_data)

        title = playlist_root.get("title", "Без названия")
        owner_data = playlist_root.get("owner")
        owner_name = owner_data.get("name") if isinstance(owner_data, dict) else "Неизвестен"

        return {
            "title": title,
            "owner": owner_name,
            "tracks": yandex_client.process_tracks(raw_data)
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Unhandled error: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
