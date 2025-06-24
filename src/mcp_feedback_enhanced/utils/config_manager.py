#!/usr/bin/env python3
"""
Secure Configuration Management System
=====================================

Comprehensive configuration management for MCP Feedback Enhanced with Telegram integration.
Provides secure storage, validation, and management of configuration settings including
bot tokens, chat IDs, security settings, and feature toggles.

Key Features:
- Secure storage of sensitive data (bot tokens, chat IDs)
- Environment variable support for deployment
- Configuration validation and error handling
- Runtime configuration updates without restart
- Configuration backup and restore
- Template and example generation
- Encryption for sensitive data

Author: MCP Feedback Enhanced Team
"""

import os
import json
import base64
import hashlib
import secrets
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, asdict, field
from enum import Enum
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from ..debug import debug_log


class ConfigLevel(Enum):
    """Configuration security levels"""
    PUBLIC = "public"          # Can be logged and shared
    INTERNAL = "internal"      # Internal use only, not logged
    SENSITIVE = "sensitive"    # Encrypted storage required
    SECRET = "secret"          # Highest security, encrypted + access control


class ConfigSource(Enum):
    """Configuration sources in order of priority"""
    ENVIRONMENT = "environment"    # Environment variables (highest priority)
    CONFIG_FILE = "config_file"   # Configuration file
    DEFAULTS = "defaults"         # Default values (lowest priority)


@dataclass
class ConfigField:
    """Configuration field definition with metadata"""
    name: str
    value: Any
    level: ConfigLevel
    source: ConfigSource
    description: str
    required: bool = False
    validation_pattern: Optional[str] = None
    default_value: Any = None
    env_var: Optional[str] = None
    
    def is_sensitive(self) -> bool:
        """Check if field contains sensitive data"""
        return self.level in [ConfigLevel.SENSITIVE, ConfigLevel.SECRET]
    
    def should_encrypt(self) -> bool:
        """Check if field should be encrypted"""
        return self.level == ConfigLevel.SECRET
    
    def can_log(self) -> bool:
        """Check if field can be included in logs"""
        return self.level == ConfigLevel.PUBLIC


@dataclass
class TelegramConfig:
    """Telegram integration configuration"""
    enabled: bool = False
    bot_token: Optional[str] = None
    chat_id: Optional[str] = None
    enable_bridge: bool = False
    enable_auto_forwarding: bool = True
    enable_chunking: bool = True
    
    # Message formatting settings
    include_session_id: bool = True
    include_timestamp: bool = True
    include_project_path: bool = False
    include_details: bool = True
    
    # Chunking settings
    max_chunk_size: int = 3800
    preserve_code_blocks: bool = True
    preserve_markdown: bool = True
    add_navigation: bool = True
    add_previews: bool = True
    
    # Bridge settings
    session_timeout_minutes: int = 30
    max_concurrent_sessions: int = 5
    polling_interval_seconds: int = 1
    
    # Security settings
    allowed_users: List[str] = field(default_factory=list)
    rate_limit_messages_per_minute: int = 30
    enable_command_filtering: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TelegramConfig':
        """Create from dictionary"""
        return cls(**data)


@dataclass
class LoggingConfig:
    """Logging configuration"""
    enabled: bool = True
    level: str = "info"
    enable_telegram_forwarding: bool = False
    max_log_entries: int = 1000
    include_request_data: bool = True
    include_response_data: bool = True
    log_file_path: Optional[str] = None
    rotate_logs: bool = True
    max_log_files: int = 5
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LoggingConfig':
        """Create from dictionary"""
        return cls(**data)


@dataclass
class SecurityConfig:
    """Security configuration"""
    enable_encryption: bool = True
    encryption_key_file: str = ".mcp_key"
    enable_access_control: bool = False
    allowed_ips: List[str] = field(default_factory=list)
    session_timeout_minutes: int = 60
    max_failed_attempts: int = 5
    lockout_duration_minutes: int = 15
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SecurityConfig':
        """Create from dictionary"""
        return cls(**data)


@dataclass
class MCPConfig:
    """Complete MCP Feedback Enhanced configuration"""
    version: str = "1.0.0"
    debug_enabled: bool = False
    desktop_mode: bool = False
    
    # Component configurations
    telegram: TelegramConfig = field(default_factory=TelegramConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    
    # Web UI settings
    web_ui_enabled: bool = True
    web_ui_port: int = 8080
    web_ui_host: str = "localhost"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "version": self.version,
            "debug_enabled": self.debug_enabled,
            "desktop_mode": self.desktop_mode,
            "telegram": self.telegram.to_dict(),
            "logging": self.logging.to_dict(),
            "security": self.security.to_dict(),
            "web_ui_enabled": self.web_ui_enabled,
            "web_ui_port": self.web_ui_port,
            "web_ui_host": self.web_ui_host
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MCPConfig':
        """Create from dictionary"""
        telegram_data = data.get("telegram", {})
        logging_data = data.get("logging", {})
        security_data = data.get("security", {})
        
        return cls(
            version=data.get("version", "1.0.0"),
            debug_enabled=data.get("debug_enabled", False),
            desktop_mode=data.get("desktop_mode", False),
            telegram=TelegramConfig.from_dict(telegram_data),
            logging=LoggingConfig.from_dict(logging_data),
            security=SecurityConfig.from_dict(security_data),
            web_ui_enabled=data.get("web_ui_enabled", True),
            web_ui_port=data.get("web_ui_port", 8080),
            web_ui_host=data.get("web_ui_host", "localhost")
        )


class ConfigEncryption:
    """Handles encryption/decryption of sensitive configuration data"""
    
    def __init__(self, key_file: str = ".mcp_key"):
        self.key_file = Path(key_file)
        self._fernet = None
    
    def _get_or_create_key(self) -> bytes:
        """Get existing key or create new one"""
        if self.key_file.exists():
            try:
                with open(self.key_file, 'rb') as f:
                    return f.read()
            except Exception as e:
                debug_log(f"Failed to read encryption key: {e}", "CONFIG")
        
        # Generate new key
        key = Fernet.generate_key()
        try:
            # Ensure directory exists
            self.key_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Write key with restricted permissions
            with open(self.key_file, 'wb') as f:
                f.write(key)
            
            # Set file permissions (Unix-like systems)
            if hasattr(os, 'chmod'):
                os.chmod(self.key_file, 0o600)
            
            debug_log("Generated new encryption key", "CONFIG")
            return key
            
        except Exception as e:
            debug_log(f"Failed to create encryption key: {e}", "CONFIG")
            raise
    
    def _get_fernet(self) -> Fernet:
        """Get Fernet instance for encryption/decryption"""
        if self._fernet is None:
            key = self._get_or_create_key()
            self._fernet = Fernet(key)
        return self._fernet
    
    def encrypt(self, data: str) -> str:
        """Encrypt string data"""
        try:
            fernet = self._get_fernet()
            encrypted = fernet.encrypt(data.encode('utf-8'))
            return base64.b64encode(encrypted).decode('utf-8')
        except Exception as e:
            debug_log(f"Encryption failed: {e}", "CONFIG")
            raise
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt string data"""
        try:
            fernet = self._get_fernet()
            encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
            decrypted = fernet.decrypt(encrypted_bytes)
            return decrypted.decode('utf-8')
        except Exception as e:
            debug_log(f"Decryption failed: {e}", "CONFIG")
            raise


class ConfigManager:
    """
    Comprehensive configuration manager for MCP Feedback Enhanced.
    
    Provides secure storage, validation, and management of all configuration
    settings including Telegram integration, logging, and security settings.
    """
    
    DEFAULT_CONFIG_FILE = "mcp_config.json"
    BACKUP_SUFFIX = ".backup"
    
    # Environment variable mappings
    ENV_MAPPINGS = {
        "TELEGRAM_BOT_TOKEN": ("telegram", "bot_token"),
        "TELEGRAM_CHAT_ID": ("telegram", "chat_id"),
        "TELEGRAM_ENABLE_BRIDGE": ("telegram", "enable_bridge"),
        "TELEGRAM_ENABLED": ("telegram", "enabled"),
        "MCP_DEBUG": ("debug_enabled",),
        "MCP_DESKTOP_MODE": ("desktop_mode",),
        "MCP_WEB_UI_PORT": ("web_ui_port",),
        "MCP_WEB_UI_HOST": ("web_ui_host",),
        "MCP_LOG_LEVEL": ("logging", "level"),
        "MCP_ENCRYPTION_ENABLED": ("security", "enable_encryption"),
    }
    
    def __init__(self, 
                 config_file: Optional[str] = None,
                 enable_encryption: bool = True,
                 auto_save: bool = True):
        """
        Initialize configuration manager.
        
        Args:
            config_file: Path to configuration file
            enable_encryption: Whether to enable encryption for sensitive data
            auto_save: Whether to automatically save changes
        """
        self.config_file = Path(config_file or self.DEFAULT_CONFIG_FILE)
        self.enable_encryption = enable_encryption
        self.auto_save = auto_save
        
        # Initialize encryption if enabled
        self.encryption = ConfigEncryption() if enable_encryption else None
        
        # Load configuration
        self.config = self._load_config()
        
        debug_log(f"ConfigManager initialized with file: {self.config_file}", "CONFIG")
    
    def _load_config(self) -> MCPConfig:
        """Load configuration from file and environment variables"""
        # Start with defaults
        config = MCPConfig()
        
        # Load from file if exists
        if self.config_file.exists():
            try:
                config = self._load_from_file()
                debug_log("Configuration loaded from file", "CONFIG")
            except Exception as e:
                debug_log(f"Failed to load config file: {e}", "CONFIG")
        
        # Override with environment variables
        config = self._apply_environment_variables(config)
        
        # Validate configuration
        self._validate_config(config)
        
        return config
    
    def _load_from_file(self) -> MCPConfig:
        """Load configuration from JSON file"""
        with open(self.config_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Decrypt sensitive fields if encryption is enabled
        if self.enable_encryption and self.encryption:
            data = self._decrypt_sensitive_fields(data)
        
        return MCPConfig.from_dict(data)
    
    def _apply_environment_variables(self, config: MCPConfig) -> MCPConfig:
        """Apply environment variable overrides"""
        config_dict = config.to_dict()
        
        for env_var, config_path in self.ENV_MAPPINGS.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                # Convert string values to appropriate types
                converted_value = self._convert_env_value(env_value)
                
                # Apply to config dict
                self._set_nested_value(config_dict, config_path, converted_value)
                
                debug_log(f"Applied environment variable: {env_var}", "CONFIG")
        
        return MCPConfig.from_dict(config_dict)
    
    def _convert_env_value(self, value: str) -> Union[str, bool, int]:
        """Convert environment variable string to appropriate type"""
        # Boolean conversion
        if value.lower() in ('true', '1', 'yes', 'on'):
            return True
        elif value.lower() in ('false', '0', 'no', 'off'):
            return False
        
        # Integer conversion
        try:
            return int(value)
        except ValueError:
            pass
        
        # Return as string
        return value
    
    def _set_nested_value(self, config_dict: Dict[str, Any], path: tuple, value: Any):
        """Set nested dictionary value using path tuple"""
        current = config_dict
        for key in path[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[path[-1]] = value
    
    def _validate_config(self, config: MCPConfig):
        """Validate configuration settings"""
        errors = []
        
        # Validate Telegram configuration
        if config.telegram.enabled:
            if not config.telegram.bot_token:
                errors.append("Telegram bot token is required when Telegram is enabled")
            
            if not config.telegram.chat_id:
                errors.append("Telegram chat ID is required when Telegram is enabled")
            
            if config.telegram.max_chunk_size < 100:
                errors.append("Telegram max chunk size must be at least 100 characters")
            
            if config.telegram.session_timeout_minutes < 1:
                errors.append("Telegram session timeout must be at least 1 minute")
        
        # Validate logging configuration
        if config.logging.level not in ['debug', 'info', 'warning', 'error', 'critical']:
            errors.append("Invalid logging level")
        
        # Validate web UI configuration
        if config.web_ui_port < 1 or config.web_ui_port > 65535:
            errors.append("Web UI port must be between 1 and 65535")
        
        if errors:
            error_msg = "Configuration validation failed:\n" + "\n".join(f"- {error}" for error in errors)
            debug_log(error_msg, "CONFIG")
            raise ValueError(error_msg)
    
    def _encrypt_sensitive_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt sensitive fields in configuration data"""
        if not self.enable_encryption or not self.encryption:
            return data
        
        encrypted_data = data.copy()
        
        # Encrypt Telegram bot token
        if 'telegram' in encrypted_data and 'bot_token' in encrypted_data['telegram']:
            if encrypted_data['telegram']['bot_token']:
                encrypted_data['telegram']['bot_token'] = self.encryption.encrypt(
                    encrypted_data['telegram']['bot_token']
                )
        
        return encrypted_data
    
    def _decrypt_sensitive_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Decrypt sensitive fields in configuration data"""
        if not self.enable_encryption or not self.encryption:
            return data
        
        decrypted_data = data.copy()
        
        # Decrypt Telegram bot token
        if 'telegram' in decrypted_data and 'bot_token' in decrypted_data['telegram']:
            if decrypted_data['telegram']['bot_token']:
                try:
                    decrypted_data['telegram']['bot_token'] = self.encryption.decrypt(
                        decrypted_data['telegram']['bot_token']
                    )
                except Exception:
                    # If decryption fails, assume it's already decrypted
                    pass
        
        return decrypted_data
    
    def save_config(self, backup: bool = True) -> bool:
        """
        Save configuration to file.
        
        Args:
            backup: Whether to create backup before saving
            
        Returns:
            True if saved successfully
        """
        try:
            # Create backup if requested
            if backup and self.config_file.exists():
                backup_file = self.config_file.with_suffix(self.config_file.suffix + self.BACKUP_SUFFIX)
                backup_file.write_bytes(self.config_file.read_bytes())
                debug_log(f"Created config backup: {backup_file}", "CONFIG")
            
            # Prepare data for saving
            config_dict = self.config.to_dict()
            
            # Encrypt sensitive fields
            if self.enable_encryption:
                config_dict = self._encrypt_sensitive_fields(config_dict)
            
            # Ensure directory exists
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Write configuration
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=2, ensure_ascii=False)
            
            debug_log(f"Configuration saved to: {self.config_file}", "CONFIG")
            return True
            
        except Exception as e:
            debug_log(f"Failed to save configuration: {e}", "CONFIG")
            return False
    
    def reload_config(self) -> bool:
        """
        Reload configuration from file and environment variables.
        
        Returns:
            True if reloaded successfully
        """
        try:
            self.config = self._load_config()
            debug_log("Configuration reloaded", "CONFIG")
            return True
        except Exception as e:
            debug_log(f"Failed to reload configuration: {e}", "CONFIG")
            return False
    
    def update_telegram_config(self, **kwargs) -> bool:
        """
        Update Telegram configuration settings.

        Args:
            **kwargs: Telegram configuration fields to update

        Returns:
            True if updated successfully
        """
        try:
            # Update fields
            for key, value in kwargs.items():
                if hasattr(self.config.telegram, key):
                    setattr(self.config.telegram, key, value)
                    debug_log(f"Updated telegram.{key}", "CONFIG")

            # Validate updated configuration
            self._validate_config(self.config)

            # Auto-save if enabled
            if self.auto_save:
                return self.save_config()

            return True

        except ValueError as e:
            # Re-raise validation errors
            debug_log(f"Telegram config validation failed: {e}", "CONFIG")
            raise
        except Exception as e:
            debug_log(f"Failed to update Telegram config: {e}", "CONFIG")
            return False
    
    def get_telegram_config(self) -> TelegramConfig:
        """Get current Telegram configuration"""
        return self.config.telegram
    
    def get_logging_config(self) -> LoggingConfig:
        """Get current logging configuration"""
        return self.config.logging
    
    def get_security_config(self) -> SecurityConfig:
        """Get current security configuration"""
        return self.config.security
    
    def is_telegram_enabled(self) -> bool:
        """Check if Telegram integration is enabled and properly configured"""
        return (self.config.telegram.enabled and 
                bool(self.config.telegram.bot_token) and 
                bool(self.config.telegram.chat_id))
    
    def get_safe_config_summary(self) -> Dict[str, Any]:
        """Get configuration summary with sensitive data masked"""
        config_dict = self.config.to_dict()
        
        # Mask sensitive fields
        if 'telegram' in config_dict and 'bot_token' in config_dict['telegram']:
            if config_dict['telegram']['bot_token']:
                config_dict['telegram']['bot_token'] = "***MASKED***"
        
        return config_dict
    
    def export_config_template(self, include_examples: bool = True) -> Dict[str, Any]:
        """
        Export configuration template with examples and documentation.
        
        Args:
            include_examples: Whether to include example values
            
        Returns:
            Configuration template dictionary
        """
        template = {
            "_comment": "MCP Feedback Enhanced Configuration Template",
            "_version": "1.0.0",
            "_documentation": "https://github.com/your-repo/mcp-feedback-enhanced/docs/configuration.md",
            
            "version": "1.0.0",
            "debug_enabled": False,
            "desktop_mode": False,
            
            "telegram": {
                "_comment": "Telegram Bot Integration Settings",
                "enabled": False,
                "bot_token": "YOUR_BOT_TOKEN_HERE" if include_examples else None,
                "chat_id": "YOUR_CHAT_ID_HERE" if include_examples else None,
                "enable_bridge": True,
                "enable_auto_forwarding": True,
                "enable_chunking": True,
                
                "_message_formatting": "Message formatting options",
                "include_session_id": True,
                "include_timestamp": True,
                "include_project_path": False,
                "include_details": True,
                
                "_chunking_settings": "Message chunking configuration",
                "max_chunk_size": 3800,
                "preserve_code_blocks": True,
                "preserve_markdown": True,
                "add_navigation": True,
                "add_previews": True,
                
                "_bridge_settings": "Bridge behavior settings",
                "session_timeout_minutes": 30,
                "max_concurrent_sessions": 5,
                "polling_interval_seconds": 1,
                
                "_security_settings": "Security and access control",
                "allowed_users": [],
                "rate_limit_messages_per_minute": 30,
                "enable_command_filtering": True
            },
            
            "logging": {
                "_comment": "Logging configuration",
                "enabled": True,
                "level": "info",
                "enable_telegram_forwarding": False,
                "max_log_entries": 1000,
                "include_request_data": True,
                "include_response_data": True,
                "log_file_path": None,
                "rotate_logs": True,
                "max_log_files": 5
            },
            
            "security": {
                "_comment": "Security settings",
                "enable_encryption": True,
                "encryption_key_file": ".mcp_key",
                "enable_access_control": False,
                "allowed_ips": [],
                "session_timeout_minutes": 60,
                "max_failed_attempts": 5,
                "lockout_duration_minutes": 15
            },
            
            "web_ui_enabled": True,
            "web_ui_port": 8080,
            "web_ui_host": "localhost"
        }
        
        return template


# Global configuration manager instance
_global_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> Optional[ConfigManager]:
    """Get the global configuration manager instance"""
    return _global_config_manager


def initialize_config_manager(config_file: Optional[str] = None,
                             enable_encryption: bool = True,
                             auto_save: bool = True) -> ConfigManager:
    """Initialize the global configuration manager"""
    global _global_config_manager
    
    _global_config_manager = ConfigManager(
        config_file=config_file,
        enable_encryption=enable_encryption,
        auto_save=auto_save
    )
    
    debug_log("Global configuration manager initialized", "CONFIG")
    return _global_config_manager


# Convenience functions
def get_telegram_config() -> Optional[TelegramConfig]:
    """Get Telegram configuration"""
    manager = get_config_manager()
    return manager.get_telegram_config() if manager else None


def is_telegram_enabled() -> bool:
    """Check if Telegram integration is enabled"""
    manager = get_config_manager()
    return manager.is_telegram_enabled() if manager else False


def update_telegram_settings(**kwargs) -> bool:
    """Update Telegram settings"""
    manager = get_config_manager()
    return manager.update_telegram_config(**kwargs) if manager else False


def get_safe_config() -> Dict[str, Any]:
    """Get safe configuration summary (sensitive data masked)"""
    manager = get_config_manager()
    return manager.get_safe_config_summary() if manager else {}