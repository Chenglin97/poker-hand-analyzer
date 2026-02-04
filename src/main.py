"""Main entry point for Poker Hand Analyzer."""

import sys
import argparse
import logging

from poker_analyzer.analyzer import PokerHandAnalyzer
from poker_analyzer.config import config
from poker_analyzer.utils import setup_logging

logger = logging.getLogger(__name__)


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Poker Hand Analyzer - Analyze poker hands from screen capture'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        help='Path to custom config file'
    )
    
    parser.add_argument(
        '--log-level',
        type=str,
        default=config.log_level,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Logging level'
    )
    
    parser.add_argument(
        '--once',
        action='store_true',
        help='Run analysis once and exit (instead of continuous loop)'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(
        log_level=args.log_level,
        log_file=config.log_file
    )
    
    logger.info("=" * 70)
    logger.info("Poker Hand Analyzer Starting")
    logger.info("=" * 70)
    
    try:
        # Initialize analyzer
        analyzer = PokerHandAnalyzer()
        
        if args.once:
            # Single analysis
            result = analyzer.analyze_once()
            if result:
                analyzer._print_result(result)
                sys.exit(0)
            else:
                print("❌ Analysis failed")
                sys.exit(1)
        else:
            # Continuous analysis
            analyzer.run_continuous()
            
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()