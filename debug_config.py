"""
Debug script to examine the configuration object
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.config import get_config

def debug_config():
    """Debug the configuration object"""
    config = get_config()
    print(f"Config type: {type(config)}")
    print(f"Config attributes: {dir(config)}")
    print(f"Environment: {getattr(config, 'environment', 'NOT FOUND')}")
    print(f"Log level: {getattr(config, 'log_level', 'NOT FOUND')}")
    print(f"Max workers: {getattr(config, 'max_workers', 'NOT FOUND')}")
    print(f"Timeout seconds: {getattr(config, 'timeout_seconds', 'NOT FOUND')}")
    
    # Check all attributes
    for attr in ['environment', 'debug', 'log_level', 'enable_monitoring', 'max_workers', 'timeout_seconds', 'enable_validation', 'validation_timeout']:
        value = getattr(config, attr, 'NOT FOUND')
        print(f"{attr}: {value} (type: {type(value)})")

if __name__ == "__main__":
    debug_config()