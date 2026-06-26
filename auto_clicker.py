import threading
import time
import webbrowser
import http.server
import socketserver
import os
import sys
import random
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

pyautogui.FAILSAFE = True   # Move mouse to top-left corner to abort
pyautogui.PAUSE = 0.05


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


def find_button_center(button_name):
    """Find button by text on screen using OCR-free method."""
    try:
        # Try to locate the button by searching for its text
        # We'll use a region-based search to improve accuracy
        screen_w, screen_h = pyautogui.size()
        search_region = (0, 100, screen_w, screen_h - 200)  # Exclude top/bottom areas
        
        # Search for the button text
        loc = pyautogui.locateOnScreen(
            f'btn_{button_name.lower()}',
            confidence=0.7,
            region=search_region
        )
        if loc:
            return pyautogui.center(loc)
    except Exception:
        pass
    
    # Fallback: try to find by searching for button-like elements
    try:
        # Look for buttons in the expected grid area
        grid_w = min(600, screen_w - 40)
        grid_x = (screen_w - grid_w) // 2
        grid_y = 185  # Browser chrome offset + header
        
        # Define search regions for each button position
        button_positions = [
            (grid_x + int(grid_w * 0.25), grid_y + 35),  # Start
            (grid_x + int(grid_w * 0.75), grid_y + 35),  # Stop
            (grid_x + int(grid_w * 0.25), grid_y + 121), # Refresh
            (grid_x + int(grid_w * 0.75), grid_y + 121), # Save
            (grid_x + int(grid_w * 0.25), grid_y + 207), # Upload
            (grid_x + int(grid_w * 0.75), grid_y + 207), # Download
            (grid_x + int(grid_w * 0.25), grid_y + 293), # Settings
            (grid_x + int(grid_w * 0.75), grid_y + 293), # Analyze
            (grid_x + int(grid_w * 0.25), grid_y + 379), # Reset
            (grid_x + int(grid_w * 0.75), grid_y + 379), # Done
        ]
        
        button_index = BUTTONS.index(button_name)
        if button_index < len(button_positions):
            return button_positions[button_index]
    except Exception:
        pass
    
    return None


def click_sequence(log_callback, status_callback, random_mode=False):
    global running
    stop_flag.clear()
    loop_num = 0
    total = 0

    time.sleep(2.5)  # wait for browser to open

    screen_w, screen_h = pyautogui.size()
    log_callback(f'Screen: {screen_w}x{screen_h}')

    # Get browser window position (works on Mac and Windows)
    try:
        import pygetwindow
        browser = pygetwindow.getActiveWindow()
        if browser and hasattr(browser, 'left'):
            win_x, win_y = browser.left, browser.top
            win_w, win_h = browser.width, browser.height
            log_callback(f'Browser window: ({win_x}, {win_y}) {win_w}x{win_h}')
        else:
            win_x, win_y = 0, 100  # fallback
            win_w, win_h = screen_w, screen_h - 100
            log_callback('Could not detect browser window, using screen coordinates')
    except Exception as e:
        win_x, win_y = 0, 100  # fallback
        win_w, win_h = screen_w, screen_h - 100
        log_callback(f'Window detection failed: {e}, using screen coordinates')

    # Calculate button positions based on actual browser window
    grid_w = min(600, win_w - 40)
    grid_x = win_x + (win_w - grid_w) // 2
    grid_y = win_y + 150  # Browser chrome offset + header (adjusted for Mac)

    button_positions = [
        (grid_x + int(grid_w * 0.25), grid_y + 35),  # Start
        (grid_x + int(grid_w * 0.75), grid_y + 35),  # Stop
        (grid_x + int(grid_w * 0.25), grid_y + 121), # Refresh
        (grid_x + int(grid_w * 0.75), grid_y + 121), # Save
        (grid_x + int(grid_w * 0.25), grid_y + 207), # Upload
        (grid_x + int(grid_w * 0.75), grid_y + 207), # Download
        (grid_x + int(grid_w * 0.25), grid_y + 293), # Settings
        (grid_x + int(grid_w * 0.75), grid_y + 293), # Analyze
        (grid_x + int(grid_w * 0.25), grid_y + 379), # Reset
        (grid_x + int(grid_w * 0.75), grid_y + 379), # Done
    ]

    log_callback(f'Grid: x={grid_x}, y={grid_y}, w={grid_w}')
    for i, (bx, by) in enumerate(button_positions):
        log_callback(f'  {BUTTONS[i]}: ({bx}, {by})')

    # Calibration: ask user to click Start button to get actual position
    log_callback('Please click the Start button to calibrate...')
    status_callback('Click Start to calibrate')
    
    # Wait for user to click Start button
    calibration_done = False
    while not calibration_done and not stop_flag.is_set():
        time.sleep(0.1)
        # Check if mouse was clicked (simple check - wait 5 seconds)
        for _ in range(50):  # 5 seconds
            if stop_flag.is_set():
                break
            time.sleep(0.1)
        
        if stop_flag.is_set():
            break
        
        # Get current mouse position as calibration point
        cal_x, cal_y = pyautogui.position()
        log_callback(f'Calibrated at: ({cal_x}, {cal_y})')
        
        # Calculate offset from expected position
        expected_x, expected_y = button_positions[0]
        offset_x = cal_x - expected_x
        offset_y = cal_y - expected_y
        
        log_callback(f'Offset: x={offset_x}, y={offset_y}')
        
        # Apply offset to all button positions
        button_positions = [(x + offset_x, y + offset_y) for x, y in button_positions]
        
        calibration_done = True

    if stop_flag.is_set():
        running = False
        return

    # Check if Start button is clicked first
    first_click_done = False

    try:
        while not stop_flag.is_set():
            loop_num += 1
            if LOOP_COUNT > 0 and loop_num > LOOP_COUNT:
                break

            # Create button list for this loop
            if random_mode:
                button_indices = list(range(len(BUTTONS)))
                # Ensure Start is first if not clicked yet
                if not first_click_done and 0 in button_indices:
                    button_indices.remove(0)
                    button_indices.insert(0, 0)
                random.shuffle(button_indices)
            else:
                button_indices = list(range(len(BUTTONS)))

            for idx in button_indices:
                if stop_flag.is_set():
                    break
                
                button_name = BUTTONS[idx]
                
                # Check if first click is Start button
                if not first_click_done and button_name != 'Start':
                    log_callback('ERROR: You must click Start button first')
                    status_callback('Click Start first')
                    running = False
                    break
                
                # Store mouse position before move
                mouse_before = pyautogui.position()
                
                status_callback(f'Clicking: {button_name}')
                
                # Get button position
                if idx < len(button_positions):
                    x, y = button_positions[idx]
                else:
                    log_callback(f'ERROR: Button index {idx} out of range')
                    break
                
                try:
                    pyautogui.moveTo(x, y, duration=MOUSE_SPEED)
                    time.sleep(0.15)
                    
                    # Check if mouse is at expected position (user didn't move it)
                    mouse_after = pyautogui.position()
                    if abs(mouse_after[0] - x) > 30 or abs(mouse_after[1] - y) > 30:
                        log_callback('CANCELLED: Mouse moved by user')
                        status_callback('Stopped — mouse moved')
                        running = False
                        break
                    
                    pyautogui.click()
                    total += 1
                    first_click_done = True
                    log_callback(f'[Loop {loop_num}]  {button_name}  — total: {total}')
                except Exception as e:
                    log_callback(f'ERROR clicking {button_name}: {e}')
                
                if not running:
                    break
                
                time.sleep(DELAY_MS)

            if not running:
                break
            time.sleep(0.8)
    except Exception as e:
        log_callback(f'FATAL: {e}')

    running = False
    status_callback(f'Done — {total} clicks total')
    log_callback('--- Finished ---')


# ── Tkinter GUI ────────────────────────────────────────────
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Task Assistant')
        self.geometry('460x380')
        self.resizable(False, False)
        self.configure(bg='#0f0f1a')
        self.attributes('-topmost', True)  # Keep window always on top
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

        # Random mode row
        random_cfg = tk.Frame(self, bg='#0f0f1a')
        random_cfg.pack(pady=(8, 0))
        self.random_var = tk.BooleanVar(value=False)
        tk.Checkbutton(random_cfg, text='Random order', variable=self.random_var,
                      bg='#0f0f1a', fg='#c4b5fd', selectcolor='#1a1a2e',
                      activebackground='#0f0f1a', activeforeground='#a78bfa',
                      font=('Segoe UI', 9)).pack()

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
        random_mode = self.random_var.get()

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
                random_mode,
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
