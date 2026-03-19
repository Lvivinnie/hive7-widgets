"""
Red Queen Desktop Widgets - Main Server
Opens multiple transparent windows with HIVE-7 Red Queen AI theme.
"""
import webview
import ctypes
import threading
import time
import os
import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
import psutil
import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PORT = 18765

# GPU data (cached by background thread)
gpu_state = {'load': 0, 'clock': None, 'temp': None}


def refresh_gpu():
    """Background thread: poll nvidia-smi every 3 seconds."""
    global gpu_state
    while True:
        try:
            import subprocess
            out = subprocess.check_output(
                ['nvidia-smi', '--query-gpu=utilization.gpu,clocks.current.graphics,temperature.gpu',
                 '--format=csv,noheader,nounits'],
                stderr=subprocess.DEVNULL, timeout=3
            ).decode()
            parts = out.strip().split(',')
            gpu_state = {
                'load': float(parts[0].strip()),
                'clock': int(float(parts[1].strip())),
                'temp': int(float(parts[2].strip())),
            }
        except Exception:
            gpu_state = {'load': 0, 'clock': None, 'temp': None}
        time.sleep(3)


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def do_GET(self):
        if self.path == '/data':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            cpu = psutil.cpu_percent(interval=None)
            mem = psutil.virtual_memory()
            net = psutil.net_io_counters()

            procs = []
            for p in psutil.process_iter(['name', 'cpu_percent']):
                try:
                    n = p.info['name']
                    c = p.info['cpu_percent'] or 0
                    if c > 0:
                        procs.append({'name': (n or '?')[:30], 'cpu': c})
                except Exception:
                    pass
            procs.sort(key=lambda x: x['cpu'], reverse=True)

            data = {
                'cpu': cpu,
                'mem': {'total': mem.total, 'used': mem.used, 'pct': mem.percent},
                'gpu': gpu_state,
                'net': {'sent': net.bytes_sent, 'recv': net.bytes_recv},
                'procs': procs[:15],
                'time_str': datetime.datetime.now().strftime('%H:%M:%S'),
            }
            self.wfile.write(json.dumps(data).encode())
        else:
            super().do_GET()

    def log_message(self, *args):
        pass


def start_server():
    HTTPServer(('127.0.0.1', PORT), Handler).serve_forever()


def set_transparent_callback(windows):
    """pywebview calls this with a list of window objects."""
    for win in (windows if isinstance(windows, list) else [windows]):
        try:
            hwnd = win.handle
            GWL = -20
            exstyle = ctypes.windll.user32.GetWindowLongW(hwnd, GWL)
            ctypes.windll.user32.SetWindowLongW(hwnd, GWL, exstyle | 0x00080000)
            ctypes.windll.user32.SetLayeredWindowAttributes(hwnd, 0, 238, 0x00000002)
        except Exception:
            pass


if __name__ == '__main__':
    # GPU polling
    gt = threading.Thread(target=refresh_gpu, daemon=True)
    gt.start()

    # HTTP server
    st = threading.Thread(target=start_server, daemon=True)
    st.start()
    time.sleep(1.2)

    sw = ctypes.windll.user32.GetSystemMetrics(0)
    sh = ctypes.windll.user32.GetSystemMetrics(1)
    BASE_URL = f'http://127.0.0.1:{PORT}'

    gap = 10
    # Layout: System Monitor (top-left of right cluster) | Calendar (top-right of right cluster) | Price (bottom-right)
    cal_w, cal_h = 360, 540
    mon_w, mon_h = 400, 540
    pri_w, pri_h = 360, 580

    win1 = webview.create_window(
        'HIVE-7 // Calendar',
        f'{BASE_URL}/redqueen_widget.html',
        width=cal_w, height=cal_h,
        x=sw - cal_w - 20, y=40,
        resizable=True, frameless=True,
    )
    win2 = webview.create_window(
        'HIVE-7 // System Monitor',
        f'{BASE_URL}/redqueen_sysmon.html',
        width=mon_w, height=mon_h,
        x=sw - cal_w - gap - mon_w - 20, y=40,
        resizable=True, frameless=True,
    )
    win3 = webview.create_window(
        'HIVE-7 // Price Monitor',
        f'{BASE_URL}/redqueen_price.html',
        width=pri_w, height=pri_h,
        x=sw - pri_w - 20, y=sh - pri_h - 40,
        resizable=True, frameless=True,
    )

    webview.start(set_transparent_callback, [win1, win2, win3], debug=False)
