import subprocess
import os
import sys
import datetime
import socket

WORDLIST = "/usr/share/wordlists/dirb/common.txt"

def run_cmd(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        return str(e)

def banner_grab(ip, port):
    try:
        s = socket.socket()
        s.settimeout(2)
        s.connect((ip, port))
        data = s.recv(2048).decode(errors="ignore")
        s.close()
        return f"{port}/tcp → {data}"
    except:
        return f"{port}/tcp → (no banner)"

def aggressive_nmap(ip, outdir):
    cmd = f"nmap -A -Pn -T4 {ip}"
    output = run_cmd(cmd)
    with open(f"{outdir}/nmap.txt", "w", encoding="utf-8") as f:
        f.write(output)
    return output

def gobuster_scan(ip, outdir):
    cmd = f"gobuster dir -u http://{ip}/ -w {WORDLIST} -q"
    output = run_cmd(cmd)
    with open(f"{outdir}/gobuster.txt", "w", encoding="utf-8") as f:
        f.write(output)
    return output

def whois_scan(ip, outdir):
    cmd = f"whois {ip}"
    output = run_cmd(cmd)
    with open(f"{outdir}/whois.txt", "w", encoding="utf-8") as f:
        f.write(output)
    return output

def banners(ip, ports, outdir):
    banner_output = ""
    for p in ports:
        banner_output += banner_grab(ip, p) + "\n"
    with open(f"{outdir}/banners.txt", "w", encoding="utf-8") as f:
        f.write(banner_output)
    return banner_output

def make_html(outdir, nmap, gob, whois, banners):
    html = f"""
    <html>
    <head>
        <meta charset="utf-8"/>
        <title>AutoEnum Report</title>
        <style>
            body {{ font-family: monospace; background: #111; color: #0f0; padding: 20px; }}
            pre {{ background: #000; padding: 10px; border-radius: 8px; }}
            h1, h2 {{ color: #f4f4f4; }}
        </style>
    </head>
    <body>
        <h1>AutoEnum Report</h1>
        
        <h2>Nmap Aggressive Scan</h2>
        <pre>{nmap}</pre>

        <h2>Gobuster Results</h2>
        <pre>{gob}</pre>

        <h2>WHOIS Info</h2>
        <pre>{whois}</pre>

        <h2>Banner Grab</h2>
        <pre>{banners}</pre>

    </body>
    </html>
    """
    with open(f"{outdir}/report.html", "w", encoding="utf-8") as f:
        f.write(html)

def main():
    if len(sys.argv) < 2:
        print("Usage: python autoenum.py <target_ip>")
        sys.exit(1)

    ip = sys.argv[1]
    timestamp = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M")
    outdir = f"reports/scan_{timestamp}"
    os.makedirs(outdir, exist_ok=True)

    print(f"[+] Aggressive Nmap scanning…")
    nmap_res = aggressive_nmap(ip, outdir)

    print(f"[+] Gobuster scanning…")
    gob_res = gobuster_scan(ip, outdir)

    print(f"[+] WHOIS lookup…")
    whois_res = whois_scan(ip, outdir)

    print(f"[+] Banner grabbing…")
    banner_res = banners(ip, [21,22,80,443,445,8080], outdir)

    print(f"[+] Generating HTML report…")
    make_html(outdir, nmap_res, gob_res, whois_res, banner_res)

    print(f"[✔] Done! Report saved to: {outdir}/report.html")

if __name__ == "__main__":
    main()
