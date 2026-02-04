"""Poker hand evaluation logic."""

from itertools import combinations
from collections import Counter
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)


class PokerEvaluator:
    """Evaluate and compare poker hands."""
    
    # Hand rankings
    HAND_RANKS = {
        'Royal Flush': 10,
        'Straight Flush': 9,
        'Four of a Kind': 8,
        'Full House': 7,
        'Flush': 6,
        'Straight': 5,
        'Three of a Kind': 4,
        'Two Pair': 3,
        'One Pair': 2,
        'High Card': 1
    }
    
    # Rank values
    RANK_VALUES = {
        '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8,
        '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14
    }
    
    def __init__(self):
        """Initialize poker evaluator."""
        logger.info("Poker evaluator initialized")
    
    def evaluate_hand(self, hole_cards: List[str], board: List[str]) -> Tuple[int, str]:
        """
        Evaluate the best 5-card hand from 2 hole cards + 5 board cards.
        
        Returns:
            Tuple of (rank_value, hand_name)  # Only 2 values!
        """
        if len(hole_cards) != 2:
            logger.error(f"Invalid hole cards count: {len(hole_cards)}")
            return 0, "Invalid"
        
        if len(board) != 5:
            logger.error(f"Invalid board count: {len(board)}")
            return 0, "Invalid"
        
        all_cards = hole_cards + board
        
        best_rank = 0
        best_name = "High Card"
        best_5 = []
        
        # Try all 21 combinations of 5 cards from 7
        for combo in combinations(all_cards, 5):
            rank, name = self._rank_5_cards(list(combo))
            
            if rank > best_rank:
                best_rank = rank
                best_name = name
                best_5 = list(combo)
        
        logger.debug(f"Hand {hole_cards} + {board} = {best_name} with {best_5}")
        
        return best_rank, best_name  # Return only 2 values
    
    def _rank_5_cards(self, cards: List[str]) -> Tuple[int, str]:
        """
        Rank exactly 5 cards.
        
        Args:
            cards: List of 5 card strings
            
        Returns:
            Tuple of (rank_value, hand_name)
        """
        # Parse cards
        ranks = [c[:-1] for c in cards]  # e.g., 'A' from 'AH'
        suits = [c[-1] for c in cards]   # e.g., 'H' from 'AH'
        
        # Convert ranks to values
        rank_values = [self.RANK_VALUES[r] for r in ranks]
        rank_values.sort(reverse=True)
        
        # Check for flush
        is_flush = len(set(suits)) == 1
        
        # Check for straight
        is_straight = self._is_straight(rank_values)
        
        # Count rank frequencies
        rank_counts = Counter(ranks)
        counts = sorted(rank_counts.values(), reverse=True)
        
        # Determine hand
        if is_straight and is_flush:
            if rank_values == [14, 13, 12, 11, 10]:
                return self.HAND_RANKS['Royal Flush'], 'Royal Flush'
            return self.HAND_RANKS['Straight Flush'], 'Straight Flush'
        
        if counts == [4, 1]:
            return self.HAND_RANKS['Four of a Kind'], 'Four of a Kind'
        
        if counts == [3, 2]:
            return self.HAND_RANKS['Full House'], 'Full House'
        
        if is_flush:
            return self.HAND_RANKS['Flush'], 'Flush'
        
        if is_straight:
            return self.HAND_RANKS['Straight'], 'Straight'
        
        if counts == [3, 1, 1]:
            return self.HAND_RANKS['Three of a Kind'], 'Three of a Kind'
        
        if counts == [2, 2, 1]:
            return self.HAND_RANKS['Two Pair'], 'Two Pair'
        
        if counts == [2, 1, 1, 1]:
            return self.HAND_RANKS['One Pair'], 'One Pair'
        
        return self.HAND_RANKS['High Card'], 'High Card'
    
    def _is_straight(self, rank_values: List[int]) -> bool:
        """
        Check if rank values form a straight.
        
        Args:
            rank_values: Sorted list of rank values
            
        Returns:
            True if straight, False otherwise
        """
        # Check normal straight
        if rank_values[0] - rank_values[4] == 4 and len(set(rank_values)) == 5:
            return True
        
        # Check wheel (A-2-3-4-5)
        if rank_values == [14, 5, 4, 3, 2]:
            return True
        
        return False
    
    def compare_hands(self, rank1: int, rank2: int) -> str:
        """
        Compare two hand ranks.
        
        Args:
            rank1: First hand rank value
            rank2: Second hand rank value
            
        Returns:
            'LEFT', 'RIGHT', or 'TIE'
        """
        if rank1 > rank2:
            return 'LEFT'
        elif rank2 > rank1:
            return 'RIGHT'
        else:
            return 'TIE'