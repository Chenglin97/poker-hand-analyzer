"""Debug what's being captured from QuickTime."""

import sys
sys.path.insert(0, 'src')

from poker_analyzer.screen_capture import ScreenCapture
import cv2

print("Debugging live screen capture...")
print("Make sure QuickTime is showing poker game!")
print()

sc = ScreenCapture()
print(f"Capture region: {sc.monitor}")
print()

# Capture
img = sc.capture()

if img is None:
    print("❌ Screen capture failed!")
    sys.exit(1)

print(f"✅ Captured: {img.shape[1]}x{img.shape[0]}")

# Save
cv2.imwrite('live_debug.png', img)
print("✅ Saved as: live_debug.png")
print()
print("Open this image and check:")
print("  1. Does it show the poker game?")
print("  2. Are cards visible and clear?")
print("  3. Is the entire game visible?")
print()
print("If NOT showing poker game:")
print("  → Update .env with correct screen coordinates")
print()

# Also extract one card as test
from poker_analyzer.card_detector import CardDetector

detector = CardDetector()

# Try to extract first board card
h, w = img.shape[:2]
card_config = detector.card_positions['board'][0]
pos = card_config['position']
x, y, width, height = pos

sx = int(x * w / detector.ref_width)
sy = int(y * h / detector.ref_height)
sw = int(width * w / detector.ref_width)
sh = int(height * h / detector.ref_height)

print(f"Trying to extract first board card at ({sx}, {sy}, {sw}, {sh})...")

if sy + sh <= h and sx + sw <= w and sy >= 0 and sx >= 0:
    card_img = img[sy:sy+sh, sx:sx+sw]
    cv2.imwrite('live_card_sample.png', card_img)
    print("✅ Saved sample card as: live_card_sample.png")
    
    # Extract rank region
    rank_reg = card_config['rank_region']
    rt, rl, rb, rr = rank_reg
    ch, cw = card_img.shape[:2]
    rank_img = card_img[int(ch*rt):int(ch*rb), int(cw*rl):int(cw*rr)]
    cv2.imwrite('live_rank_sample.png', rank_img)
    print("✅ Saved rank region as: live_rank_sample.png")
else:
    print("❌ Card coordinates out of bounds!")
    print(f"   Image size: {w}x{h}")
    print(f"   Trying to extract: ({sx}, {sy}) to ({sx+sw}, {sy+sh})")

