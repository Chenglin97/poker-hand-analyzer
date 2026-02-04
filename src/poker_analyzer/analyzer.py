"""Main poker hand analyzer."""

import time
import logging
from typing import Optional, Dict

from .screen_capture import ScreenCapture
from .card_detector import CardDetector
from .poker_evaluator import PokerEvaluator
from .config import config

logger = logging.getLogger(__name__)


class PokerHandAnalyzer:
    """Main analyzer orchestrating all components."""
    
    def __init__(self):
        """Initialize poker hand analyzer."""
        self.screen_capture = ScreenCapture()
        self.card_detector = CardDetector()
        self.evaluator = PokerEvaluator()
        
        logger.info("Poker Hand Analyzer initialized")
    
    def analyze_once(self) -> Optional[Dict]:
        """
        Perform single analysis of current screen.
        
        Returns:
            Analysis result dictionary or None if analysis failed
        """
        start_time = time.time()
        
        # Capture screen
        img = self.screen_capture.capture()
        if img is None:
            logger.error("Screen capture failed")
            return None
        
        # Detect cards
        cards = self.card_detector.detect_all_cards(img)
        
        # Validate detection
        if not self._validate_cards(cards):
            logger.warning("Incomplete card detection")
            return None
        
        # Evaluate hands
        left_rank, left_name = self.evaluator.evaluate_hand(
            cards['left_hand'], 
            cards['board']
        )
        
        right_rank, right_name = self.evaluator.evaluate_hand(
            cards['right_hand'],
            cards['board']
        )
        
        # Determine winner
        winner = self.evaluator.compare_hands(left_rank, right_rank)
        
        # Calculate elapsed time
        elapsed_ms = (time.time() - start_time) * 1000
        
        result = {
            'board': cards['board'],
            'left_hand': cards['left_hand'],
            'left_name': left_name,
            'left_rank': left_rank,
            'right_hand': cards['right_hand'],
            'right_name': right_name,
            'right_rank': right_rank,
            'winner': winner,
            'elapsed_ms': elapsed_ms
        }
        
        logger.info(f"Analysis complete: {winner} wins ({elapsed_ms:.0f}ms)")
        
        return result
    
    def _validate_cards(self, cards: Dict) -> bool:
        """
        Validate that all required cards were detected.
        
        Args:
            cards: Card detection results
            
        Returns:
            True if valid, False otherwise
        """
        if len(cards['board']) != 5:
            logger.warning(f"Invalid board count: {len(cards['board'])}/5")
            return False
        
        if len(cards['left_hand']) != 2:
            logger.warning(f"Invalid left hand count: {len(cards['left_hand'])}/2")
            return False
        
        if len(cards['right_hand']) != 2:
            logger.warning(f"Invalid right hand count: {len(cards['right_hand'])}/2")
            return False
        
        return True
    
    def run_continuous(self):
        """Run continuous analysis loop."""
        logger.info("Starting continuous analysis...")
        logger.info("Press Ctrl+C to stop")
        
        try:
            while True:
                result = self.analyze_once()
                
                if result:
                    self._print_result(result)
                else:
                    print("⚠️  Analysis failed - check logs")
                
                # Wait before next analysis
                time.sleep(config.analysis_interval)
                
        except KeyboardInterrupt:
            logger.info("Stopping analyzer...")
            print("\n✅ Analyzer stopped")
    
    def _print_result(self, result: Dict):
        """
        Print analysis result to console.
        
        Args:
            result: Analysis result dictionary
        """
        print("\n" + "=" * 70)
        print(f"Board:      {' '.join(result['board'])}")
        print(f"Left Hand:  {' '.join(result['left_hand'])} → {result['left_name']}")
        print(f"Right Hand: {' '.join(result['right_hand'])} → {result['right_name']}")
        print(f"\n🎯 **{result['winner']} WINS!**")
        print(f"\nAnalysis time: {result['elapsed_ms']:.0f}ms")
        print("=" * 70)