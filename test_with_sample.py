"""Test analyzer with sample image and verification."""

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
img_path = './live_debug.png'
print(f"Loading: {img_path}")

img = cv2.imread(img_path)

if img is None:
    print(f"❌ Could not load image from {img_path}")
    sys.exit(1)

print(f"✅ Image loaded successfully")
print(f"   Size: {img.shape[1]}x{img.shape[0]} pixels")
print()

# Define expected cards for verification
EXPECTED_CARDS = {
    'board': ['6D', '4S', '8C', '10S', '5H'],
    'left_hand': ['AH', '3H'],
    'right_hand': ['9H', 'KD']
}

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

# Verify cards match expected
print("=" * 70)
print("STEP 2: Verifying Card Accuracy")
print("=" * 70)
print()

all_correct = True
errors = []

for position in ['board', 'left_hand', 'right_hand']:
    expected = EXPECTED_CARDS[position]
    detected = cards[position]
    
    print(f"{position.upper().replace('_', ' ')}:")
    
    for i, (exp, det) in enumerate(zip(expected, detected)):
        # Check rank
        exp_rank = exp[:-1]
        det_rank = det[:-1]
        rank_match = exp_rank == det_rank
        
        # Check suit
        exp_suit = exp[-1]
        det_suit = det[-1]
        suit_match = exp_suit == det_suit
        
        status = "✅" if (rank_match and suit_match) else "❌"
        
        print(f"  Card {i+1}: Expected {exp}, Detected {det} {status}")
        
        if not rank_match:
            errors.append(f"{position} card {i+1}: Rank mismatch - expected {exp_rank}, got {det_rank}")
            all_correct = False
        
        if not suit_match:
            errors.append(f"{position} card {i+1}: Suit mismatch - expected {exp_suit}, got {det_suit}")
            all_correct = False
    
    print()

if all_correct:
    print("✅ ALL CARDS DETECTED CORRECTLY!")
else:
    print("❌ CARD DETECTION ERRORS:")
    for error in errors:
        print(f"  • {error}")
    print()
    print("Suit Legend: H=Hearts, D=Diamonds, S=Spades, C=Clubs")
    print()

print()

# Evaluate hands
print("=" * 70)
print("STEP 3: Evaluating Poker Hands")
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

# Compare hands with tie-breaking
print("=" * 70)
print("STEP 4: Determining Winner")
print("=" * 70)
print()

# Basic comparison
if left_rank > right_rank:
    winner = 'LEFT'
elif right_rank > left_rank:
    winner = 'RIGHT'
else:
    # Tie-breaker: compare highest cards
    print("Same hand rank - comparing high cards...")
    
    left_values = sorted([evaluator.RANK_VALUES[c[:-1]] for c in cards['left_hand']], reverse=True)
    right_values = sorted([evaluator.RANK_VALUES[c[:-1]] for c in cards['right_hand']], reverse=True)
    
    print(f"  Left high cards: {left_values}")
    print(f"  Right high cards: {right_values}")
    
    for lv, rv in zip(left_values, right_values):
        if lv > rv:
            winner = 'LEFT'
            print(f"  Left wins tie-breaker: {lv} > {rv}")
            break
        elif rv > lv:
            winner = 'RIGHT'
            print(f"  Right wins tie-breaker: {rv} > {lv}")
            break
    else:
        winner = 'TIE'
        print("  Complete tie!")
    print()

print(f"Left hand rank:  {left_rank} ({left_name})")
print(f"Right hand rank: {right_rank} ({right_name})")
print()

# Expected winner verification
EXPECTED_WINNER = 'LEFT'  # A♥ high beats K♦ high

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

# Verify winner
if winner == EXPECTED_WINNER:
    print(f"✅ Winner correct! Expected {EXPECTED_WINNER}, got {winner}")
else:
    print(f"❌ Winner incorrect! Expected {EXPECTED_WINNER}, got {winner}")

print()
print("=" * 70)

if all_correct and winner == EXPECTED_WINNER:
    print("✅ ALL TESTS PASSED!")
    print("   • Card detection: 100% accurate")
    print("   • Suit detection: 100% accurate")
    print("   • Winner determination: Correct")
else:
    print("⚠️  SOME TESTS FAILED")
    if not all_correct:
        print(f"   • Card/Suit detection: {len(errors)} error(s)")
    if winner != EXPECTED_WINNER:
        print(f"   • Winner determination: Incorrect")

print("=" * 70)