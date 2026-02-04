"""Debug card detection by saving extracted regions."""

import sys
sys.path.insert(0, 'src')

import cv2
import os
from poker_analyzer.card_detector import CardDetector
from poker_analyzer.config import config

print("=" * 70)
print("DEBUG: Card Region Extraction")
print("=" * 70)

# Load image
img_path = './test_capture.png'
img = cv2.imread(img_path)

if img is None:
    print(f"❌ Could not load {img_path}")
    sys.exit(1)

print(f"✅ Image loaded: {img.shape[1]}x{img.shape[0]}")
print()

# Create debug directory
os.makedirs('debug_cards', exist_ok=True)

# Initialize detector
detector = CardDetector()
h, w = img.shape[:2]

print(f"Reference resolution: {detector.ref_width}x{detector.ref_height}")
print(f"Actual image size: {w}x{h}")
print(f"Scale factor: {w/detector.ref_width:.3f}x, {h/detector.ref_height:.3f}y")
print()

# Extract and save each card region
card_num = 0
for position_name, regions in detector.positions.items():
    print(f"\n{position_name.upper()}:")
    for idx, (x, y, width, height) in enumerate(regions):
        # Scale coordinates
        sx = int(x * w / detector.ref_width)
        sy = int(y * h / detector.ref_height)
        sw = int(width * w / detector.ref_width)
        sh = int(height * h / detector.ref_height)
        
        print(f"  Card {idx+1}: x={sx}, y={sy}, w={sw}, h={sh}")
        
        # Extract card region
        card_img = img[sy:sy+sh, sx:sx+sw]
        
        # Save full card
        output_path = f'debug_cards/{card_num:02d}_{position_name}_{idx+1}_full.png'
        cv2.imwrite(output_path, card_img)
        
        # Extract and save corner (what OCR sees)
        if card_img.shape[0] > 0 and card_img.shape[1] > 0:
            corner_h, corner_w = card_img.shape[:2]
            corner = card_img[5:int(corner_h*0.45), 5:int(corner_w*0.45)]
            corner_path = f'debug_cards/{card_num:02d}_{position_name}_{idx+1}_corner.png'
            cv2.imwrite(corner_path, corner)
        
        card_num += 1

print()
print("=" * 70)
print(f"✅ Saved {card_num} card regions to debug_cards/")
print("=" * 70)
print()
print("Next steps:")
print("1. Open debug_cards/ folder")
print("2. Check if card images look correct")
print("3. Check if corner images show the rank and suit clearly")
print()
print("If cards are not visible or in wrong positions:")
print("  → Card positions in config need adjustment")

# Also save the full image with rectangles drawn
img_with_boxes = img.copy()
for position_name, regions in detector.positions.items():
    for (x, y, width, height) in regions:
        sx = int(x * w / detector.ref_width)
        sy = int(y * h / detector.ref_height)
        sw = int(width * w / detector.ref_width)
        sh = int(height * h / detector.ref_height)
        
        # Draw rectangle
        cv2.rectangle(img_with_boxes, (sx, sy), (sx+sw, sy+sh), (0, 255, 0), 2)

cv2.imwrite('debug_cards/00_full_image_with_boxes.png', img_with_boxes)
print("Also saved: debug_cards/00_full_image_with_boxes.png")
print("  → Shows where the detector is looking for cards")
