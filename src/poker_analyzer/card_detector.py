"""Card detection and recognition."""

import cv2
import numpy as np
import pytesseract
from typing import Optional, Dict, List, Tuple
import logging

from .config import config

logger = logging.getLogger(__name__)


class CardDetector:
    """Detect and recognize playing cards from game screenshots."""
    
    def __init__(self):
        """Initialize card detector."""
        # Set tesseract command if specified
        if config.tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = config.tesseract_cmd
        
        # Load configuration
        self.ref_width = config.reference_resolution['width']
        self.ref_height = config.reference_resolution['height']
        self.positions = config.card_positions
        
        # Recognition settings
        self.corner_crop_ratio = config.get('recognition.corner_crop_ratio', 0.45)
        self.ocr_whitelist = config.get('recognition.ocr_whitelist', 'A23456789JQK10')
        
        logger.info("Card detector initialized")
    
    def detect_all_cards(self, img: np.ndarray) -> Dict[str, List[str]]:
        """
        Detect all cards from screenshot.
        
        Args:
            img: Screenshot image (BGR format)
            
        Returns:
            Dictionary with 'board', 'left_hand', 'right_hand' card lists
        """
        h, w = img.shape[:2]
        
        cards = {
            'board': [],
            'left_hand': [],
            'right_hand': []
        }
        
        for position_name, regions in self.positions.items():
            for (x, y, width, height) in regions:
                # Scale coordinates to actual image size
                sx = int(x * w / self.ref_width)
                sy = int(y * h / self.ref_height)
                sw = int(width * w / self.ref_width)
                sh = int(height * h / self.ref_height)
                
                # Extract card region
                card_img = img[sy:sy+sh, sx:sx+sw]
                
                # Recognize card
                card = self._recognize_card(card_img)
                
                if card:
                    cards[position_name].append(card)
                    logger.debug(f"Detected {card} in {position_name}")
                else:
                    logger.warning(f"Failed to detect card in {position_name} at ({sx}, {sy})")
        
        return cards
    
    def _recognize_card(self, card_img: np.ndarray) -> Optional[str]:
        """
        Recognize a single card.
        
        Args:
            card_img: Card image region
            
        Returns:
            Card string (e.g., 'AH', '7D') or None if recognition failed
        """
        # Extract top-left corner
        h, w = card_img.shape[:2]
        corner = card_img[5:int(h*self.corner_crop_ratio), 5:int(w*self.corner_crop_ratio)]
        
        # Read rank
        rank = self._read_rank(corner)
        if not rank:
            return None
        
        # Detect suit
        suit = self._detect_suit(corner)
        if not suit:
            return None
        
        return f"{rank}{suit}"
    
    def _read_rank(self, corner_img: np.ndarray) -> Optional[str]:
        """
        Read card rank using OCR.
        
        Args:
            corner_img: Corner image containing rank
            
        Returns:
            Rank string (A, K, Q, J, 10, 9, ..., 2) or None
        """
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(corner_img, cv2.COLOR_BGR2GRAY)
            
            # Threshold
            _, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY_INV)
            
            # OCR
            custom_config = f'--oem 3 --psm 6 -c tessedit_char_whitelist={self.ocr_whitelist}'
            text = pytesseract.image_to_string(thresh, config=custom_config)
            
            # Parse rank
            rank = self._parse_rank(text)
            return rank
            
        except Exception as e:
            logger.error(f"OCR error: {e}")
            return None
    
    def _parse_rank(self, text: str) -> Optional[str]:
        """
        Parse rank from OCR text.
        
        Args:
            text: Raw OCR text
            
        Returns:
            Parsed rank or None
        """
        text = text.strip().upper().replace('O', '0').replace('I', '1')
        
        # Check for each rank in priority order
        for rank in ['10', 'A', 'K', 'Q', 'J', '9', '8', '7', '6', '5', '4', '3', '2']:
            if rank in text:
                return rank
        
        return None
    
    def _detect_suit(self, corner_img: np.ndarray) -> Optional[str]:
        """
        Detect suit by color analysis.
        
        Args:
            corner_img: Corner image containing suit symbol
            
        Returns:
            Suit character ('H', 'D', 'S', 'C') or None
        """
        h, w = corner_img.shape[:2]
        
        # Sample suit symbol area
        suit_region = corner_img[int(h*0.25):int(h*0.55), int(w*0.15):int(w*0.45)]
        
        # Calculate average color
        avg_color = np.mean(suit_region, axis=(0, 1))
        b, g, r = avg_color
        
        # Get thresholds from config
        red_cfg = config.get('recognition.red_threshold', {})
        black_cfg = config.get('recognition.black_threshold', {})
        
        min_r = red_cfg.get('min_r', 140)
        r_over_b = red_cfg.get('r_over_b', 40)
        r_over_g = red_cfg.get('r_over_g', 20)
        
        max_r = black_cfg.get('max_r', 100)
        max_g = black_cfg.get('max_g', 100)
        max_b = black_cfg.get('max_b', 100)
        
        # Detect suit by color
        if r > min_r and r > b + r_over_b and r > g + r_over_g:
            # Red suit - default to Hearts
            # TODO: Add shape detection to distinguish Hearts vs Diamonds
            return 'H'
        elif r < max_r and g < max_g and b < max_b:
            # Black suit - default to Spades
            # TODO: Add shape detection to distinguish Spades vs Clubs
            return 'S'
        
        logger.warning(f"Could not determine suit from color: R={r:.1f}, G={g:.1f}, B={b:.1f}")
        return None