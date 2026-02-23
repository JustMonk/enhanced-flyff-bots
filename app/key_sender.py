from pynput.keyboard import Controller, Key
import pygetwindow as gw  # For window management
import time

def get_window_by_hwnd(hwnd):
    """Get window object by HWND"""
    try:
        # Get all windows
        all_windows = gw.getAllWindows()
        
        # Find window with matching HWND
        for window in all_windows:
            if window._hWnd == hwnd:
                return window
        
        return None
    except Exception as e:
        # print(f"Error getting window: {e}")
        return None

def send_to_window(hwnd, key: Key | str):
    # print('send_to_window called with: ', hwnd, key)

    if isinstance(hwnd, str):
        if hwnd.startswith('0x'):
            hwnd = int(hwnd, 16)
        else:
            hwnd = int(hwnd)

    window = get_window_by_hwnd(hwnd)

    if window:
        # Activate the window (throws an error)
        # windows.activate()
        # workaround:
        if not window.isActive:
            window.minimize()
            window.restore()
        keyboard = Controller()

        keyboard.press(key)
        time.sleep(0.02)
        keyboard.release(key)
        return True
    
    return False
