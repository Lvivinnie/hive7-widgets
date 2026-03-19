"""
Red Queen Desktop Widget - pywebview launcher
Loads the HIVE-7 Red Queen AI themed widget as a desktop overlay.
"""
import webview
import ctypes
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_FILE = os.path.join(BASE_DIR, "redqueen_widget.html")


def set_window_transparent(window):
    """Enable transparent window background."""
    hwnd = window.handle
    GWL_EXSTYLE = -20
    WS_EX_TRANSPARENT = 0x00000020
    WS_EX_LAYERED = 0x00080000
    LWA_ALPHA = 0x00000002

    exstyle = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
    ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, exstyle | WS_EX_LAYERED)
    ctypes.windll.user32.SetLayeredWindowAttributes(hwnd, 0, 240, LWA_ALPHA)


def set_always_on_top(window):
    """Keep window above other windows."""
    HWND_TOPMOST = -1
    SWP_NOMOVE = 0x0002
    SWP_NOSIZE = 0x0001
    ctypes.windll.user32.SetWindowPos(window.handle, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE)


if __name__ == '__main__':
    screen_w = ctypes.windll.user32.GetSystemMetrics(0)  # SM_CXSCREEN
    screen_h = ctypes.windll.user32.GetSystemMetrics(1)   # SM_CYSCREEN

    # Default size
    win_w = 360
    win_h = 520
    # Position: top-right corner
    x = screen_w - win_w - 20
    y = 40

    window = webview.create_window(
        'HIVE-7 // Red Queen',
        HTML_FILE,
        width=win_w,
        height=win_h,
        x=x,
        y=y,
        resizable=True,
        frameless=True,
    )

    webview.start(set_window_transparent, window, debug=False)
