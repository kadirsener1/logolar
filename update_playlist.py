import requests
import json
import urllib3
from datetime import datetime
from urllib.parse import urljoin, urlparse

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

RESOLVE_URL = "https://vavooproxy.magnitude.workers.dev/resolve?url=https://vavoo.to/vavoo-iptv/play/2485009235d60801ad626b"

CHANNEL_NAME = "Vavoo TV"
GROUP_TITLE = "Vavoo"
OUTPUT_FILE = "playlist.m3u"


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


def get_m3u8_url():
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "*/*"
    }

    session = requests.Session()

    response = session.get(
        RESOLVE_URL,
        headers=headers,
        timeout=30,
        verify=False,
        allow_redirects=True
    )
    response.raise_for_status()

    content = response.text.strip()
    final_url = response.url

    print("Final response.url:", final_url)

    # 1) En önemli durum:
    # Eğer endpoint doğrudan m3u8 içeriği döndürdüyse,
    # gerçek tokenlı link response.url içindedir.
    if content.startswith("#EXTM3U"):
        if final_url and final_url != RESOLVE_URL:
            return final_url

        # response.url değişmediyse redirect history'den çek
        for hist in reversed(response.history):
            location = hist.headers.get("Location")
            if location and (".m3u8" in location or "/sunshine/" in location):
                return make_absolute(location, hist.url)

    # 2) Direkt body içinde tam URL dönüyorsa
    if content.startswith("http") and ".m3u8" in content:
        return make_absolute(content, final_url)

    # 3) Body içinde relative token path dönüyorsa
    if (content.startswith("/") or content.startswith("sunshine/")) and (
        ".m3u8" in content or "/sunshine/" in content
    ):
        return make_absolute(content, final_url)

    # 4) JSON ise içinden çek
    try:
        data = response.json()
        json_url = extract_url_from_json(data, final_url)
        if json_url:
            return json_url
    except Exception:
        pass

    # 5) Redirect geçmişini ayrıca kontrol et
    for hist in reversed(response.history):
        location = hist.headers.get("Location")
        if location and (".m3u8" in location or "/sunshine/" in location):
            return make_absolute(location, hist.url)

    raise Exception(
        "Tokenlı m3u8 linki bulunamadı.\n"
        f"response.url = {final_url}\n"
        f"response.text[:500] = {content[:500]}"
    )


def main():
    print(f"[{datetime.now()}] Tokenlı m3u8 linki çözülüyor...")

    m3u8_url = get_m3u8_url()
    print("Bulunan tokenlı link:", m3u8_url)

    m3u_content = f"""#EXTM3U
#EXTINF:-1 group-title="{GROUP_TITLE}" tvg-id="",{CHANNEL_NAME}
{m3u8_url}
"""

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(m3u_content)

    print(f"{OUTPUT_FILE} güncellendi.")


if __name__ == "__main__":
    main()
