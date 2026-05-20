import json
import requests
import sys

def main():
    print("[*] Vavoo IPTV M3U Playlist Generator")
    target_url = "https://vavooproxy.magnitude.workers.dev/resolve?url=https://vavoo.to/vavoo-iptv/play/2485009235d60801ad626b"
    output_filename = "vavoo_playlist.m3u"
    
    try:
        print(f"[*] Bağlantı test ediliyor: {target_url}")
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(target_url, headers=headers, timeout=10)
        
        # M3U İçeriğini oluştur
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            f.write('#EXTINF:-1 tvg-id="" tvg-name="Vavoo Stream" group-title="Vavoo Canlı",Vavoo Özel Yayın\n')
            f.write(f"{target_url}\n")
            
        print(f"[+] Başarılı! M3U dosyası oluşturuldu: {output_filename}")
    except Exception as e:
        print(f"[-] Hata oluştu: {e}")

if __name__ == '__main__':
    main()
