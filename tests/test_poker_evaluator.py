"""Tests for poker evaluator."""

import pytest
from poker_analyzer.poker_evaluator import PokerEvaluator


class TestPokerEvaluator:
    """Test poker hand evaluation."""
    
    @pytest.fixture
    def evaluator(self):
        """Create evaluator instance."""
        return PokerEvaluator()
    
    def test_royal_flush(self, evaluator):
        """Test royal flush detection."""
        board = ['AH', 'KH', 'QH', 'JH', '2C']
        hole = ['10H', '3D']
        
        rank, name = evaluator.evaluate_hand(hole, board)
        assert name == 'Royal Flush'
        assert rank == 10
    
    def test_pair(self, evaluator):
        """Test one pair detection."""
        board = ['AH', 'AC', '7D', '2S', '9H']
        hole = ['KS', 'QD']
        
        rank, name = evaluator.evaluate_hand(hole, board)
        assert name == 'One Pair'
        assert rank == 2
    
    def test_compare_hands(self, evaluator):
        """Test hand comparison."""
        assert evaluator.compare_hands(8, 2) == 'LEFT'
        assert evaluator.compare_hands(2, 8) == 'RIGHT'
        assert evaluator.compare_hands(5, 5) == 'TIE'