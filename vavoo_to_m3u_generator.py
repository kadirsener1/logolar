import requests
import re
import json
from urllib.parse import urljoin, urlparse
import time

def find_stream_url(target_url):
    """URL'yi tarayıp içindeki yayın linkini bulur"""
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://vavoo.to/',
        'Origin': 'https://vavoo.to',
        'Connection': 'keep-alive',
    }
    
    stream_urls = []
    
    print(f"[*] URL taranıyor: {target_url}")
    
    try:
        # İlk isteği yap
        response = requests.get(target_url, headers=headers, timeout=30, allow_redirects=True)
        
        print(f"[*] Status Code: {response.status_code}")
        print(f"[*] Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        print(f"[*] Final URL: {response.url}")
        
        content = response.text
        
        # 1. M3U8 linklerini ara
        m3u8_patterns = [
            r'https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*',
            r'src["\']?\s*:\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
            r'file["\']?\s*:\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
            r'stream["\']?\s*:\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
            r'url["\']?\s*:\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
            r'source["\']?\s*:\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
        ]
        
        for pattern in m3u8_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if match not in stream_urls:
                    stream_urls.append(match)
                    print(f"[+] M3U8 bulundu: {match}")
        
        # 2. RTMP/RTSP linklerini ara
        rtmp_pattern = r'(rtmp[s]?://[^\s"\'<>]+)'
        rtmp_matches = re.findall(rtmp_pattern, content, re.IGNORECASE)
        for match in rtmp_matches:
            if match not in stream_urls:
                stream_urls.append(match)
                print(f"[+] RTMP bulundu: {match}")
        
        # 3. HLS linklerini ara
        hls_pattern = r'(https?://[^\s"\'<>]*(?:hls|live|stream|play)[^\s"\'<>]*)'
        hls_matches = re.findall(hls_pattern, content, re.IGNORECASE)
        for match in hls_matches:
            if match not in stream_urls and len(match) > 20:
                stream_urls.append(match)
                print(f"[+] HLS benzeri link bulundu: {match}")
        
        # 4. JSON içinde stream ara
        try:
            json_data = response.json()
            json_str = json.dumps(json_data)
            
            for pattern in m3u8_patterns:
                matches = re.findall(pattern, json_str, re.IGNORECASE)
                for match in matches:
                    if match not in stream_urls:
                        stream_urls.append(match)
                        print(f"[+] JSON'dan M3U8 bulundu: {match}")
            
            # JSON'da 'url', 'stream', 'source' anahtarlarını ara
            def search_json(obj, path=""):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        if key.lower() in ['url', 'stream', 'source', 'file', 'link', 'hls', 'src']:
                            if isinstance(value, str) and ('http' in value or 'rtmp' in value):
                                if value not in stream_urls:
                                    stream_urls.append(value)
                                    print(f"[+] JSON key '{key}': {value}")
                        search_json(value, f"{path}.{key}")
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        search_json(item, f"{path}[{i}]")
            
            search_json(json_data)
            
        except json.JSONDecodeError:
            pass
        
        # 5. Content-Type kontrolü - direkt stream ise
        content_type = response.headers.get('Content-Type', '')
        if 'application/vnd.apple.mpegurl' in content_type or \
           'application/x-mpegURL' in content_type or \
           '#EXTM3U' in content:
            if response.url not in stream_urls:
                stream_urls.append(response.url)
                print(f"[+] Direkt M3U8 stream bulundu: {response.url}")
        
        # 6. Redirect kontrolü
        if response.history:
            for redirect in response.history:
                print(f"[*] Redirect: {redirect.url} -> {redirect.headers.get('Location', '')}")
                redirect_url = redirect.headers.get('Location', '')
                if redirect_url and ('.m3u8' in redirect_url or 'stream' in redirect_url.lower()):
                    if redirect_url not in stream_urls:
                        stream_urls.append(redirect_url)
                        print(f"[+] Redirect'ten stream bulundu: {redirect_url}")
        
    except requests.exceptions.RequestException as e:
        print(f"[!] İstek hatası: {e}")
    
    return stream_urls


def resolve_vavoo_stream(url):
    """Vavoo proxy üzerinden stream linkini çöz"""
    
    headers = {
        'User-Agent': 'VAVOO/2.6 (Android)',
        'Accept': '*/*',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30, allow_redirects=True)
        
        # Final URL'i kontrol et
        final_url = response.url
        if '.m3u8' in final_url or 'stream' in final_url.lower():
            return final_url
        
        content = response.text
        
        # M3U8 ara
        m3u8_match = re.search(r'https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*', content)
        if m3u8_match:
            return m3u8_match.group(0)
        
        return final_url
        
    except Exception as e:
        print(f"[!] Resolve hatası: {e}")
        return url


def save_to_m3u(stream_urls, channel_name="Vavoo Channel", output_file="vavoo_streams.m3u"):
    """Stream URL'lerini M3U dosyasına kaydet"""
    
    if not stream_urls:
        print("[!] Kaydedilecek stream URL'si bulunamadı!")
        return
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('#EXTM3U\n')
        f.write(f'# Generated by Vavoo Stream Finder - {time.strftime("%Y-%m-%d %H:%M:%S")}\n\n')
        
        for i, url in enumerate(stream_urls):
            channel_num = i + 1
            f.write(f'#EXTINF:-1 tvg-id="vavoo{channel_num}" tvg-name="{channel_name} {channel_num}" group-title="Vavoo",{channel_name} {channel_num}\n')
            f.write(f'{url}\n\n')
    
    print(f"\n[✓] {len(stream_urls)} stream URL'si '{output_file}' dosyasına kaydedildi!")


def main():
    # Hedef URL
    target_url = "https://vavooproxy.magnitude.workers.dev/resolve?url=https://vavoo.to/vavoo-iptv/play/2485009235d60801ad626b"
    
    print("=" * 60)
    print("  VAVOO STREAM BULUCU")
    print("=" * 60)
    print()
    
    # Stream URL'lerini bul
    stream_urls = find_stream_url(target_url)
    
    # Vavoo özel çözümleyiciyi dene
    print("\n[*] Vavoo özel çözümleyici deneniyor...")
    resolved_url = resolve_vavoo_stream(target_url)
    if resolved_url and resolved_url not in stream_urls:
        stream_urls.append(resolved_url)
        print(f"[+] Çözümlendi: {resolved_url}")
    
    # Sonuçları göster
    print("\n" + "=" * 60)
    print(f"  BULUNAN STREAM URL'LERİ: {len(stream_urls)}")
    print("=" * 60)
    
    for i, url in enumerate(stream_urls, 1):
        print(f"{i}. {url}")
    
    # M3U dosyasına kaydet
    save_to_m3u(stream_urls, channel_name="Vavoo TV", output_file="vavoo_streams.m3u")
    
    # M3U içeriğini göster
    print("\n[*] M3U Dosyası İçeriği:")
    print("-" * 40)
    try:
        with open("vavoo_streams.m3u", 'r', encoding='utf-8') as f:
            print(f.read())
    except:
        pass


if __name__ == "__main__":
    main()
