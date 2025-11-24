"""
Utility Functions Module
Helper functions for logging, validation, file I/O, and formatting
"""

import logging
import sys
from pathlib import Path
from typing import Optional, Dict, Any, Tuple, List
from datetime import datetime
import json
import csv

# Configure logging
def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None):
    """
    Setup logging configuration
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional log file path
    """
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    handlers = [logging.StreamHandler(sys.stdout)]
    if log_file:
        # Ensure log directory exists
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured at {log_level} level")


def validate_text(text: str, max_length: int = 10000) -> Tuple[bool, Optional[str]]:
    """
    Validate input text
    
    Args:
        text: Text to validate
        max_length: Maximum allowed length
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not text:
        return False, "Text cannot be empty"
    
    if not isinstance(text, str):
        return False, "Text must be a string"
    
    if len(text) > max_length:
        return False, f"Text exceeds maximum length of {max_length} characters"
    
    # Check for only whitespace
    if not text.strip():
        return False, "Text cannot be only whitespace"
    
    return True, None


def sanitize_text(text: str) -> str:
    """
    Sanitize text input
    
    Args:
        text: Text to sanitize
        
    Returns:
        Sanitized text
    """
    # Remove excessive whitespace
    text = ' '.join(text.split())
    
    # Remove control characters except newlines and tabs
    text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\t')
    
    return text.strip()


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human-readable string
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f} minutes"
    else:
        hours = seconds / 3600
        return f"{hours:.1f} hours"


def ensure_directory(path: str):
    """
    Ensure directory exists, create if it doesn't
    
    Args:
        path: Directory path
    """
    Path(path).mkdir(parents=True, exist_ok=True)


def export_to_csv(data: List[Dict[str, Any]], filepath: str):
    """
    Export data to CSV file
    
    Args:
        data: List of dictionaries to export
        filepath: Output file path
    """
    if not data:
        return
    
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    fieldnames = data[0].keys()
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    
    logging.getLogger(__name__).info(f"Data exported to CSV: {filepath}")


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from JSON or YAML file
    
    Args:
        config_path: Path to config file
        
    Returns:
        Configuration dictionary
    """
    config_path = Path(config_path)
    
    if not config_path.exists():
        logging.getLogger(__name__).warning(f"Config file not found: {config_path}")
        return {}
    
    if config_path.suffix == '.json':
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    elif config_path.suffix in ['.yaml', '.yml']:
        try:
            import yaml
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except ImportError:
            logging.getLogger(__name__).error("PyYAML not installed. Install with: pip install pyyaml")
            return {}
    else:
        logging.getLogger(__name__).warning(f"Unsupported config file format: {config_path.suffix}")
        return {}


def get_timestamp_string() -> str:
    """Get formatted timestamp string"""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

