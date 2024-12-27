import logging
import os
from datetime import datetime

def setup_logger():
    """Configure logging with PHI-safe practices"""
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Create a unique log file for each session
    log_filename = os.path.join('logs', f'phi_cleanse_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler()
        ]
    )
    
    # Create logger instance
    logger = logging.getLogger('phi_cleanse')
    
    # Add PHI warning
    logger.info('PHI CLEANSE TOOL - DO NOT LOG SENSITIVE INFORMATION')
    logger.info('Logging session started')
    
    return logger
