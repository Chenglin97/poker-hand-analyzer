"""Test screen capture functionality."""

import sys
sys.path.insert(0, 'src')

from poker_analyzer.screen_capture import ScreenCapture
import cv2

print("Testing Screen Capture...")
print("-" * 50)

try:
    # Initialize
    sc = ScreenCapture()
    print("Screen capture initialized")
    print(f"   Capture region: {sc.monitor}")
    
    # Capture
    print("\nCapturing screen...")
    img = sc.capture()
    
    if img is None:
        print("Screen capture returned None")
        sys.exit(1)
    
    print(f"✅ Screen captured successfully")
    print(f"   Image size: {img.shape[1]}x{img.shape[0]}")
    
    # Save test image
    cv2.imwrite('test_capture.png', img)
    print(f"Saved test_capture.png")
    print("\n👀 Open test_capture.png to verify it captured your screen")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 50)
print("Screen capture test: PASSED")
print("=" * 50)
