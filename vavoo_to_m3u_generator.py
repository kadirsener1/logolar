import json
import requests

def fetch_vavoo_channels():
    # Vavoo'nun güncel kanal listesini ve tokenları dağıttığı ana API uç noktaları
    api_url = "https://www.vavoo.to/live2/index"
    
    # Vavoo sunucularının istekleri reddetmemesi için gerekli başlıklar ve user-agent
    headers = {
        "User-Agent": "VAVOO/2.6",
        "Accept": "*/*",
        "Content-Type": "application/json"
    }
    
    # Sunucuya gönderilecek standart boş doğrulama gövdesi
    payload = {"id": ""}
    
    print("[*] Vavoo API'sine bağlanılıyor ve güncel liste alınıyor...")
    
    try:
        response = requests.post(api_url, data=json.dumps(payload), headers=headers, timeout=15)
        response.raise_for_status()
        
        # Gelen veri genellikle JSON formatında bir kanal listesidir
        channels_data = response.json()
        return channels_data
        
    except requests.exceptions.RequestException as e:
        print(f"[-] Hata oluştu: {e}")
        return None

def generate_m3u(channels):
    if not channels:
        print("[-] İşlenecek kanal verisi bulunamadı.")
        return

    m3u_file_name = "vavoo_channels.m3u"
    
    print(f"[*] M3U dosyası oluşturuluyor: {m3u_file_name}")
    
    with open(m3u_file_name, "w", encoding="utf-8") as f:
        # M3U dosyasının standart başlangıç başlığı
        f.write("#EXTM3U\n")
        
        count = 0
        for channel in channels:
            # Kanal adı ve url bilgisini güvenli bir şekilde çekiyoruz
            name = channel.get("name", "Bilinmeyen Kanal")
            url = channel.get("url")
            group = channel.get("group", "Genel")
            logo = channel.get("logo", "")
            
            if url:
                # IPTV oynatıcıların (VLC, IPTV Smarters vb.) kanalları kategorize edebilmesi için etiketler ekliyoruz
                f.write(f'#EXTINF:-1 tvg-logo="{logo}" group-title="{group}",{name}\n')
                f.write(f"{url}\n")
                count += 1
                
        print(f"[+] Başarılı! {count} adet kanal '{m3u_file_name}' dosyasına yazıldı.")

if __name__ == "__main__":
    # 1. Kanalları ve dinamik linkleri çek
    raw_channels = fetch_vavoo_channels()
    
    # 2. Veriyi işle ve M3U formatına çevir
    generate_m3u(raw_channels)
