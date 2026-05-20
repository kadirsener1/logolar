import json
from datetime import datetime
from pathlib import Path

CONFIG_FILE = "channels.json"
OUTPUT_FILE = "playlist.m3u"


def load_channels(path=CONFIG_FILE):
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"{path} bulunamadı.")

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("channels.json kök yapısı liste olmalı.")

    normalized = []

    for i, item in enumerate(data, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"{i}. kayıt obje olmalı.")

        name = str(item.get("name", "")).strip()
        group = str(item.get("group", "Genel")).strip()
        logo = str(item.get("logo", "")).strip()
        tvg_id = str(item.get("tvg_id", "")).strip()
        stream_url = str(item.get("stream_url", "")).strip()

        if not name:
            print(f"[UYARI] {i}. kayıtta 'name' boş, kayıt atlandı.")
            continue

        if not stream_url:
            print(f"[UYARI] {name}: 'stream_url' boş, kayıt atlandı.")
            continue

        normalized.append({
            "name": name,
            "group": group or "Genel",
            "logo": logo,
            "tvg_id": tvg_id,
            "stream_url": stream_url
        })

    return normalized


def build_extinf(channel):
    name = channel["name"]
    group = channel["group"]
    logo = channel["logo"]
    tvg_id = channel["tvg_id"]

    return (
        f'#EXTINF:-1 tvg-id="{tvg_id}" '
        f'tvg-logo="{logo}" '
        f'group-title="{group}",{name}'
    )


def build_m3u(channels):
    lines = ["#EXTM3U"]

    for ch in channels:
        lines.append(build_extinf(ch))
        lines.append(ch["stream_url"])

    return "\n".join(lines) + "\n"


def main():
    print(f"[{datetime.now()}] channels.json okunuyor...")

    channels = load_channels(CONFIG_FILE)
    print(f"Toplam geçerli kanal: {len(channels)}")

    m3u_content = build_m3u(channels)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(m3u_content)

    print(f"{OUTPUT_FILE} başarıyla oluşturuldu/güncellendi.")


if __name__ == "__main__":
    main()
