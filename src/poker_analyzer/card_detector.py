"""Card detection using EasyOCR."""

import cv2
import numpy as np
import easyocr
from typing import Optional, Dict, List
import logging

from .config import config

logger = logging.getLogger(__name__)


class CardDetector:
    """Detect and recognize playing cards using EasyOCR."""
    
    def __init__(self):
        """Initialize card detector with EasyOCR."""
        logger.info("Initializing EasyOCR (this may take a moment)...")
        self.reader = easyocr.Reader(['en'], gpu=False, verbose=False)
        logger.info("EasyOCR initialized")
        
        # Load configuration
        self.ref_width = config.reference_resolution['width']
        self.ref_height = config.reference_resolution['height']
        self.positions = config.card_positions
        
        # Recognition settings
        self.corner_crop_ratio = config.get('recognition.corner_crop_ratio', 0.45)
        
        logger.info("Card detector ready")
    
    def detect_all_cards(self, img: np.ndarray) -> Dict[str, List[str]]:
        """Detect all cards from screenshot."""
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
        """Recognize a single card."""
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
        """Read card rank using EasyOCR."""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(corner_img, cv2.COLOR_BGR2GRAY)
            
            # Enhance contrast
            _, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY_INV)
            
            # Use EasyOCR
            results = self.reader.readtext(thresh, detail=0, allowlist='A23456789JQK10')
            
            if not results:
                return None
            
            # Combine all text
            text = ' '.join(results).upper()
            
            # Parse rank
            rank = self._parse_rank(text)
            return rank
            
        except Exception as e:
            logger.error(f"OCR error: {e}")
            return None
    
    def _parse_rank(self, text: str) -> Optional[str]:
        """Parse rank from OCR text."""
        text = text.strip().upper().replace('O', '0').replace('I', '1').replace('l', '1')
        
        # Check for each rank in priority order
        for rank in ['10', 'A', 'K', 'Q', 'J', '9', '8', '7', '6', '5', '4', '3', '2']:
            if rank in text:
                return rank
        
        return None
    
    def _detect_suit(self, corner_img: np.ndarray) -> Optional[str]:
        """Detect suit by color and shape analysis."""
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
        
        # First determine if red or black
        is_red = r > min_r and r > b + r_over_b and r > g + r_over_g
        is_black = r < max_r and g < max_g and b < max_b
        
        if not (is_red or is_black):
            logger.warning(f"Could not determine color: R={r:.1f}, G={g:.1f}, B={b:.1f}")
            return None
        
        # Analyze shape to distinguish between suits of same color
        try:
            suit = self._distinguish_suit_by_shape(suit_region, is_red)
            if suit:
                logger.debug(f"Detected suit {suit} (red={is_red})")
                return suit
        except Exception as e:
            logger.warning(f"Shape analysis failed: {e}")
        
        # Fallback to color only
        return 'H' if is_red else 'S'
    
    def _distinguish_suit_by_shape(self, suit_region: np.ndarray, is_red: bool) -> Optional[str]:
        """Distinguish between suits of the same color using shape analysis."""
        # Convert to grayscale
        gray = cv2.cvtColor(suit_region, cv2.COLOR_BGR2GRAY)
        
        # Threshold to get binary image
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
        
        # Find contours
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return None
        
        # Get largest contour (the suit symbol)
        largest_contour = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest_contour)
        
        # Need minimum area to analyze
        if area < 10:
            return None
        
        perimeter = cv2.arcLength(largest_contour, True)
        
        # Calculate circularity
        circularity = 0
        if perimeter > 0:
            circularity = 4 * np.pi * area / (perimeter * perimeter)
        
        # Bounding box aspect ratio
        x, y, w_box, h_box = cv2.boundingRect(largest_contour)
        aspect_ratio = w_box / h_box if h_box > 0 else 1.0
        
        # Convex hull ratio
        hull = cv2.convexHull(largest_contour)
        hull_area = cv2.contourArea(hull)
        solidity = area / hull_area if hull_area > 0 else 0
        
        logger.debug(f"Shape: circ={circularity:.3f}, aspect={aspect_ratio:.3f}, solid={solidity:.3f}")
        
        if is_red:
            # Hearts vs Diamonds
            if circularity > 0.55 or solidity > 0.80:
                return 'H'  # Hearts (rounded)
            else:
                return 'D'  # Diamonds (angular)
        else:
            # Spades vs Clubs
            if aspect_ratio < 0.80:
                return 'S'  # Spades (tall/pointed)
            else:
                return 'C'  # Clubs (wide/compact)