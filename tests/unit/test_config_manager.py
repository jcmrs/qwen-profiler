"""
Unit tests for the ConfigManager component
"""
import pytest
import os
from unittest.mock import patch, mock_open
from src.core.config import ConfigManager, AppConfig


class TestConfigManager:
    """Test suite for ConfigManager functionality"""
    
    def setup_method(self):
        """Setup method that runs before each test"""
        # Ensure we have a predictable environment
        if 'ENVIRONMENT' in os.environ:
            del os.environ['ENVIRONMENT']
        if 'LOG_LEVEL' in os.environ:
            del os.environ['LOG_LEVEL']
        if 'DEBUG' in os.environ:
            del os.environ['DEBUG']
    
    def test_config_manager_initialization(self):
        """Test basic initialization of ConfigManager"""
        config_manager = ConfigManager()
        config = config_manager.get_config()
        
        # Verify basic configuration properties
        assert config is not None
        assert hasattr(config, 'environment')
        assert hasattr(config, 'debug')
        assert hasattr(config, 'log_level')
        assert config.environment in ['development', 'staging', 'production']
    
    def test_config_with_nonexistent_file(self):
        """Test ConfigManager creates default config when file doesn't exist"""
        config_manager = ConfigManager(config_path="nonexistent_config.yaml")
        config = config_manager.get_config()
        
        # Should have been created with defaults
        assert config is not None
        assert config.environment == "development"  # Default value
        assert config.debug is False  # Default value
    
    def test_config_validation_valid_values(self):
        """Test configuration validation with valid values"""
        config_data = {
            'environment': 'test',
            'debug': True,
            'log_level': 'INFO',
            'max_workers': 8,
            'timeout_seconds': 60
        }
        
        # Create config with valid values
        config = AppConfig(**config_data)
        
        # Verify values
        assert config.environment == 'test'
        assert config.debug is True
        assert config.log_level == 'INFO'
        assert config.max_workers == 8
        assert config.timeout_seconds == 60
    
    def test_config_validation_invalid_log_level(self):
        """Test configuration validation with invalid log level"""
        config_data = {
            'log_level': 'INVALID_LEVEL'  # This should be rejected
        }
        
        # Should raise an error with invalid log level
        with pytest.raises(ValueError):
            AppConfig(**config_data)
    
    def test_config_with_env_override(self):
        """Test configuration loading with environment variable overrides"""
        # Set environment variables
        os.environ['LOG_LEVEL'] = 'DEBUG'
        os.environ['DEBUG'] = 'true'
        os.environ['MAX_WORKERS'] = '10'
        
        # Create config manager which should pick up env vars
        config_manager = ConfigManager(config_path="nonexistent_config.yaml")
        config = config_manager.get_config()
        
        # Verify environment variable values were used
        assert config.log_level == 'DEBUG'
        assert config.debug is True
        assert config.max_workers == 10
    
    def test_config_with_env_override_boolean_false(self):
        """Test configuration loading with boolean environment variable set to false"""
        # Set environment variables with false values
        os.environ['DEBUG'] = 'false'
        os.environ['ENABLE_MONITORING'] = 'False'
        os.environ['ENABLE_VALIDATION'] = '0'
        
        # Create config manager
        config_manager = ConfigManager(config_path="nonexistent_config.yaml")
        config = config_manager.get_config()
        
        # Verify boolean environment variables were parsed correctly
        assert config.debug is False
        assert config.enable_monitoring is False
        assert config.enable_validation is False
    
    def test_config_with_env_override_integer(self):
        """Test configuration loading with integer environment variable"""
        # Set environment variable with integer value
        os.environ['MAX_WORKERS'] = '15'
        os.environ['TIMEOUT_SECONDS'] = '45'
        
        # Create config manager
        config_manager = ConfigManager(config_path="nonexistent_config.yaml")
        config = config_manager.get_config()
        
        # Verify integer environment variables were parsed correctly
        assert config.max_workers == 15
        assert config.timeout_seconds == 45
    
    def test_config_reload(self):
        """Test reloading configuration"""
        config_manager = ConfigManager(config_path="nonexistent_config.yaml")
        initial_config = config_manager.get_config()
        
        # Modify something in the config object (simulated)
        # Then call reload
        config_manager.reload_config()
        reloaded_config = config_manager.get_config()
        
        # Both should be valid configs (the specific values may be the same since we're using default)
        assert initial_config is not None
        assert reloaded_config is not None
        assert hasattr(reloaded_config, 'environment')
    
    def test_create_default_config_file(self):
        """Test that default config file is created when it doesn't exist"""
        # This test implicitly runs when we create a ConfigManager with a new file path
        test_config_path = "test_config.yaml"
        
        try:
            # Remove the file if it already exists
            import os
            if os.path.exists(test_config_path):
                os.remove(test_config_path)
            
            # Create config manager with new path
            config_manager = ConfigManager(config_path=test_config_path)
            
            # Verify the file was created
            assert os.path.exists(test_config_path)
            
        finally:
            # Clean up test file
            if os.path.exists(test_config_path):
                os.remove(test_config_path)