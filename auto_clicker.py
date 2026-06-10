import threading
import time
import webbrowser
import http.server
import socketserver
import os
import sys
import tkinter as tk
from tkinter import ttk
import pyautogui

# ── Settings ──────────────────────────────────────────────
PORT        = 8742
DELAY_MS    = 1.2   # seconds between clicks
MOUSE_SPEED = 0.4   # mouse move duration (seconds)
LOOP_COUNT  = 3     # 0 = infinite
# ──────────────────────────────────────────────────────────

BASE_DIR = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
HTML_PATH = os.path.join(BASE_DIR, 'demo.html')

pyautogui.FAILSAFE = True   # move mouse to top-left corner to abort


# ── Local HTTP server ──────────────────────────────────────
class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def log_message(self, format, *args):
        pass


def start_server():
    with socketserver.TCPServer(('', PORT), QuietHandler) as httpd:
        httpd.serve_forever()


# ── Auto clicker logic ─────────────────────────────────────
BUTTONS = [
    'Start', 'Stop', 'Refresh', 'Save', 'Upload',
    'Download', 'Settings', 'Analyze', 'Reset', 'Done'
]

running = False
stop_flag = threading.Event()


def find_button_center(label_text):
    """Use pyautogui image-free search: locate button text on screen."""
    try:
        loc = pyautogui.locateOnScreen(
            os.path.join(BASE_DIR, f'btn_{label_text.lower()}.png'),
            confidence=0.8
        )
        if loc:
            return pyautogui.center(loc)
    except Exception:
        pass
    return None


def click_sequence(log_callback, status_callback):
    global running
    stop_flag.clear()
    loop_num = 0
    total = 0

    time.sleep(2.5)  # wait for browser to open

    screen_w, screen_h = pyautogui.size()

    # Estimated button grid positions based on 1920x1080 reference
    # Buttons are in a 2-col x 5-row grid, centered, max-width 600px
    grid_w = min(600, screen_w - 40)
    grid_x = (screen_w - grid_w) // 2
    col = [int(grid_x + grid_w * 0.25), int(grid_x + grid_w * 0.75)]

    # Browser chrome offset + header + log box
    top_offset = 185
    btn_h = 70
    gap_h = 16
    rows = [int(top_offset + i * (btn_h + gap_h) + btn_h // 2) for i in range(5)]

    coords = [
        (col[0], rows[0]), (col[1], rows[0]),
        (col[0], rows[1]), (col[1], rows[1]),
        (col[0], rows[2]), (col[1], rows[2]),
        (col[0], rows[3]), (col[1], rows[3]),
        (col[0], rows[4]), (col[1], rows[4]),
    ]

    while not stop_flag.is_set():
        loop_num += 1
        if LOOP_COUNT > 0 and loop_num > LOOP_COUNT:
            break

        for i, (x, y) in enumerate(coords):
            if stop_flag.is_set():
                break
            name = BUTTONS[i]
            status_callback(f'Clicking: {name}')
            pyautogui.moveTo(x, y, duration=MOUSE_SPEED)
            time.sleep(0.15)
            pyautogui.click()
            total += 1
            log_callback(f'[Loop {loop_num}]  {name}  — total clicks: {total}')
            time.sleep(DELAY_MS)

        time.sleep(0.8)

    running = False
    status_callback(f'Done — {total} clicks total')
    log_callback('--- Finished ---')


# ── Tkinter GUI ────────────────────────────────────────────
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Auto Clicker')
        self.geometry('460x380')
        self.resizable(False, False)
        self.configure(bg='#0f0f1a')
        self._build_ui()

        # Start local server in background
        t = threading.Thread(target=start_server, daemon=True)
        t.start()

    def _build_ui(self):
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('TLabel', background='#0f0f1a', foreground='#c4b5fd',
                        font=('Segoe UI', 10))
        style.configure('Start.TButton', background='#7c3aed', foreground='white',
                        font=('Segoe UI', 11, 'bold'), padding=8)
        style.configure('Stop.TButton', background='#6b7280', foreground='white',
                        font=('Segoe UI', 11, 'bold'), padding=8)

        tk.Label(self, text='AUTO CLICKER', bg='#0f0f1a', fg='#a78bfa',
                 font=('Segoe UI', 18, 'bold')).pack(pady=(20, 4))

        self.status_var = tk.StringVar(value='Ready')
        tk.Label(self, textvariable=self.status_var, bg='#0f0f1a', fg='#6b7280',
                 font=('Segoe UI', 9)).pack()

        # Log box
        frame = tk.Frame(self, bg='#1a1a2e', bd=1, relief='solid')
        frame.pack(fill='x', padx=20, pady=12)
        self.log_box = tk.Text(frame, height=8, bg='#1a1a2e', fg='#94a3b8',
                               font=('Consolas', 9), bd=0, wrap='word',
                               state='disabled', insertbackground='white')
        self.log_box.pack(fill='x', padx=8, pady=6)

        # Buttons row
        btn_frame = tk.Frame(self, bg='#0f0f1a')
        btn_frame.pack(pady=6)

        self.start_btn = ttk.Button(btn_frame, text='▶  Open & Start',
                                    style='Start.TButton', command=self.on_start)
        self.start_btn.grid(row=0, column=0, padx=8)

        self.stop_btn = ttk.Button(btn_frame, text='■  Stop',
                                   style='Stop.TButton', command=self.on_stop,
                                   state='disabled')
        self.stop_btn.grid(row=0, column=1, padx=8)

        # Settings row
        cfg = tk.Frame(self, bg='#0f0f1a')
        cfg.pack(pady=(4, 0))
        tk.Label(cfg, text='Delay (s):', bg='#0f0f1a', fg='#6b7280',
                 font=('Segoe UI', 9)).grid(row=0, column=0, padx=4)
        self.delay_var = tk.DoubleVar(value=DELAY_MS)
        tk.Spinbox(cfg, from_=0.3, to=10.0, increment=0.1,
                   textvariable=self.delay_var, width=5,
                   bg='#1a1a2e', fg='#c4b5fd', bd=0).grid(row=0, column=1, padx=4)

        tk.Label(cfg, text='Loops:', bg='#0f0f1a', fg='#6b7280',
                 font=('Segoe UI', 9)).grid(row=0, column=2, padx=4)
        self.loop_var = tk.IntVar(value=LOOP_COUNT)
        tk.Spinbox(cfg, from_=0, to=999, increment=1,
                   textvariable=self.loop_var, width=5,
                   bg='#1a1a2e', fg='#c4b5fd', bd=0).grid(row=0, column=3, padx=4)

        tk.Label(cfg, text='(0=∞)', bg='#0f0f1a', fg='#4b5563',
                 font=('Segoe UI', 8)).grid(row=0, column=4, padx=2)

    def log(self, msg):
        self.log_box.config(state='normal')
        self.log_box.insert('end', msg + '\n')
        self.log_box.see('end')
        self.log_box.config(state='disabled')

    def set_status(self, msg):
        self.status_var.set(msg)

    def on_start(self):
        global running, DELAY_MS, LOOP_COUNT
        if running:
            return
        running = True
        DELAY_MS   = self.delay_var.get()
        LOOP_COUNT = self.loop_var.get()

        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.log('Opening browser...')
        self.set_status('Running...')

        webbrowser.open(f'http://localhost:{PORT}/demo.html')

        t = threading.Thread(
            target=click_sequence,
            args=(
                lambda m: self.after(0, self.log, m),
                lambda m: self.after(0, self.set_status, m),
            ),
            daemon=True
        )
        t.start()
        self.after(100, self._check_done)

    def on_stop(self):
        stop_flag.set()
        self.set_status('Stopping...')

    def _check_done(self):
        if running:
            self.after(500, self._check_done)
        else:
            self.start_btn.config(state='normal')
            self.stop_btn.config(state='disabled')


if __name__ == '__main__':
    app = App()
    app.mainloop()
