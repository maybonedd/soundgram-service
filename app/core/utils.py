import re
from typing import NamedTuple, Optional


class PlaylistInfo(NamedTuple):
    owner: Optional[str]
    kind: str
    is_old_format: bool


def parse_yandex_url(url: str) -> PlaylistInfo:
    old_pattern = r"music\.yandex\.ru/users/([a-zA-Z0-9._-]+)/playlists/([\w-]+)"
    new_pattern = r"music\.yandex\.ru/playlists/([\w-]+)"

    if match := re.search(old_pattern, url):
        return PlaylistInfo(owner=match.group(1), kind=match.group(2), is_old_format=True)

    if match := re.search(new_pattern, url):
        return PlaylistInfo(owner=None, kind=match.group(1), is_old_format=False)

    raise ValueError("Некорректный формат ссылки на плейлист Яндекс Музыки")


def format_cover_url(template: Optional[str], size: str = "400x400") -> Optional[str]:
    if not template:
        return None
    return "https://" + template.replace("%%", size)
