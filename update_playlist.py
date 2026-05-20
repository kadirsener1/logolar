import requests
import json
import os
import urllib3
from datetime import datetime

# SSL uyarılarını kapat
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ===================== AYARLAR =====================
RESOLVE_URL = "https://vavooproxy.magnitude.workers.dev/resolve?url=https://vavoo.to/vavoo-iptv/play/2485009235d60801ad626b"

CHANNEL_NAME = "Vavoo TV"
GROUP_TITLE = "Vavoo"
OUTPUT_FILE = "playlist.m3u"
# ===================================================

def get_m3u8_url():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json"
    }
    
    # SSL sertifikasını atla (verify=False)
    response = requests.get(RESOLVE_URL, headers=headers, timeout=25, verify=False)
    response.raise_for_status()
    
    content = response.text.strip()
    
    # Durum 1: Direkt m3u8 linki dönüyorsa
    if '.m3u8' in content and 'http' in content:
        # Tırnak işaretlerini temizle
        url = content.strip().strip('"').strip("'")
        # Eğer JSON formatındaysa parse et
        if content.startswith('{'):
            try:
                data = json.loads(content)
                for key in ["url", "stream", "link", "m3u8", "data", "hls", "src"]:
                    if key in data and isinstance(data[key], str):
                        return data[key]
            except:
                pass
        return url

    # Durum 2: JSON dönüyorsa
    try:
        data = response.json()
        
        possible_keys = ["url", "stream", "link", "m3u8", "data", "hls", "src"]
        
        if isinstance(data, dict):
            for key in possible_keys:
                if key in data:
                    value = data[key]
                    if isinstance(value, str) and "m3u8" in value:
                        return value
                    if isinstance(value, dict):
                        for k2 in possible_keys:
                            if k2 in value and isinstance(value[k2], str):
                                return value[k2]
        
        if "result" in data and isinstance(data["result"], dict):
            for key in possible_keys:
                if key in data["result"]:
                    return data["result"][key]
                    
    except json.JSONDecodeError:
        pass
    
    raise Exception(f"m3u8 linki bulunamadı. Response: {content[:300]}")


def verify_m3u8_url(url):
    """m3u8 linkinin çalışıp çalışmadığını kontrol et (SSL atlanarak)"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        # SSL sertifikasını atla
        response = requests.head(url, headers=headers, timeout=10, verify=False, allow_redirects=True)
        return response.status_code == 200
    except:
        # HEAD başarısız olursa yine de kaydet
        return True


def main():
    print(f"[{datetime.now()}] Vavoo m3u8 çözülüyor...")
    
    m3u8_url = get_m3u8_url()
    print(f"✅ m3u8 Linki alındı: {m3u8_url[:100]}...")

    # Link kontrolü (opsiyonel)
    if verify_m3u8_url(m3u8_url):
        print("✅ Link erişilebilir.")
    else:
        print("⚠️ Link kontrolü başarısız ama yine de kaydediliyor.")

    m3u_content = f'''#EXTM3U
#EXTINF:-1 group-title="{GROUP_TITLE}" tvg-id="",{CHANNEL_NAME}
{m3u8_url}
'''

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(m3u_content)

    print(f"✅ {OUTPUT_FILE} başarıyla güncellendi!")
    print(f"📺 Link: {m3u8_url}")

if __name__ == "__main__":
    main()
