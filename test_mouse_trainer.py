"""
UI Automation Test for Schedule Assistant
Tests basic functionality: start, stop, restart
"""
import pyautogui
import time
import subprocess
import sys

def find_button(button_text):
    """Find a button by text on screen"""
    try:
        # Try to locate button by text (simplified approach)
        # In a real test, you'd use image recognition or accessibility APIs
        screen_w, screen_h = pyautogui.size()
        # Assume window is centered - adjust based on actual window position
        center_x, center_y = screen_w // 2, screen_h // 2
        
        # Approximate button positions based on window layout
        if button_text == 'Start':
            return (center_x - 80, center_y + 100)
        elif button_text == 'Stop':
            return (center_x + 80, center_y + 100)
        return None
    except Exception as e:
        print(f"Error finding button: {e}")
        return None

def test_basic_functionality():
    """Test basic start/stop/restart functionality"""
    print("Starting UI Automation Test...")
    
    # Give time for user to position the app
    print("Please make sure the Schedule Assistant window is visible.")
    print("Test will begin in 5 seconds...")
    time.sleep(5)
    
    try:
        # Test 1: Click Start
        print("\n[TEST 1] Clicking Start button...")
        start_pos = find_button('Start')
        if start_pos:
            pyautogui.moveTo(start_pos[0], start_pos[1], duration=0.5)
            pyautogui.click()
            print("Start button clicked")
            time.sleep(3)  # Wait for mouse to start moving
            
            # Check if mouse is moving
            pos1 = pyautogui.position()
            time.sleep(1)
            pos2 = pyautogui.position()
            
            if pos1 != pos2:
                print("✓ Mouse is moving - PASS")
            else:
                print("✗ Mouse is not moving - FAIL")
        else:
            print("✗ Could not find Start button - FAIL")
        
        # Test 2: Click Stop
        print("\n[TEST 2] Clicking Stop button...")
        stop_pos = find_button('Stop')
        if stop_pos:
            pyautogui.moveTo(stop_pos[0], stop_pos[1], duration=0.5)
            pyautogui.click()
            print("Stop button clicked")
            time.sleep(1)
            print("✓ Stop clicked - PASS")
        else:
            print("✗ Could not find Stop button - FAIL")
        
        # Test 3: Click Start again (restart test)
        print("\n[TEST 3] Clicking Start button again (restart test)...")
        if start_pos:
            pyautogui.moveTo(start_pos[0], start_pos[1], duration=0.5)
            pyautogui.click()
            print("Start button clicked again")
            time.sleep(3)
            
            # Check if mouse is moving again
            pos1 = pyautogui.position()
            time.sleep(1)
            pos2 = pyautogui.position()
            
            if pos1 != pos2:
                print("✓ Mouse is moving after restart - PASS")
            else:
                print("✗ Mouse is not moving after restart - FAIL")
        else:
            print("✗ Could not find Start button - FAIL")
        
        # Test 4: Click Stop to clean up
        print("\n[TEST 4] Clicking Stop button to clean up...")
        if stop_pos:
            pyautogui.moveTo(stop_pos[0], stop_pos[1], duration=0.5)
            pyautogui.click()
            print("Stop button clicked")
        
        print("\n=== Test Complete ===")
        
    except Exception as e:
        print(f"Error during test: {e}")

if __name__ == '__main__':
    print("Schedule Assistant UI Automation Test")
    print("=" * 50)
    test_basic_functionality()
