"""Configuration management for Poker Hand Analyzer."""

import os
import yaml
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration manager."""
    
    def __init__(self, config_path: str = None):
        """
        Initialize configuration.
        
        Args:
            config_path: Path to YAML config file. If None, tries custom then default.
        """
        if config_path is None:
            # Try custom config first, fall back to default
            custom_path = Path(__file__).parent.parent.parent / "config" / "custom_config.yaml"
            default_path = Path(__file__).parent.parent.parent / "config" / "default_config.yaml"
            
            if custom_path.exists():
                config_path = custom_path
                print(f"📝 Using custom config: {custom_path.name}")
            else:
                config_path = default_path
                print(f"📝 Using default config: {default_path.name}")
        
        with open(config_path, 'r') as f:
            self._config = yaml.safe_load(f)
        
        # Override with environment variables
        self._load_env_overrides()
    
    def _load_env_overrides(self):
        """Load configuration overrides from environment variables."""
        # Screen capture settings
        self.screen_top = int(os.getenv('SCREEN_TOP', 0))
        self.screen_left = int(os.getenv('SCREEN_LEFT', 0))
        self.screen_width = int(os.getenv('SCREEN_WIDTH', 1520))
        self.screen_height = int(os.getenv('SCREEN_HEIGHT', 560))
        
        # Analysis settings
        self.analysis_interval = float(os.getenv('ANALYSIS_INTERVAL', 2.0))
        self.confidence_threshold = float(os.getenv('CONFIDENCE_THRESHOLD', 0.7))
        
        # Logging
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.log_file = os.getenv('LOG_FILE', 'poker_analyzer.log')
        
        # OCR
        self.ocr_engine = os.getenv('OCR_ENGINE', 'easyocr')
        self.tesseract_cmd = os.getenv('TESSERACT_CMD', '')
        
        # Display
        self.show_visual_feedback = os.getenv('SHOW_VISUAL_FEEDBACK', 'true').lower() == 'true'
        self.save_screenshots = os.getenv('SAVE_SCREENSHOTS', 'false').lower() == 'true'
        self.screenshot_dir = os.getenv('SCREENSHOT_DIR', 'screenshots/')
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key.
        
        Args:
            key: Configuration key (supports dot notation, e.g., 'card_positions.board')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    @property
    def card_positions(self) -> Dict[str, list]:
        """Get card position configuration."""
        return self._config.get('card_positions', {})
    
    @property
    def reference_resolution(self) -> Dict[str, int]:
        """Get reference resolution."""
        return self._config.get('reference_resolution', {'width': 1520, 'height': 560})


# Global config instance
config = Config()