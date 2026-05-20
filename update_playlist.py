import requests
import json
import os
from datetime import datetime

# ===================== AYARLAR =====================
RESOLVE_URL = "https://vavooproxy.magnitude.workers.dev/resolve?url=https://vavoo.to/vavoo-iptv/play/2485009235d60801ad626b"

CHANNEL_NAME = "Vavoo TV"          # İstediğin kanal adını buraya yaz
GROUP_TITLE = "Vavoo"              # Grup ismi
OUTPUT_FILE = "playlist.m3u"
# ===================================================

def get_m3u8_url():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json"
    }
    
    response = requests.get(RESOLVE_URL, headers=headers, timeout=25)
    response.raise_for_status()
    
    content = response.text.strip()
    
    # Durum 1: Direkt m3u8 linki dönüyorsa
    if content.endswith(('.m3u8', '.ts')) and ('http' in content):
        return content.strip('"')

    # Durum 2: JSON dönüyorsa
    try:
        data = response.json()
        
        # Olası anahtarlar (birden fazla proxy'de test edildi)
        possible_keys = ["url", "stream", "link", "m3u8", "data", "hls", "src"]
        
        if isinstance(data, dict):
            for key in possible_keys:
                if key in data:
                    value = data[key]
                    if isinstance(value, str) and ("m3u8" in value or value.endswith(('.m3u8', '.ts'))):
                        return value
                    # İç içe dict olabilir
                    if isinstance(value, dict):
                        for k2 in possible_keys:
                            if k2 in value and isinstance(value[k2], str):
                                return value[k2]
        
        # Bazen "result" veya "response" içinde olabilir
        if "result" in data and isinstance(data["result"], dict):
            for key in possible_keys:
                if key in data["result"]:
                    return data["result"][key]
                    
    except json.JSONDecodeError:
        pass
    
    raise Exception(f"m3u8 linki bulunamadı. Response: {content[:200]}")


def main():
    print(f"[{datetime.now()}] Vavoo m3u8 çözülüyor...")
    
    m3u8_url = get_m3u8_url()
    print(f"✅ m3u8 Linki alındı: {m3u8_url[:80]}...")

    m3u_content = f'''#EXTM3U
#EXTINF:-1 group-title="{GROUP_TITLE}" tvg-id="", {CHANNEL_NAME}
{m3u8_url}
'''

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(m3u_content)

    print(f"✅ {OUTPUT_FILE} başarıyla oluşturuldu/güncellendi.")

if __name__ == "__main__":
    main()
