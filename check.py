import socket
import subprocess
import time
import requests
from datetime import datetime

def check_port(port=8888):
    """Zkontroluje, zda port 8888 je obsazený"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            result = s.connect_ex(('127.0.0.1', port))
            return result == 0
    except:
        return False

def check_pythonw_processes():
    """Zkontroluje běžící pythonw procesy"""
    pythonw_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'create_time']):
        try:
            if 'pythonw' in proc.info['name'].lower():
                pythonw_processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return pythonw_processes

def check_web_interface():
    """Zkusí připojit k webovému rozhraní"""
    try:
        response = requests.get('http://localhost:8888', timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    print("🔍 DIAGNOSTIKA KEYLOGGERU")
    print("=" * 50)
    
    # 1. Kontrola portu
    print("1️⃣ Kontrola portu 8888...")
    port_status = check_port()
    print(f"   📍 Port 8888: {'🟢 OBSAZEN' if port_status else '🔴 VOLNÝ'}")
    
    # 2. Kontrola procesů
    print("2️⃣ Kontrola pythonw procesů...")
    processes = check_pythonw_processes()
    if processes:
        print(f"   🟢 Nalezeno {len(processes)} pythonw procesů:")
        for proc in processes:
            create_time = datetime.fromtimestamp(proc['create_time']).strftime("%H:%M:%S")
            print(f"      - PID {proc['pid']} (spuštěn {create_time})")
    else:
        print("   🔴 Žádné pythonw procesy neběží!")
    
    # 3. Kontrola webového rozhraní
    print("3️⃣ Kontrola webového rozhraní...")
    web_status = check_web_interface()
    print(f"   🌐 Webové rozhraní: {'🟢 DOSTUPNÉ' if web_status else '🔴 NEDOSTUPNÉ'}")
    
    # 4. Diagnostika
    print("\n🔎 DIAGNÓZA:")
    if not processes and not port_status:
        print("   ❌ Keylogger se pravděpodobně nespustil")
        print("   💡 Zkus: python spoustec.py znovu")
    
    elif processes and not port_status:
        print("   ⚠️  Keylogger běží, ale web server ne")
        print("   💡 Možná chyba v kódu keyloggeru")
    
    elif port_status and not web_status:
        print("   ⚠️  Port je obsazený, ale web neodpovídá")
        print("   💡 Možná jiná aplikace na portu 8888")
    
    elif processes and port_status and web_status:
        print("   ✅ Vše funguje správně!")
        print("   🌐 Otevři: http://localhost:8888")
    
    print("\n🛠️  ŘEŠENÍ PROBLÉMŮ:")
    print("   🔧 Restartuj keylogger: python spoustec.py")
    print("   🔧 Zkontroluj firewall")
    print("   🔧 Zkus jiný port v kódu")

if __name__ == "__main__":
    main()
