"""Debug card detection with separate rank and suit regions."""

import sys
sys.path.insert(0, 'src')

import cv2
import os
import yaml

print("=" * 70)
print("DEBUG: Card Region Extraction (Rank + Suit Separate)")
print("=" * 70)

# Load image
img_path = './test_capture.png'
img = cv2.imread(img_path)

if img is None:
    print(f"❌ Could not load {img_path}")
    sys.exit(1)

print(f"✅ Image loaded: {img.shape[1]}x{img.shape[0]}")
print()

# Load config
with open('config/custom_config.yaml', 'r') as f:
    config_data = yaml.safe_load(f)

ref_width = config_data['reference_resolution']['width']
ref_height = config_data['reference_resolution']['height']
card_positions = config_data['card_positions']

img_h, img_w = img.shape[:2]

print(f"Reference resolution: {ref_width}x{ref_height}")
print(f"Actual image size: {img_w}x{img_h}")
print(f"Scale factor: {img_w/ref_width:.3f}x, {img_h/ref_height:.3f}y")
print()

# Create debug directory
os.makedirs('debug_cards', exist_ok=True)

# Process each card
card_num = 0
img_with_boxes = img.copy()

for position_name, card_list in card_positions.items():
    print(f"\n{position_name.upper()}:")
    
    for idx, card_config in enumerate(card_list):
        pos = card_config['position']
        rank_reg = card_config['rank_region']
        suit_reg = card_config['suit_region']
        
        x, y, width, height = pos
        
        # Scale card position
        sx = int(x * img_w / ref_width)
        sy = int(y * img_h / ref_height)
        sw = int(width * img_w / ref_width)
        sh = int(height * img_h / ref_height)
        
        print(f"  Card {idx+1}: x={sx}, y={sy}, w={sw}, h={sh}")
        
        # Extract full card
        card_img = img[sy:sy+sh, sx:sx+sw]
        
        if card_img.size == 0:
            print(f"    ⚠️  Empty card region!")
            continue
        
        # Save full card
        full_path = f'debug_cards/{card_num:02d}_{position_name}_{idx+1}_full.png'
        cv2.imwrite(full_path, card_img)
        
        # Extract rank region
        ch, cw = card_img.shape[:2]
        rt, rl, rb, rr = rank_reg
        rank_img = card_img[int(ch*rt):int(ch*rb), int(cw*rl):int(cw*rr)]
        
        rank_path = f'debug_cards/{card_num:02d}_{position_name}_{idx+1}_rank.png'
        cv2.imwrite(rank_path, rank_img)
        print(f"    Rank region: {rank_img.shape} → {rank_path}")
        
        # Extract suit region
        st, sl, sb, sr = suit_reg
        suit_img = card_img[int(ch*st):int(ch*sb), int(cw*sl):int(cw*sr)]
        
        suit_path = f'debug_cards/{card_num:02d}_{position_name}_{idx+1}_suit.png'
        cv2.imwrite(suit_path, suit_img)
        print(f"    Suit region: {suit_img.shape} → {suit_path}")
        
        # Draw boxes on full image
        # Card box (green)
        cv2.rectangle(img_with_boxes, (sx, sy), (sx+sw, sy+sh), (0, 255, 0), 2)
        
        # Rank box (blue)
        rx1 = sx + int(cw*rl)
        ry1 = sy + int(ch*rt)
        rx2 = sx + int(cw*rr)
        ry2 = sy + int(ch*rb)
        cv2.rectangle(img_with_boxes, (rx1, ry1), (rx2, ry2), (255, 0, 0), 1)
        
        # Suit box (red)
        sux1 = sx + int(cw*sl)
        suy1 = sy + int(ch*st)
        sux2 = sx + int(cw*sr)
        suy2 = sy + int(ch*sb)
        cv2.rectangle(img_with_boxes, (sux1, suy1), (sux2, suy2), (0, 0, 255), 1)
        
        card_num += 1

print()
print("=" * 70)
print(f"✅ Saved {card_num} card regions to debug_cards/")
print("=" * 70)
print()
print("Files created:")
print("  XX_position_N_full.png  - Full card image")
print("  XX_position_N_rank.png  - Rank extraction region (for OCR)")
print("  XX_position_N_suit.png  - Suit extraction region (for color/shape)")
print()

# Save image with boxes
cv2.imwrite('debug_cards/00_full_image_with_boxes.png', img_with_boxes)
print("Also saved: debug_cards/00_full_image_with_boxes.png")
print("  Green = Card boundary")
print("  Blue = Rank region")
print("  Red = Suit region")
print()
print("Check these images and adjust regions in config/custom_config.yaml")
print("Then run this script again until regions look correct")