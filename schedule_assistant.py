import tkinter as tk
import pyautogui
import time
import random
import threading
import math

# ── Settings ──────────────────────────────────────────────
MOVE_SPEED = 0.3      # mouse move duration (seconds)
PAUSE_BETWEEN = 0.5   # pause between moves (seconds)
PATTERN_TYPE = 'circle'  # 'circle', 'figure8', 'random'
# ──────────────────────────────────────────────────────────

pyautogui.FAILSAFE = True  # Move mouse to top-left corner to abort


class ScheduleAssistant(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Schedule Assistant')
        self.geometry('800x600')
        self.configure(bg='#2d2d44')
        self.attributes('-topmost', True)
        self._build_ui()
        
        self.running = False
        self.stop_flag = threading.Event()
        self.last_mouse_pos = None  # Will be set on first move
        self.thread = None  # Track the running thread
        
        # Window bounds for mouse movement
        self.window_x = 100
        self.window_y = 100
        self.window_w = 800
        self.window_h = 600
        
    def _build_ui(self):
        # Title
        tk.Label(self, text='📅 Schedule Assistant', bg='#2d2d44', fg='#fbbf24',
                 font=('Segoe UI', 20, 'bold')).pack(pady=(20, 10))
        
        tk.Label(self, text='Auto-schedule task tracking', bg='#2d2d44', fg='#fde047',
                 font=('Segoe UI', 10)).pack(pady=(0, 20))
        
        # Canvas for character animation
        self.canvas = tk.Canvas(self, width=400, height=200, bg='#1a1a2e',
                               highlightthickness=0)
        self.canvas.pack(pady=10)
        
        # Character
        self.char_id = self.canvas.create_text(200, 100, text='📋', font=('Segoe UI', 40))
        
        # Cursor indicator
        self.cursor_id = self.canvas.create_oval(195, 95, 205, 105, fill='#fbbf24', outline='#fde047', width=2)
        
        # Path preview
        self.path_lines = []
        
        # Controls
        btn_frame = tk.Frame(self, bg='#2d2d44')
        btn_frame.pack(pady=15)
        
        tk.Button(btn_frame, text='▶ Start', command=self.start_training,
                 bg='#000000', fg='#fbbf24', font=('Segoe UI', 11, 'bold'),
                 padx=20, pady=8, bd=0, cursor='hand2').grid(row=0, column=0, padx=5)
        
        tk.Button(btn_frame, text='■ Stop', command=self.stop_training,
                 bg='#000000', fg='#fbbf24', font=('Segoe UI', 11, 'bold'),
                 padx=20, pady=8, bd=0, cursor='hand2').grid(row=0, column=1, padx=5)
        
        # Pattern selection
        pattern_frame = tk.Frame(self, bg='#2d2d44')
        pattern_frame.pack(pady=10)
        
        tk.Label(pattern_frame, text='Pattern:', bg='#2d2d44', fg='#fde047',
                 font=('Segoe UI', 9)).pack(side='left', padx=5)
        
        self.pattern_var = tk.StringVar(value='circle')
        patterns = ['circle', 'figure8', 'random']
        for p in patterns:
            tk.Radiobutton(pattern_frame, text=p.capitalize(), variable=self.pattern_var,
                          value=p, bg='#2d2d44', fg='#fbbf24', selectcolor='#1a1a2e',
                          activebackground='#2d2d44', activeforeground='#fbbf24',
                          font=('Segoe UI', 9)).pack(side='left', padx=5)
        
        # Window bounds controls
        bounds_frame = tk.Frame(self, bg='#2d2d44')
        bounds_frame.pack(pady=10)
        
        tk.Label(bounds_frame, text='Movement Area:', bg='#2d2d44', fg='#fde047',
                 font=('Segoe UI', 9)).grid(row=0, column=0, padx=5)
        
        tk.Label(bounds_frame, text='X:', bg='#2d2d44', fg='#fde047',
                 font=('Segoe UI', 9)).grid(row=0, column=1, padx=2)
        self.x_var = tk.IntVar(value=100)
        tk.Spinbox(bounds_frame, from_=0, to=3000, increment=10,
                   textvariable=self.x_var, width=5,
                   bg='#1a1a2e', fg='#fbbf24', bd=0).grid(row=0, column=2, padx=2)
        
        tk.Label(bounds_frame, text='Y:', bg='#2d2d44', fg='#fde047',
                 font=('Segoe UI', 9)).grid(row=0, column=3, padx=2)
        self.y_var = tk.IntVar(value=100)
        tk.Spinbox(bounds_frame, from_=0, to=2000, increment=10,
                   textvariable=self.y_var, width=5,
                   bg='#1a1a2e', fg='#fbbf24', bd=0).grid(row=0, column=4, padx=2)
        
        tk.Label(bounds_frame, text='W:', bg='#2d2d44', fg='#fde047',
                 font=('Segoe UI', 9)).grid(row=0, column=5, padx=2)
        self.w_var = tk.IntVar(value=800)
        tk.Spinbox(bounds_frame, from_=100, to=3000, increment=50,
                   textvariable=self.w_var, width=5,
                   bg='#1a1a2e', fg='#fbbf24', bd=0).grid(row=0, column=6, padx=2)
        
        tk.Label(bounds_frame, text='H:', bg='#2d2d44', fg='#fde047',
                 font=('Segoe UI', 9)).grid(row=0, column=7, padx=2)
        self.h_var = tk.IntVar(value=600)
        tk.Spinbox(bounds_frame, from_=100, to=2000, increment=50,
                   textvariable=self.h_var, width=5,
                   bg='#1a1a2e', fg='#fbbf24', bd=0).grid(row=0, column=8, padx=2)
        
        # Status
        self.status_var = tk.StringVar(value='Ready')
        tk.Label(self, textvariable=self.status_var, bg='#2d2d44', fg='#fde047',
                 font=('Segoe UI', 9)).pack(pady=(10, 0))
        
        # Instructions
        tk.Label(self, text='Move mouse to top-left corner to stop',
                 bg='#2d2d44', fg='#fde047', font=('Segoe UI', 8)).pack(pady=(5, 0))
    
    def start_training(self):
        if self.running:
            return
        self.running = True
        self.stop_flag.clear()
        self.last_mouse_pos = None  # Reset mouse position tracking
        self.status_var.set('Running...')
        
        # Get window bounds from UI
        self.window_x = self.x_var.get()
        self.window_y = self.y_var.get()
        self.window_w = self.w_var.get()
        self.window_h = self.h_var.get()
        
        self.thread = threading.Thread(target=self.run_pattern, daemon=True)
        self.thread.start()
    
    def stop_training(self):
        self.stop_flag.set()
        self.running = False  # Reset immediately
        self.status_var.set('Stopped')
        self.thread = None
    
    def run_pattern(self):
        # Use window bounds for movement area
        cx = self.window_x + self.window_w // 2
        cy = self.window_y + self.window_h // 2
        radius = min(self.window_w, self.window_h) // 4
        
        pattern = self.pattern_var.get()
        
        print(f"DEBUG: Starting pattern {pattern} at center ({cx}, {cy}) with radius {radius}")
        print(f"DEBUG: Window bounds: x={self.window_x}, y={self.window_y}, w={self.window_w}, h={self.window_h}")
        
        # Draw path preview on canvas
        self.draw_path_preview(pattern, 200, 100, 80)
        
        try:
            if pattern == 'circle':
                self.circle_pattern(cx, cy, radius)
            elif pattern == 'figure8':
                self.figure8_pattern(cx, cy, radius)
            else:
                self.random_pattern(cx, cy, radius)
        except Exception as e:
            print(f'Error: {e}')
        
        self.running = False
        self.status_var.set('Stopped')
        self.after(0, lambda: self.canvas.coords(self.char_id, 200, 100))
    
    def draw_path_preview(self, pattern, cx, cy, r):
        self.canvas.delete('path')
        if pattern == 'circle':
            self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r, outline='#3b3b6e', 
                                   width=2, tags='path')
        elif pattern == 'figure8':
            self.canvas.create_oval(cx-r, cy-r//2, cx+r, cy+r//2, outline='#3b3b6e',
                                   width=2, tags='path')
            self.canvas.create_oval(cx-r, cy-r//2-10, cx+r, cy+r//2+10, outline='#3b3b6e',
                                   width=2, tags='path')
    
    def circle_pattern(self, cx, cy, r):
        steps = 36
        for i in range(steps * 3):  # 3 full circles
            if self.stop_flag.is_set():
                break
            angle = (i % steps) * (2 * math.pi / steps)
            x = int(cx + r * math.cos(angle))
            y = int(cy + r * math.sin(angle))
            self.move_to(x, y)
            time.sleep(PAUSE_BETWEEN)
    
    def figure8_pattern(self, cx, cy, r):
        steps = 72
        for i in range(steps * 2):  # 2 full figure-8s
            if self.stop_flag.is_set():
                break
            t = (i % steps) * (2 * math.pi / steps)
            x = int(cx + r * math.sin(t))
            y = int(cy + r * math.sin(2 * t) / 2)
            self.move_to(x, y)
            time.sleep(PAUSE_BETWEEN)
    
    def random_pattern(self, cx, cy, r):
        prev_x, prev_y = cx, cy
        for _ in range(100):
            if self.stop_flag.is_set():
                break
            x = random.randint(max(self.window_x + 50, cx - r), min(self.window_x + self.window_w - 50, cx + r))
            y = random.randint(max(self.window_y + 50, cy - r), min(self.window_y + self.window_h - 50, cy + r))
            self.move_to(x, y)
            prev_x, prev_y = x, y
            time.sleep(PAUSE_BETWEEN)
    
    def move_to(self, x, y):
        # Only check for user movement after we've made at least one move
        if self.last_mouse_pos is not None:
            current_pos = pyautogui.position()
            if abs(current_pos[0] - self.last_mouse_pos[0]) > 50 or abs(current_pos[1] - self.last_mouse_pos[1]) > 50:
                self.stop_flag.set()
                self.status_var.set('Stopped — mouse moved')
                return
        
        # Update canvas character and cursor position
        screen_w, screen_h = pyautogui.size()
        canvas_x = (x / screen_w) * 400
        canvas_y = (y / screen_h) * 200
        self.after(0, lambda: self.canvas.coords(self.char_id, canvas_x, canvas_y))
        self.after(0, lambda: self.canvas.coords(self.cursor_id, canvas_x-5, canvas_y-5, canvas_x+5, canvas_y+5))
        
        # Move mouse
        pyautogui.moveTo(x, y, duration=MOVE_SPEED)
        
        # Update last position after successful move
        self.last_mouse_pos = (x, y)


if __name__ == '__main__':
    app = ScheduleAssistant()
    app.mainloop()
