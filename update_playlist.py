import requests
import json
import re
import urllib3
from datetime import datetime
from urllib.parse import urljoin, urlparse

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

OUTPUT_FILE = "playlist.m3u"
PROXY_BASE = "https://vavooproxy.magnitude.workers.dev/resolve?url="

# ===================== KANAL LİSTESİ =====================
CHANNELS = [
    {
        "name": "beIN Sports 1 HD",
        "group": "Spor",
        "logo": "https://raw.githubusercontent.com/kadirsener1/logolar/master/logos/bein1.png",
        "tvg_id": "beinsports1.tr",
        "urls": [
            "https://vavoo.to/vavoo-iptv/play/300113394ceebba66c8ad",
            "https://vavoo.to/vavoo-iptv/play/38404756531618c87fcc66",
            "https://vavoo.to/vavoo-iptv/play/22330664333ebb4acbb6ab",
            "https://vavoo.to/vavoo-iptv/play/342898470360b159ef8301"
        ]
    },
    {
        "name": "beIN Sports 2 HD",
        "group": "Spor",
        "logo": "https://raw.githubusercontent.com/kadirsener1/logolar/master/logos/bein2.png",
        "tvg_id": "beinsports2.tr",
        "urls": [
            "https://vavoo.to/vavoo-iptv/play/BIRINCI_ID",
            "https://vavoo.to/vavoo-iptv/play/IKINCI_ID"
        ]
    },
    {
        "name": "TRT 1 HD",
        "group": "Ulusal",
        "logo": "https://raw.githubusercontent.com/kadirsener1/logolar/master/logos/trt1.png",
        "tvg_id": "trt1.tr",
        "urls": [
            "https://vavoo.to/vavoo-iptv/play/TRT1_ID_1",
            "https://vavoo.to/vavoo-iptv/play/TRT1_ID_2"
        ]
    },
    {
        "name": "Show TV",
        "group": "Ulusal",
        "logo": "https://raw.githubusercontent.com/kadirsener1/logolar/master/logos/showtv.png",
        "tvg_id": "showtv.tr",
        "urls": [
            "https://vavoo.to/vavoo-iptv/play/SHOW_ID_1"
        ]
    },
    {
        "name": "CNN Türk",
        "group": "Haber",
        "logo": "https://raw.githubusercontent.com/kadirsener1/logolar/master/logos/cnnturk.png",
        "tvg_id": "cnnturk.tr",
        "urls": [
            "https://vavoo.to/vavoo-iptv/play/CNN_ID_1",
            "https://vavoo.to/vavoo-iptv/play/CNN_ID_2",
            "https://vavoo.to/vavoo-iptv/play/CNN_ID_3"
        ]
    },
    # {
    #     "name": "Kanal Adı",
    #     "group": "Grup",
    #     "logo": "https://logo.png",
    #     "tvg_id": "epg.id",
    #     "urls": [
    #         "https://vavoo.to/vavoo-iptv/play/ANA_ID",
    #         "https://vavoo.to/vavoo-iptv/play/YEDEK_ID"
    #     ]
    # },
]


# ===================== YARDIMCI FONKSİYONLAR =====================

def make_absolute(url, base_url):
    if not url:
        return None
    url = url.strip().strip('"').strip("'")
    if url.startswith("http://") or url.startswith("https://"):
        return url
    if url.startswith("/"):
        parsed = urlparse(base_url)
        return f"{parsed.scheme}://{parsed.netloc}{url}"
    return urljoin(base_url, url)


def extract_url_from_json(data, base_url):
    if isinstance(data, dict):
        for _, value in data.items():
            result = extract_url_from_json(value, base_url)
            if result:
                return result
    elif isinstance(data, list):
        for item in data:
            result = extract_url_from_json(item, base_url)
            if result:
                return result
    elif isinstance(data, str):
        text = data.strip()
        if ".m3u8" in text or "/sunshine/" in text:
            return make_absolute(text, base_url)
    return None


# ===================== URL ÇÖZME =====================

def resolve_single_url(vavoo_url):
    resolve_url = PROXY_BASE + vavoo_url

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "*/*"
    }

    session = requests.Session()
    response = session.get(
        resolve_url,
        headers=headers,
        timeout=30,
        verify=False,
        allow_redirects=True
    )
    response.raise_for_status()

    content = response.text.strip()
    final_url = response.url

    # 1) Body m3u8 içeriği döndüyse
    if content.startswith("#EXTM3U"):
        if final_url and final_url != resolve_url:
            return final_url
        for hist in reversed(response.history):
            location = hist.headers.get("Location")
            if location and (".m3u8" in location or "/sunshine/" in location):
                return make_absolute(location, hist.url)

    # 2) Direkt URL
    if content.startswith("http") and ".m3u8" in content:
        return make_absolute(content, final_url)

    # 3) Relative path
    if (content.startswith("/") or content.startswith("sunshine/")) and (
        ".m3u8" in content or "/sunshine/" in content
    ):
        return make_absolute(content, final_url)

    # 4) JSON
    try:
        data = response.json()
        json_url = extract_url_from_json(data, final_url)
        if json_url:
            return json_url
    except Exception:
        pass

    # 5) Redirect history
    for hist in reversed(response.history):
        location = hist.headers.get("Location")
        if location and (".m3u8" in location or "/sunshine/" in location):
            return make_absolute(location, hist.url)

    return None


# ===================== ÇÖZÜNÜRLÜK TESPİTİ =====================

def get_max_resolution(m3u8_url):
    """
    m3u8 master playlist'ini indir ve içindeki
    en yüksek çözünürlüklü stream URL'sini bul.

    Döndürür: (resolution_height, best_stream_url)
    Örnek:    (1080, "https://.../1080p/index.m3u8")

    Eğer master playlist değilse (tek kalite):
    Döndürür: (0, m3u8_url)  → orijinal URL'yi aynen kullan
    """
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(
            m3u8_url,
            headers=headers,
            timeout=15,
            verify=False
        )
        response.raise_for_status()
        content = response.text.strip()

        # Master playlist mi kontrol et
        if "#EXT-X-STREAM-INF" not in content:
            # Tek kalite stream, çözünürlük bilinmiyor
            # Ama stream çalışıyor demektir
            return (0, m3u8_url)

        # Master playlist → tüm kaliteleri çek
        best_height = 0
        best_url = None

        lines = content.split("\n")
        for i, line in enumerate(lines):
            line = line.strip()

            if line.startswith("#EXT-X-STREAM-INF"):
                height = 0

                # RESOLUTION=1920x1080 formatından yüksekliği çek
                res_match = re.search(r'RESOLUTION=\d+x(\d+)', line)
                if res_match:
                    height = int(res_match.group(1))

                # BANDWIDTH değerinden de tahmini çözünürlük
                if height == 0:
                    bw_match = re.search(r'BANDWIDTH=(\d+)', line)
                    if bw_match:
                        bandwidth = int(bw_match.group(1))
                        if bandwidth > 5000000:
                            height = 1080
                        elif bandwidth > 2500000:
                            height = 720
                        elif bandwidth > 1000000:
                            height = 576
                        elif bandwidth > 500000:
                            height = 480
                        else:
                            height = 360

                # Sonraki satır stream URL'sidir
                if i + 1 < len(lines):
                    stream_line = lines[i + 1].strip()
                    if stream_line and not stream_line.startswith("#"):
                        stream_url = make_absolute(stream_line, m3u8_url)

                        if height > best_height:
                            best_height = height
                            best_url = stream_url

        if best_url:
            return (best_height, best_url)
        else:
            return (0, m3u8_url)

    except Exception as e:
        # m3u8 içeriği okunamazsa orijinal URL'yi döndür
        print(f"      ⚠️ Çözünürlük kontrolü başarısız: {str(e)[:60]}")
        return (0, m3u8_url)


# ===================== KANAL ÇÖZME (TÜM URL'LER) =====================

def resolve_channel_best(url_list):
    """
    Tüm URL'leri dener.
    Her birinin çözünürlüğünü tespit eder.
    En yüksek çözünürlüklü olanı döndürür.
    """
    candidates = []

    for idx, vavoo_url in enumerate(url_list, 1):
        try:
            print(f"    URL {idx}/{len(url_list)} deneniyor...")
            m3u8_url = resolve_single_url(vavoo_url)

            if not m3u8_url:
                print(f"    URL {idx}: Çözülemedi, sonraki...")
                continue

            print(f"    URL {idx}: Çözüldü → çözünürlük kontrol ediliyor...")

            height, best_stream = get_max_resolution(m3u8_url)

            res_label = f"{height}p" if height > 0 else "bilinmiyor"
            print(f"    URL {idx}: ✅ Çözünürlük: {res_label}")

            candidates.append({
                "height": height,
                "master_url": m3u8_url,
                "best_stream": best_stream
            })

        except Exception as e:
            print(f"    URL {idx}: ❌ Hata → {str(e)[:80]}")

    if not candidates:
        return None, 0

    # En yüksek çözünürlüklü olanı seç
    best = max(candidates, key=lambda x: x["height"])

    return best["master_url"], best["height"]


# ===================== ANA FONKSİYON =====================

def main():
    print(f"[{datetime.now()}] Playlist güncelleniyor...")
    print(f"Toplam {len(CHANNELS)} kanal işlenecek.")
    print(f"Mod: En yüksek çözünürlük seçimi aktif\n")

    lines = ['#EXTM3U']
    success = 0
    failed = 0
    results = []

    for i, ch in enumerate(CHANNELS, 1):
        name = ch["name"]
        group = ch.get("group", "Genel")
        logo = ch.get("logo", "")
        tvg_id = ch.get("tvg_id", "")

        # Eski "url" formatını da destekle
        if "urls" in ch:
            url_list = ch["urls"]
        elif "url" in ch:
            url_list = [ch["url"]]
        else:
            print(f"[{i}/{len(CHANNELS)}] {name}: URL tanımlı değil, atlanıyor.")
            failed += 1
            continue

        print(f"[{i}/{len(CHANNELS)}] {name} ({len(url_list)} URL taranıyor)...")

        m3u8_url, height = resolve_channel_best(url_list)

        if m3u8_url:
            res_label = f"{height}p" if height > 0 else "?"
            extinf = (
                f'#EXTINF:-1 tvg-id="{tvg_id}" '
                f'tvg-logo="{logo}" '
                f'group-title="{group}",{name}'
            )
            lines.append(extinf)
            lines.append(m3u8_url)
            print(f"  ✅ {name} → {res_label} → {m3u8_url[:70]}...\n")
            results.append(f"  {name}: {res_label}")
            success += 1
        else:
            print(f"  ❌ {name}: Tüm URL'ler başarısız.\n")
            failed += 1

    # M3U dosyasını yaz
    m3u_content = "\n".join(lines) + "\n"

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(m3u_content)

    print(f"{'='*50}")
    print(f"📊 SONUÇ RAPORU")
    print(f"{'='*50}")
    print(f"✅ Başarılı: {success} kanal")
    print(f"❌ Başarısız: {failed} kanal")
    print(f"{'='*50}")
    if results:
        print("📺 Seçilen çözünürlükler:")
        for r in results:
            print(r)
    print(f"{'='*50}")
    print(f"📄 {OUTPUT_FILE} güncellendi!")


if __name__ == "__main__":
    main()
