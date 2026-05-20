import requests
import json
import urllib3
from datetime import datetime
from urllib.parse import urljoin, urlparse

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

OUTPUT_FILE = "playlist.m3u"
PROXY_BASE = "https://vavooproxy.magnitude.workers.dev/resolve?url="

# ===================== KANAL LİSTESİ =====================
# "urls" → Liste olarak birden fazla URL yazabilirsin
#           İlk çalışan kullanılır, başarısız olursa sonrakine geçer
# ==========================================================

CHANNELS = [
    {
        "name": "beIN 1 HD",
        "group": "Spor",
        "logo": "https://raw.githubusercontent.com/kadirsener1/logolar/master/logos/bein1.png",
        "tvg_id": "beinsports1.tr",
        "urls": [
            "https://vavoo.to/vavoo-iptv/play/1363827223a1c98515d61"
        ]
    },
       {
        "name": "beIN 1 HD",
        "group": "Spor",
        "logo": "https://raw.githubusercontent.com/kadirsener1/logolar/master/logos/bein1.png",
        "tvg_id": "beinsports1.tr",
        "urls": [
            "https://vavoo.to/vavoo-iptv/play/3692337241ec1b0872b06e"
        ]
    },
       {
        "name": "beIN 1 HD",
        "group": "Spor",
        "logo": "https://raw.githubusercontent.com/kadirsener1/logolar/master/logos/bein1.png",
        "tvg_id": "beinsports1.tr",
        "urls": [
            "https://vavoo.to/vavoo-iptv/play/2919229346c4e9a95ddb3f"
        ]
    },
    {
        "name": "beIN Sports 1 HD",
        "group": "Spor",
        "logo": "https://raw.githubusercontent.com/kadirsener1/logolar/master/logos/bein2.png",
        "tvg_id": "beinsports2.tr",
        "urls": [
            "https://vavoo.to/vavoo-iptv/play/300113394ceebba66c8ad"
        ]
    },
      {
        "name": "beIN Sports 1 HD",
        "group": "Spor",
        "logo": "https://raw.githubusercontent.com/kadirsener1/logolar/master/logos/bein2.png",
        "tvg_id": "beinsports2.tr",
        "urls": [
            
            "https://vavoo.to/vavoo-iptv/play/38404756531618c87fcc66"
        ]
    },
      {
        "name": "beIN Sports 1 HD",
        "group": "Spor",
        "logo": "https://raw.githubusercontent.com/kadirsener1/logolar/master/logos/bein2.png",
        "tvg_id": "beinsports2.tr",
        "urls": [
           
            "https://vavoo.to/vavoo-iptv/play/22330664333ebb4acbb6ab"
        ]
    },
      {
        "name": "beIN Sports 1 HD",
        "group": "Spor",
        "logo": "https://raw.githubusercontent.com/kadirsener1/logolar/master/logos/bein2.png",
        "tvg_id": "beinsports2.tr",
        "urls": [
        
            "https://vavoo.to/vavoo-iptv/play/342898470360b159ef8301"
        ]
    },
    {
        "name": "beIN Sports 1 HD (yedek)",
        "group": "Spor",
        "logo": "https://raw.githubusercontent.com/kadirsener1/logolar/master/logos/trt1.png",
        "tvg_id": "trt1.tr",
        "urls": [
            "https://vavoo.to/vavoo-iptv/play/2576216897d1c2b14af4e9"
        ] 
    },
     {
        "name": "beIN Sports 1 HD (yedek)",
        "group": "Spor",
        "logo": "https://raw.githubusercontent.com/kadirsener1/logolar/master/logos/trt1.png",
        "tvg_id": "trt1.tr",
        "urls": [
            
            "https://vavoo.to/vavoo-iptv/play/13524210538e192d878d20"
        ] 
    },
     {
        "name": "beIN Sports 1 HD (yedek)",
        "group": "Spor",
        "logo": "https://raw.githubusercontent.com/kadirsener1/logolar/master/logos/trt1.png",
        "tvg_id": "trt1.tr",
        "urls": [

            "https://vavoo.to/vavoo-iptv/play/2729088606df69156b1eda"
        ] 
    },
    {
        "name": "beIN Sports 1 HD (yedek 2(",
        "group": "Spor",
        "logo": "https://raw.githubusercontent.com/kadirsener1/logolar/master/logos/showtv.png",
        "tvg_id": "showtv.tr",
        "urls": [
            "https://vavoo.to/vavoo-iptv/play/24034250314fd9aa349685"
        ]
    },
        {
        "name": "beIN Sports 1 HD (yedek 2(",
        "group": "Spor",
        "logo": "https://raw.githubusercontent.com/kadirsener1/logolar/master/logos/showtv.png",
        "tvg_id": "showtv.tr",
        "urls": [
           
            "https://vavoo.to/vavoo-iptv/play/66217962033a2d3e9c47f"
        ]
    },
        {
        "name": "beIN Sports 1 HD (yedek 2(",
        "group": "Spor",
        "logo": "https://raw.githubusercontent.com/kadirsener1/logolar/master/logos/showtv.png",
        "tvg_id": "showtv.tr",
        "urls": [
            "https://vavoo.to/vavoo-iptv/play/5934938605e361d7e0ff0"
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
    # ========================================================
    # YENİ KANAL EKLEMEK İÇİN:
    # ========================================================
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

    # 1) Body m3u8 içeriği döndüyse → response.url tokenlı linktir
    if content.startswith("#EXTM3U"):
        if final_url and final_url != resolve_url:
            return final_url
        for hist in reversed(response.history):
            location = hist.headers.get("Location")
            if location and (".m3u8" in location or "/sunshine/" in location):
                return make_absolute(location, hist.url)

    # 2) Direkt URL dönüyorsa
    if content.startswith("http") and ".m3u8" in content:
        return make_absolute(content, final_url)

    # 3) Relative path dönüyorsa
    if (content.startswith("/") or content.startswith("sunshine/")) and (
        ".m3u8" in content or "/sunshine/" in content
    ):
        return make_absolute(content, final_url)

    # 4) JSON ise
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


def resolve_channel(url_list):
    """
    Birden fazla URL dener.
    İlk başarılı olanı döndürür.
    Hepsi başarısız olursa None döner.
    """
    for idx, vavoo_url in enumerate(url_list, 1):
        try:
            print(f"    URL {idx}/{len(url_list)} deneniyor...")
            result = resolve_single_url(vavoo_url)
            if result:
                return result
            else:
                print(f"    URL {idx}: Link çözülemedi, sonraki deneniyor...")
        except Exception as e:
            print(f"    URL {idx}: Hata → {str(e)[:80]}, sonraki deneniyor...")

    return None


def main():
    print(f"[{datetime.now()}] Playlist güncelleniyor...")
    print(f"Toplam {len(CHANNELS)} kanal işlenecek.\n")

    lines = ['#EXTM3U']
    success = 0
    failed = 0

    for i, ch in enumerate(CHANNELS, 1):
        name = ch["name"]
        group = ch.get("group", "Genel")
        logo = ch.get("logo", "")
        tvg_id = ch.get("tvg_id", "")

        # Eski "url" formatını da destekle (tek URL string)
        if "urls" in ch:
            url_list = ch["urls"]
        elif "url" in ch:
            url_list = [ch["url"]]
        else:
            print(f"[{i}/{len(CHANNELS)}] {name}: URL tanımlı değil, atlanıyor.")
            failed += 1
            continue

        print(f"[{i}/{len(CHANNELS)}] {name} çözülüyor ({len(url_list)} URL mevcut)...")

        m3u8_url = resolve_channel(url_list)

        if m3u8_url:
            extinf = (
                f'#EXTINF:-1 tvg-id="{tvg_id}" '
                f'tvg-logo="{logo}" '
                f'group-title="{group}",{name}'
            )
            lines.append(extinf)
            lines.append(m3u8_url)
            print(f"  ✅ {name}: {m3u8_url[:80]}...")
            success += 1
        else:
            print(f"  ❌ {name}: Tüm URL'ler başarısız, atlanıyor.")
            failed += 1

    # M3U dosyasını yaz
    m3u_content = "\n".join(lines) + "\n"

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(m3u_content)

    print(f"\n{'='*50}")
    print(f"✅ Başarılı: {success} kanal")
    print(f"❌ Başarısız: {failed} kanal")
    print(f"📄 {OUTPUT_FILE} güncellendi!")


if __name__ == "__main__":
    main()
