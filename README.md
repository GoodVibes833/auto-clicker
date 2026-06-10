# Auto Clicker — Windows EXE

Zero install. Double-click `AutoClicker.exe` and it works.

## Files
- `demo.html` — 10-button UI (served locally by the exe)
- `auto_clicker.py` — Python source (pyautogui + tkinter)
- `.github/workflows/build.yml` — GitHub Actions: builds Windows .exe automatically

---

## How to get the .exe (no install needed on Windows)

### Step 1 — Push this repo to GitHub
```bash
git init
git add .
git commit -m "init"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### Step 2 — GitHub builds the .exe automatically
Go to your repo on GitHub → **Actions** tab → click the latest run → **AutoClicker-Windows** artifact → Download

### Step 3 — Run on Windows
Extract the zip → double-click `AutoClicker.exe` → no Python, no install needed.

---

## What it does
1. Opens `demo.html` in your default browser (local server on port 8742)
2. Mouse physically moves to each button and clicks it
3. Cycles through all 10 buttons in order, repeating N times

**Move mouse to top-left corner of screen to emergency stop.**

---

## Settings (adjustable in the GUI)
| Setting | Default | Description |
|---------|---------|-------------|
| Delay | 1.2s | Wait between clicks |
| Loops | 3 | Full cycles (0 = infinite) |
