"""Screen capture utilities."""

import mss
import numpy as np
import cv2
from typing import Optional, Tuple
import logging

from .config import config

logger = logging.getLogger(__name__)


class ScreenCapture:
    """Handle screen capture operations."""
    
    def __init__(self):
        """Initialize screen capture."""
        self.sct = mss.mss()
        
        # Define capture region
        self.monitor = {
            'top': config.screen_top,
            'left': config.screen_left,
            'width': config.screen_width,
            'height': config.screen_height
        }
        
        logger.info(f"Screen capture initialized: {self.monitor}")
    
    def capture(self) -> Optional[np.ndarray]:
        """
        Capture current screen region.
        
        Returns:
            Captured image as numpy array (BGR format) or None on error
        """
        try:
            screenshot = self.sct.grab(self.monitor)
            
            # Convert to numpy array and BGR format
            img = np.array(screenshot)
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            
            return img
            
        except Exception as e:
            logger.error(f"Screen capture failed: {e}")
            return None
    
    def get_dimensions(self) -> Tuple[int, int]:
        """
        Get capture region dimensions.
        
        Returns:
            (width, height) tuple
        """
        return (self.monitor['width'], self.monitor['height'])
    
    def update_region(self, top: int, left: int, width: int, height: int):
        """
        Update capture region.
        
        Args:
            top: Top Y coordinate
            left: Left X coordinate
            width: Width in pixels
            height: Height in pixels
        """
        self.monitor = {
            'top': top,
            'left': left,
            'width': width,
            'height': height
        }
        logger.info(f"Capture region updated: {self.monitor}")
    
    def __del__(self):
        """Cleanup resources."""
        if hasattr(self, 'sct'):
            self.sct.close()