"""Helper script to find QuickTime window coordinates."""

import mss
import cv2
import numpy as np

print("Capturing full screen...")
print("This will help you find the coordinates of your QuickTime window.")
print()

with mss.mss() as sct:
    # Capture full screen
    monitor = sct.monitors[1]
    screenshot = sct.grab(monitor)
    
    img = np.array(screenshot)
    img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    
    # Save image
    cv2.imwrite('fullscreen.png', img)
    
    print(f"✅ Saved fullscreen.png ({img.shape[1]}x{img.shape[0]})")
    print()
    print("Next steps:")
    print("1. Open fullscreen.png")
    print("2. Find your QuickTime window showing the poker game")
    print("3. Note the X, Y coordinates of the top-left corner")
    print("4. Note the width and height")
    print("5. Update these values in your .env file:")
    print()
    print("   SCREEN_TOP=<Y coordinate>")
    print("   SCREEN_LEFT=<X coordinate>")
    print("   SCREEN_WIDTH=<width>")
    print("   SCREEN_HEIGHT=<height>")