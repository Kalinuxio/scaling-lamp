import os
import subprocess
from datetime import datetime

# 1) vytvoření složky s dnešním datem
nazev_slozky = "wifi_scan_" + datetime.now().strftime("%Y-%m-%d_%H-%M")
os.makedirs(nazev_slozky, exist_ok=True)

print(f"[+] Vytvořena složka: {nazev_slozky}")

# 2) spuštění nmcli pro scan Wi-Fi
print("[+] Skenuji Wi-Fi sítě...")
try:
    output = subprocess.check_output(["nmcli", "-t", "-f", "SSID,SECURITY", "dev", "wifi"])
    output = output.decode("utf-8")
except:
    print("[-] Chyba: nmcli není dostupné.")
    exit()

# 3) vytvoření souboru pro výsledky
soubor = os.path.join(nazev_slozky, "wifi_list.txt")

with open(soubor, "w") as f:
    f.write("=== SCAN VYSLEDKY ===\n")
    for line in output.strip().split("\n"):
        if line.strip() == "":
            continue

        ssid, security = line.split(":")

        # pokud nic není -> skrytá síť
        if ssid == "":
            ssid = "[SKRYTA]"

        # wifi bez hesla
        if security == "":
            security = "OPEN"

        f.write(f"WiFi: {ssid} | Zabezpečení: {security}\n")

print(f"[+] Výsledky uložené v souboru: {soubor}")

# 4) fake hacking efekty
print("\n[+] Exportuji data...")
print("[++++++++++++++] 100%")
print("[+] Hotovo.")
