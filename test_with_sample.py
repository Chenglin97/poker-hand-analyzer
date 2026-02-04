"""Test analyzer with sample image."""

import sys
sys.path.insert(0, 'src')

import cv2
from poker_analyzer.card_detector import CardDetector
from poker_analyzer.poker_evaluator import PokerEvaluator
from poker_analyzer.utils import setup_logging

# Setup logging to see what's happening
setup_logging(log_level='DEBUG')

print("=" * 70)
print("Testing Card Detection and Analysis with Sample Image")
print("=" * 70)
print()

# Load your sample image
img_path = './test_capture.png'
print(f"Loading: {img_path}")

img = cv2.imread(img_path)

if img is None:
    print(f"❌ Could not load image from {img_path}")
    sys.exit(1)

print(f"✅ Image loaded successfully")
print(f"   Size: {img.shape[1]}x{img.shape[0]} pixels")
print()

# Initialize detector
print("Initializing card detector...")
detector = CardDetector()
print("✅ Card detector ready")
print()

# Detect cards
print("=" * 70)
print("STEP 1: Detecting Cards")
print("=" * 70)
cards = detector.detect_all_cards(img)

print("\nDetected cards:")
print(f"  Board:      {cards['board']}")
print(f"  Left hand:  {cards['left_hand']}")
print(f"  Right hand: {cards['right_hand']}")
print()

# Validate detection
board_count = len(cards['board'])
left_count = len(cards['left_hand'])
right_count = len(cards['right_hand'])

print("Validation:")
print(f"  Board:      {board_count}/5 cards {'✅' if board_count == 5 else '❌'}")
print(f"  Left hand:  {left_count}/2 cards {'✅' if left_count == 2 else '❌'}")
print(f"  Right hand: {right_count}/2 cards {'✅' if right_count == 2 else '❌'}")
print()

if board_count != 5 or left_count != 2 or right_count != 2:
    print("❌ Card detection incomplete!")
    print("\nThis means the card recognition isn't working properly.")
    print("We may need to adjust OCR settings or card positions.")
    sys.exit(1)

print("✅ All 9 cards detected successfully!")
print()

# Evaluate hands
print("=" * 70)
print("STEP 2: Evaluating Poker Hands")
print("=" * 70)
print()

evaluator = PokerEvaluator()

print("Evaluating left hand...")
left_rank, left_name = evaluator.evaluate_hand(cards['left_hand'], cards['board'])
print(f"  Left:  {' '.join(cards['left_hand'])} + Board → {left_name}")

print("\nEvaluating right hand...")
right_rank, right_name = evaluator.evaluate_hand(cards['right_hand'], cards['board'])
print(f"  Right: {' '.join(cards['right_hand'])} + Board → {right_name}")
print()

# Compare hands
print("=" * 70)
print("STEP 3: Determining Winner")
print("=" * 70)
print()

winner = evaluator.compare_hands(left_rank, right_rank)

print(f"Left hand rank:  {left_rank} ({left_name})")
print(f"Right hand rank: {right_rank} ({right_name})")
print()

# Final result
print("=" * 70)
print("FINAL RESULT")
print("=" * 70)
print()
print(f"Board:      {' '.join(cards['board'])}")
print(f"Left Hand:  {' '.join(cards['left_hand'])} → {left_name}")
print(f"Right Hand: {' '.join(cards['right_hand'])} → {right_name}")
print()
print(f"🎯 **{winner} WINS!**")
print()
print("=" * 70)
print("✅ TEST PASSED - Card detection and analysis working!")
print("=" * 70)
