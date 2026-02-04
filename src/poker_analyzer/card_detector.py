"""Card detection with separate rank and suit regions."""

import cv2
import numpy as np
import easyocr
from typing import Optional, Dict, List
import logging

from .config import config

logger = logging.getLogger(__name__)


class CardDetector:
    """Detect and recognize playing cards using separate rank/suit regions."""
    
    def __init__(self):
        """Initialize card detector with EasyOCR."""
        logger.info("Initializing EasyOCR (this may take a moment)...")
        self.reader = easyocr.Reader(['en'], gpu=False, verbose=False)
        logger.info("EasyOCR initialized")
        
        # Load configuration
        self.ref_width = config.reference_resolution['width']
        self.ref_height = config.reference_resolution['height']
        self.card_positions = config.card_positions
        
        logger.info("Card detector ready")
    
    def detect_all_cards(self, img: np.ndarray) -> Dict[str, List[str]]:
        """Detect all cards from screenshot."""
        h, w = img.shape[:2]
        
        cards = {
            'board': [],
            'left_hand': [],
            'right_hand': []
        }
        
        for position_name, card_list in self.card_positions.items():
            for card_config in card_list:
                # Get card position
                pos = card_config['position']
                x, y, width, height = pos
                
                # Scale coordinates to actual image size
                sx = int(x * w / self.ref_width)
                sy = int(y * h / self.ref_height)
                sw = int(width * w / self.ref_width)
                sh = int(height * h / self.ref_height)
                
                # Extract card region
                card_img = img[sy:sy+sh, sx:sx+sw]
                
                # Recognize card with its specific regions
                card = self._recognize_card(card_img, card_config)
                
                if card:
                    cards[position_name].append(card)
                    logger.debug(f"Detected {card} in {position_name}")
                else:
                    logger.warning(f"Failed to detect card in {position_name} at ({sx}, {sy})")
        
        return cards
    
    def _recognize_card(self, card_img: np.ndarray, card_config: dict) -> Optional[str]:
        """
        Recognize a single card using separate rank and suit regions.
        
        Args:
            card_img: Full card image
            card_config: Config dict with 'rank_region' and 'suit_region'
        """
        # Get region definitions
        rank_reg = card_config.get('rank_region', [0.0, 0.0, 0.4, 0.5])
        suit_reg = card_config.get('suit_region', [0.5, 0.05, 0.75, 0.45])
        
        h, w = card_img.shape[:2]
        
        # Extract rank region
        rt, rl, rb, rr = rank_reg
        rank_img = card_img[int(h*rt):int(h*rb), int(w*rl):int(w*rr)]
        
        if rank_img.size == 0:
            logger.warning("Empty rank region")
            return None
        
        # Extract suit region
        st, sl, sb, sr = suit_reg
        suit_img = card_img[int(h*st):int(h*sb), int(w*sl):int(w*sr)]
        
        if suit_img.size == 0:
            logger.warning("Empty suit region")
            return None
        
        # Read rank
        rank = self._read_rank(rank_img)
        if not rank:
            logger.debug(f"Failed to read rank from region {rank_img.shape}")
            return None
        
        # Detect suit
        suit = self._detect_suit_from_region(suit_img)
        if not suit:
            logger.debug(f"Failed to detect suit from region {suit_img.shape}")
            return None
        
        return f"{rank}{suit}"
    
    def _read_rank(self, rank_img: np.ndarray) -> Optional[str]:
        """Read card rank using EasyOCR."""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(rank_img, cv2.COLOR_BGR2GRAY)
            
            # Resize if too small
            h, w = gray.shape
            if h < 100 or w < 100:
                scale = 3
                gray = cv2.resize(gray, (w*scale, h*scale), interpolation=cv2.INTER_CUBIC)
                logger.debug(f"Resized rank from {w}x{h} to {gray.shape[1]}x{gray.shape[0]}")
            
            # Try multiple preprocessing methods
            preprocessing = [
                lambda g: g,  # Original
                lambda g: cv2.threshold(g, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1],
                lambda g: cv2.threshold(g, 180, 255, cv2.THRESH_BINARY_INV)[1],
                lambda g: cv2.threshold(g, 150, 255, cv2.THRESH_BINARY_INV)[1],
            ]
            
            for i, preprocess in enumerate(preprocessing):
                processed = preprocess(gray)
                results = self.reader.readtext(processed, detail=0, allowlist='A23456789JQK10')
                
                if not results:
                    results = self.reader.readtext(processed, detail=0)
                
                if results:
                    text = ' '.join(results).upper()
                    rank = self._parse_rank(text)
                    if rank:
                        logger.debug(f"OCR method {i}: detected '{rank}' from '{text}'")
                        return rank
            
            logger.warning(f"All OCR methods failed")
            return None
            
        except Exception as e:
            logger.error(f"OCR error: {e}")
            return None
    
    def _parse_rank(self, text: str) -> Optional[str]:
        """Parse rank from OCR text."""
        text = text.strip().upper().replace('O', '0').replace('I', '1').replace('l', '1')
        
        for rank in ['10', 'A', 'K', 'Q', 'J', '9', '8', '7', '6', '5', '4', '3', '2']:
            if rank in text:
                return rank
        
        return None
    
    def _detect_suit_from_region(self, suit_img: np.ndarray) -> Optional[str]:
        """
        Detect suit from dedicated suit region.
        
        Args:
            suit_img: Image region containing only the suit symbol
            
        Returns:
            Suit character ('H', 'D', 'S', 'C') or None
        """
        # Get average color
        avg_color = np.mean(suit_img, axis=(0, 1))
        b, g, r = avg_color
        
        # Get thresholds
        red_cfg = config.get('recognition.red_threshold', {})
        black_cfg = config.get('recognition.black_threshold', {})
        
        min_r = red_cfg.get('min_r', 130)
        r_over_b = red_cfg.get('r_over_b', 20)
        r_over_g = red_cfg.get('r_over_g', 12)
        max_r = black_cfg.get('max_r', 140)
        max_g = black_cfg.get('max_g', 140)
        max_b = black_cfg.get('max_b', 140)
        
        # Determine color
        is_red = r > min_r and r > b + r_over_b and r > g + r_over_g
        
        # Special case for very light red
        if not is_red and r > 200 and r > b and r > g:
            is_red = True
            logger.debug(f"Light red: R={r:.1f}")
        
        is_black = r < max_r and g < max_g and b < max_b
        
        if not (is_red or is_black):
            logger.warning(f"Unknown color: R={r:.1f}, G={g:.1f}, B={b:.1f}")
            return None
        
        logger.debug(f"Suit color: R={r:.1f}, G={g:.1f}, B={b:.1f}, is_red={is_red}")
        
        # Analyze shape
        suit = self._analyze_shape(suit_img, is_red)
        return suit
    
    def _analyze_shape(self, suit_img: np.ndarray, is_red: bool) -> Optional[str]:
        """Analyze suit symbol shape."""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(suit_img, cv2.COLOR_BGR2GRAY)
            
            # Threshold
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            
            # Find contours
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if not contours:
                logger.warning("No contours found")
                return 'H' if is_red else 'S'
            
            # Get largest contour
            largest = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(largest)
            
            if area < 50:
                logger.warning(f"Contour too small: {area}")
                return 'H' if is_red else 'S'
            
            perimeter = cv2.arcLength(largest, True)
            if perimeter == 0:
                return 'H' if is_red else 'S'
            
            # Calculate metrics
            circularity = 4 * np.pi * area / (perimeter * perimeter)
            
            x, y, w, h = cv2.boundingRect(largest)
            aspect_ratio = w / h if h > 0 else 1.0
            
            hull = cv2.convexHull(largest)
            hull_area = cv2.contourArea(hull)
            solidity = area / hull_area if hull_area > 0 else 0
            
            bbox_area = w * h
            extent = area / bbox_area if bbox_area > 0 else 0
            
            logger.debug(f"Shape: circ={circularity:.3f}, aspect={aspect_ratio:.3f}, "
                        f"solid={solidity:.3f}, extent={extent:.3f}")
            
            if is_red:
                # Hearts vs Diamonds scoring
                heart_score = 0
                diamond_score = 0
                
                # Circularity
                if circularity < 0.35:
                    diamond_score += 3
                elif circularity < 0.50:
                    diamond_score += 1
                elif circularity > 0.65:
                    heart_score += 2
                elif circularity > 0.54:
                    heart_score += 1
                
                # Solidity
                if solidity < 0.70:
                    diamond_score += 2
                elif solidity > 0.90:
                    heart_score += 1
                elif solidity > 0.80:
                    heart_score += 1
                
                # Extent
                if extent < 0.50:
                    diamond_score += 3
                elif extent < 0.52:
                    diamond_score += 1
                elif extent > 0.60:
                    heart_score += 2
                elif extent > 0.55:
                    heart_score += 1
                
                # Aspect ratio
                if aspect_ratio < 0.75:
                    diamond_score += 1
                elif aspect_ratio > 0.85:
                    heart_score += 1
                
                logger.debug(f"Red scoring: H={heart_score}, D={diamond_score}")
                
                # Decide
                if diamond_score > heart_score:
                    return 'D'
                elif heart_score > diamond_score:
                    return 'H'
                else:
                    # Tie-breaker
                    if solidity > 0.82:
                        logger.debug("Tie → Heart (solidity)")
                        return 'H'
                    elif extent < 0.53:
                        logger.debug("Tie → Diamond (extent)")
                        return 'D'
                    else:
                        return 'H'
            else:
                # Spades vs Clubs
                if aspect_ratio < 0.85:
                    logger.debug(f"Black: aspect {aspect_ratio:.3f} → Spades")
                    return 'S'
                else:
                    logger.debug(f"Black: aspect {aspect_ratio:.3f} → Clubs")
                    return 'C'
                    
        except Exception as e:
            logger.error(f"Shape analysis error: {e}", exc_info=True)
            return 'H' if is_red else 'S'