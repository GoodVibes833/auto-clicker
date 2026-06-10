; ============================================================
;  Auto Clicker — AHK v2
;  Opens demo.html in Chrome and clicks all 10 buttons in order
;  Compile: right-click .ahk → Compile Script → auto_clicker.exe
; ============================================================

#Requires AutoHotkey v2.0
#SingleInstance Force

; ---------- Settings ----------
HTML_FILE   := A_ScriptDir "\demo.html"   ; path to HTML file
DELAY_MS    := 1200                        ; delay between clicks (ms)
LOOP_COUNT  := 3                           ; total loop cycles (0 = infinite)
MOUSE_SPEED := 4                           ; mouse speed (1=fast ~ 20=slow)
; ------------------------------

; Open HTML file
Run("chrome.exe --new-window " HTML_FILE)
; If Chrome is not default, use: Run(HTML_FILE)

; Wait for browser to load
Sleep(2500)

; Activate Chrome window
WinActivate("ahk_exe chrome.exe")
WinWaitActive("ahk_exe chrome.exe", , 10)

; Get window position and size
WinGetPos(&winX, &winY, &winW, &winH, "ahk_exe chrome.exe")

; Chrome address bar + tab bar height offset
CHROME_TOP_OFFSET := 140

; ---- Button grid calculation ----
; Assumes max-width:600px centered on screen
; Grid: 2 columns x 5 rows, gap:16, padding:40

gridW    := Min(600, winW - 40)
gridX    := winX + (winW - gridW) // 2   ; grid start X

; Button center X per column (2 columns)
colCenters := [
    gridX + gridW * 0.25,
    gridX + gridW * 0.75
]

; Button center Y per row (5 rows) — includes browser top offset
; log box (~100px) + header height
logBoxH  := 100
headerH  := 110   ; h1 + status + margin
gridTopY := winY + CHROME_TOP_OFFSET + headerH + logBoxH + 36

btnH     := 70   ; button height (padding:22*2 + text)
gapH     := 16

rowCenters := []
Loop 5 {
    rowCenters.Push(gridTopY + (A_Index - 1) * (btnH + gapH) + btnH // 2)
}

; Button coordinates array [x, y]
buttons := [
    [colCenters[1], rowCenters[1]],  ; btn1 Start
    [colCenters[2], rowCenters[1]],  ; btn2 Stop
    [colCenters[1], rowCenters[2]],  ; btn3 Refresh
    [colCenters[2], rowCenters[2]],  ; btn4 Save
    [colCenters[1], rowCenters[3]],  ; btn5 Upload
    [colCenters[2], rowCenters[3]],  ; btn6 Download
    [colCenters[1], rowCenters[4]],  ; btn7 Settings
    [colCenters[2], rowCenters[4]],  ; btn8 Analyze
    [colCenters[1], rowCenters[5]],  ; btn9 Reset
    [colCenters[2], rowCenters[5]]   ; btn10 Done
]

btnNames := ["Start","Stop","Refresh","Save","Upload","Download","Settings","Analyze","Reset","Done"]

; ---- Main loop ----
currentLoop := 0
loop {
    currentLoop++
    if (LOOP_COUNT > 0 && currentLoop > LOOP_COUNT)
        break

    for i, coord in buttons {
        ; Check if window is still open
        if !WinExist("ahk_exe chrome.exe") {
            MsgBox("Chrome window was closed. Exiting.")
            ExitApp()
        }

        WinActivate("ahk_exe chrome.exe")

        ; Physical mouse move
        MouseMove(coord[1], coord[2], MOUSE_SPEED)
        Sleep(200)

        ; Click
        Click(coord[1], coord[2])
        Sleep(DELAY_MS)
    }

    ; Short pause between cycles
    Sleep(800)
}

MsgBox("Auto click complete!`nClicked " (currentLoop - 1) * 10 " times total.")
ExitApp()

; ---- Hotkey: ESC to quit immediately ----
Escape:: ExitApp()
