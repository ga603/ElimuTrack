import os
import sys
import threading
import time
import subprocess
import webbrowser

# PREVENT "HIDDEN CONSOLE" CRASH:
# If PyInstaller hides the console, redirect Django's print statements into the void so it doesn't panic.
if sys.stdout is None:
    sys.stdout = open(os.devnull, 'w')
if sys.stderr is None:
    sys.stderr = open(os.devnull, 'w')
# Tell the EXE where to find your Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
from django.core.management import execute_from_command_line

def start_django():
    django.setup()
    # This runs the server internally without opening a black terminal window!
    execute_from_command_line(['manage.py', 'runserver', '127.0.0.1:8000', '--noreload'])

if __name__ == '__main__':
    # Required for Windows EXE compiling
    import multiprocessing
    multiprocessing.freeze_support()

    # Start Django in a background thread
    t = threading.Thread(target=start_django)
    t.daemon = True
    t.start()

    time.sleep(2)

    url = "http://127.0.0.1:8000"
    
    # Open as Standalone Window
    try:
        subprocess.Popen(['start', 'msedge', f'--app={url}'], shell=True)
    except Exception:
        try:
            subprocess.Popen(['start', 'chrome', f'--app={url}'], shell=True)
        except Exception:
            webbrowser.open(url)
            
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass