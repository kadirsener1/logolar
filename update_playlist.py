import requests
import json
import urllib3
from datetime import datetime
from urllib.parse import urljoin, urlparse

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

OUTPUT_FILE = "playlist.m3u"
PROXY_BASE = "https://vavooproxy.magnitude.workers.dev/resolve?url="

# ===================== KANAL LİSTESİ =====================
# Her kanala şunları yaz:
#   "name"     : Kanal adı
#   "group"    : Grup adı (Spor, Haber, Sinema, vb.)
#   "logo"     : Logo URL'si (boş bırakabilirsin "")
#   "tvg_id"   : EPG ID (boş bırakabilirsin "")
#   "url"      : Vavoo orijinal linki
# ==========================================================

CHANNELS = [
     {
        "name": "beIN Sports 1 HD",
        "group": "Spor",
        "logo": "https://raw.githubusercontent.com/kadirsener1/logolar/refs/heads/master/kanallogolari/beIN-SPORTS-1-HD.png",
        "tvg_id": "beinsports1.tr",
        "url": "https://vavooproxy.magnitude.workers.dev/resolve?url=https://vavoo.to/vavoo-iptv/play/300113394ceebba66c8ad"
    },
    {
        "name": "beIN Sports 2 HD",
        "group": "Spor",
        "logo": "https://raw.githubusercontent.com/kadirsener1/logolar/master/logos/bein2.png",
        "tvg_id": "beinsports2.tr",
        "url": "https://vavoo.to/vavoo-iptv/play/28515391437e928cafd5dd"
    },
    {
        "name": "TRT 1 HD",
        "group": "Ulusal",
        "logo": "https://raw.githubusercontent.com/kadirsener1/logolar/master/logos/trt1.png",
        "tvg_id": "trt1.tr",
        "url": "https://vavoo.to/vavoo-iptv/play/762199258e25181300f62"
    },
    {
        "name": "Show TV",
        "group": "Ulusal",
        "logo": "https://raw.githubusercontent.com/kadirsener1/logolar/master/logos/showtv.png",
        "tvg_id": "showtv.tr",
        "url": "https://vavoo.to/vavoo-iptv/play/2395422638d4ff0c834c1d"
    },
    {
        "name": "CNN Türk",
        "group": "Haber",
        "logo": "https://raw.githubusercontent.com/kadirsener1/logolar/master/logos/cnnturk.png",
        "tvg_id": "cnnturk.tr",
        "url": "https://vavoo.to/vavoo-iptv/play/2056768647bd7eb3f3cf70"
    },
    # ========================================================
    # DAHA FAZLA KANAL EKLEMEK İÇİN AŞAĞIYA KOPYALA YAPIŞTIR:
    # ========================================================
    # {
    #     "name": "Kanal Adı",
    #     "group": "Grup Adı",
    #     "logo": "https://logo-linki.png",
    #     "tvg_id": "epg.id",
    #     "url": "https://vavoo.to/vavoo-iptv/play/KANAL_ID"
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


def resolve_channel(vavoo_url):
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
        vavoo_url = ch["url"]

        print(f"[{i}/{len(CHANNELS)}] {name} çözülüyor...")

        try:
            m3u8_url = resolve_channel(vavoo_url)

            if m3u8_url:
                extinf = f'#EXTINF:-1 tvg-id="{tvg_id}" tvg-logo="{logo}" group-title="{group}",{name}'
                lines.append(extinf)
                lines.append(m3u8_url)
                print(f"  ✅ Başarılı: {m3u8_url[:80]}...")
                success += 1
            else:
                print(f"  ❌ Link bulunamadı, atlanıyor.")
                failed += 1

        except Exception as e:
            print(f"  ❌ Hata: {str(e)[:100]}")
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
