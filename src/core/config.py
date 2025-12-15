"""
Configuration management module for Qwen Profiler
Handles loading, validating, and managing application configuration
"""
import os
from typing import Dict, Any, Optional
from pathlib import Path
import yaml
from pydantic import BaseModel, ValidationError, field_validator


class AppConfig(BaseModel):
    """Application configuration model"""
    environment: str = "development"
    debug: bool = False
    log_level: str = "INFO"
    enable_monitoring: bool = True
    
    # Database configuration
    database_url: Optional[str] = None
    
    # Core system settings
    max_workers: int = 4
    timeout_seconds: int = 30
    
    # Validation settings
    enable_validation: bool = True
    validation_timeout: int = 60
    
    @field_validator('log_level')
    @classmethod
    def validate_log_level(cls, v):
        valid_levels = {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}
        if v.upper() not in valid_levels:
            raise ValueError(f'log_level must be one of {valid_levels}')
        return v.upper()


class ConfigManager:
    """Configuration manager to handle loading and validation of configurations"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._get_default_config_path()
        self.config: Optional[AppConfig] = None
        self._load_config()
    
    def _get_default_config_path(self) -> str:
        """Get the default configuration file path based on environment"""
        env = os.getenv("ENVIRONMENT", "development")
        return f"configs/{env}.yaml"
    
    def _load_config(self):
        """Load configuration from YAML file"""
        if not os.path.exists(self.config_path):
            # If config file doesn't exist, create with default values
            self._create_default_config()
        
        with open(self.config_path, 'r', encoding='utf-8') as file:
            config_data = yaml.safe_load(file) or {}
        
        # Override with environment variables if they exist
        config_data = self._apply_env_overrides(config_data)
        
        try:
            self.config = AppConfig(**config_data)
        except ValidationError as e:
            raise ValueError(f"Configuration validation error: {e}")
    
    def _apply_env_overrides(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply environment variable overrides to config data"""
        # Environment variable mappings
        env_mappings = {
            'ENVIRONMENT': 'environment',
            'DEBUG': 'debug',
            'LOG_LEVEL': 'log_level',
            'ENABLE_MONITORING': 'enable_monitoring',
            'DATABASE_URL': 'database_url',
            'MAX_WORKERS': 'max_workers',
            'TIMEOUT_SECONDS': 'timeout_seconds',
            'ENABLE_VALIDATION': 'enable_validation',
            'VALIDATION_TIMEOUT': 'validation_timeout'
        }
        
        for env_var, config_key in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                # Convert string values to appropriate types
                if config_key in ['debug', 'enable_monitoring', 'enable_validation']:
                    config_data[config_key] = env_value.lower() in ('true', '1', 'yes', 'on')
                elif config_key in ['max_workers', 'timeout_seconds', 'validation_timeout']:
                    try:
                        config_data[config_key] = int(env_value)
                    except ValueError:
                        raise ValueError(f"Invalid integer value for {env_var}: {env_value}")
                else:
                    config_data[config_key] = env_value
        
        return config_data
    
    def _create_default_config(self):
        """Create a default configuration file if it doesn't exist"""
        default_config = {
            'environment': os.getenv("ENVIRONMENT", "development"),
            'debug': os.getenv("DEBUG", "false").lower() in ('true', '1', 'yes', 'on'),
            'log_level': os.getenv("LOG_LEVEL", "INFO"),
            'enable_monitoring': True,
            'max_workers': 4,
            'timeout_seconds': 30,
            'enable_validation': True,
            'validation_timeout': 60
        }
        
        # Ensure the directory exists
        Path(self.config_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Write the default configuration
        with open(self.config_path, 'w', encoding='utf-8') as file:
            yaml.dump(default_config, file, default_flow_style=False)
    
    def get_config(self) -> AppConfig:
        """Get the loaded configuration"""
        if self.config is None:
            raise RuntimeError("Configuration not loaded")
        return self.config
    
    def reload_config(self):
        """Reload configuration from file"""
        self._load_config()


# Global configuration manager instance
config_manager = ConfigManager()


def get_config() -> AppConfig:
    """Get the global configuration instance"""
    return config_manager.get_config()