# Poker Hand Analyzer

Real-time poker hand analyzer using computer vision to determine the winning hand in Texas Hold'em poker games.

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Features

- 🎯 Real-time hand analysis (<500ms)
- 📱 Works with iPhone screen mirroring
- 🤖 Automatic card detection using OCR
- 🎮 Supports Texas Hold'em poker rules
- ⚙️ Configurable via YAML and environment variables
- 📊 Detailed logging and error handling

## Requirements

- macOS (for iPhone mirroring)
- Python 3.8+
- Tesseract OCR
- iPhone with poker game

## Quick Start

### 1. Install System Dependencies
```bash
# Install Tesseract OCR
brew install tesseract
```

### 2. Clone Repository
```bash
git clone https://github.com/yourusername/poker-hand-analyzer.git
cd poker-hand-analyzer
```

### 3. Setup Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows
```

### 4. Install Dependencies
```bash
# Install production dependencies
pip install -r requirements.txt

# Or use make
make install
```

### 5. Configure Environment
```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
nano .env
```

### 6. Mirror iPhone to Mac

**Using QuickTime Player:**
1. Connect iPhone to Mac via USB
2. Open QuickTime Player
3. File → New Movie Recording
4. Click dropdown next to record button → Select your iPhone
5. Position window showing the poker game

### 7. Find Screen Coordinates
```bash
# Run helper script to find QuickTime window position
python scripts/find_window.py
```

Update `.env` with the coordinates.

### 8. Run Analyzer
```bash
# Run continuous analysis
python src/main.py

# Or run single analysis
python src/main.py --once

# Or use make
make run
```

## Configuration

### Environment Variables (.env)
```ini
# Screen Capture
SCREEN_TOP=100
SCREEN_LEFT=100
SCREEN_WIDTH=1456
SCREEN_HEIGHT=819

# Analysis
ANALYSIS_INTERVAL=2.0
CONFIDENCE_THRESHOLD=0.7

# Logging
LOG_LEVEL=INFO
LOG_FILE=poker_analyzer.log
```

### YAML Configuration (config/default_config.yaml)

Customize card positions, recognition thresholds, and more in the YAML config file.

## Usage Examples

### Basic Usage
```bash
# Run with default settings
python src/main.py

# Run with custom config
python src/main.py --config my_config.yaml

# Run with debug logging
python src/main.py --log-level DEBUG

# Run single analysis
python src/main.py --once
```

### Programmatic Usage
```python
from poker_analyzer import PokerHandAnalyzer

# Initialize analyzer
analyzer = PokerHandAnalyzer()

# Analyze once
result = analyzer.analyze_once()

if result:
    print(f"Winner: {result['winner']}")
    print(f"Left hand: {result['left_name']}")
    print(f"Right hand: {result['right_name']}")
```

## Development

### Setup Development Environment
```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Or use make
make install-dev
```

### Run Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/poker_analyzer

# Or use make
make test
```

### Code Quality
```bash
# Run linters
make lint

# Format code
make format
```

### Project Structure
```
poker-hand-analyzer/
├── src/
│   ├── main.py                    # Entry point
│   └── poker_analyzer/
│       ├── __init__.py
│       ├── analyzer.py            # Main analyzer
│       ├── card_detector.py       # Card detection
│       ├── poker_evaluator.py     # Hand evaluation
│       ├── screen_capture.py      # Screen capture
│       ├── config.py              # Configuration
│       └── utils.py               # Utilities
├── tests/                         # Unit tests
├── config/                        # Configuration files
├── docs/                          # Documentation
├── scripts/                       # Helper scripts
├── requirements.txt               # Production dependencies
├── requirements-dev.txt           # Development dependencies
├── setup.py                       # Package setup
├── Makefile                       # Common commands
└── README.md                      # This file
```

## Troubleshooting

### Tesseract Not Found
```bash
# Check tesseract installation
which tesseract

# If not found, install it
brew install tesseract

# Set path in .env
TESSERACT_CMD=/usr/local/bin/tesseract
```

### Screen Capture Issues
```bash
# Verify screen coordinates
python scripts/find_window.py

# Update .env with correct coordinates
SCREEN_TOP=...
SCREEN_LEFT=...
```

### Card Recognition Issues
```bash
# Enable debug logging
python src/main.py --log-level DEBUG

# Check card positions in config/default_config.yaml
# Adjust positions if needed
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- OpenCV for computer vision capabilities
- Tesseract OCR for text recognition
- MSS for screen capture

## Support

If you encounter issues:
1. Check [Troubleshooting](#troubleshooting) section
2. Enable debug logging: `--log-level DEBUG`
3. Open an issue on GitHub with logs and screenshots

## Roadmap

- [ ] Support for multiple poker games
- [ ] Better suit detection (distinguish ♥/♦ and ♠/♣)
- [ ] GUI interface
- [ ] Hand history tracking
- [ ] Win rate statistics

---

**Made with ❤️ for poker enthusiasts**