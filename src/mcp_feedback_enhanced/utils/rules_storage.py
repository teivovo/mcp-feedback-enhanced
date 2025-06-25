#!/usr/bin/env python3
"""
Message Type Rules Storage
=========================

Handles persistent storage and retrieval of message type rules.
Supports JSON-based storage with atomic operations and backup management.
"""

import json
import os
import shutil
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..debug import debug_log
from .error_handler import ErrorHandler, ErrorType


class RulesStorageError(Exception):
    """Rules storage specific errors"""
    pass


class RulesStorage:
    """
    Persistent storage manager for message type rules
    
    Features:
    - JSON-based storage with atomic writes
    - Automatic backup management
    - Thread-safe operations
    - Rule validation and migration
    """
    
    def __init__(self, storage_dir: Optional[str] = None):
        """
        Initialize rules storage
        
        Args:
            storage_dir: Custom storage directory path
        """
        self.storage_dir = Path(storage_dir) if storage_dir else self._get_default_storage_dir()
        self.rules_file = self.storage_dir / "message_type_rules.json"
        self.backup_dir = self.storage_dir / "backups"
        self.lock = threading.RLock()
        
        # Ensure directories exist
        self._ensure_directories()
        
        # Initialize with default rules if file doesn't exist
        if not self.rules_file.exists():
            self._create_default_rules()
            
        debug_log(f"📁 Rules storage initialized: {self.storage_dir}")
    
    def _get_default_storage_dir(self) -> Path:
        """Get default storage directory"""
        # Use user's config directory or fallback to current directory
        if os.name == 'nt':  # Windows
            config_dir = Path(os.environ.get('APPDATA', '.')) / 'mcp_feedback_enhanced'
        else:  # Unix-like
            config_dir = Path(os.environ.get('XDG_CONFIG_HOME', '~/.config')).expanduser() / 'mcp_feedback_enhanced'
        
        return config_dir / 'rules'
    
    def _ensure_directories(self):
        """Ensure storage directories exist"""
        try:
            self.storage_dir.mkdir(parents=True, exist_ok=True)
            self.backup_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise RulesStorageError(f"Failed to create storage directories: {e}")
    
    def _create_default_rules(self):
        """Create default rules configuration"""
        default_rules = {
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "rules": [
                {
                    "id": "error_report_auto_submit",
                    "name": "Error Report Auto Submit",
                    "description": "Automatically submit error reports after 5 minutes",
                    "message_type": "error_report",
                    "rule_type": "auto_submit_override",
                    "value": True,
                    "timeout_override": 300,
                    "project_filter": {
                        "type": "all"
                    },
                    "priority": 100,
                    "enabled": True,
                    "created_at": datetime.now().isoformat()
                },
                {
                    "id": "testing_auto_submit",
                    "name": "Testing Auto Submit",
                    "description": "Auto-submit testing results after 7.5 minutes",
                    "message_type": "testing",
                    "rule_type": "auto_submit_override",
                    "value": True,
                    "timeout_override": 450,
                    "project_filter": {
                        "type": "all"
                    },
                    "priority": 90,
                    "enabled": True,
                    "created_at": datetime.now().isoformat()
                },
                {
                    "id": "deployment_auto_submit",
                    "name": "Deployment Auto Submit",
                    "description": "Quick auto-submit for deployment confirmations",
                    "message_type": "deployment",
                    "rule_type": "auto_submit_override",
                    "value": True,
                    "timeout_override": 300,
                    "project_filter": {
                        "type": "all"
                    },
                    "priority": 95,
                    "enabled": True,
                    "created_at": datetime.now().isoformat()
                },
                {
                    "id": "code_review_header",
                    "name": "Code Review Header",
                    "description": "Add standard header for code review responses",
                    "message_type": "code_review",
                    "rule_type": "response_header",
                    "value": "## Code Review Feedback\n\nThank you for the code review. Here are my responses:\n\n",
                    "project_filter": {
                        "type": "all"
                    },
                    "priority": 50,
                    "enabled": True,
                    "created_at": datetime.now().isoformat()
                },
                {
                    "id": "security_footer",
                    "name": "Security Review Footer",
                    "description": "Add security disclaimer to security-related responses",
                    "message_type": "security",
                    "rule_type": "response_footer",
                    "value": "\n\n---\n**Security Note**: This feedback is for development purposes. Please conduct proper security audits before production deployment.",
                    "project_filter": {
                        "type": "all"
                    },
                    "priority": 50,
                    "enabled": True,
                    "created_at": datetime.now().isoformat()
                }
            ]
        }
        
        self._save_rules_data(default_rules)
        debug_log("📋 Created default rules configuration")
    
    def load_rules(self) -> Dict[str, Any]:
        """
        Load rules from storage
        
        Returns:
            Dict containing all rules data
        """
        with self.lock:
            try:
                if not self.rules_file.exists():
                    self._create_default_rules()
                
                with open(self.rules_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Validate and migrate if needed
                data = self._validate_and_migrate(data)
                
                debug_log(f"📖 Loaded {len(data.get('rules', []))} rules from storage")
                return data
                
            except Exception as e:
                error_id = ErrorHandler.log_error_with_context(
                    e, ErrorType.FILE_OPERATION,
                    context={"operation": "load_rules", "file": str(self.rules_file)}
                )
                raise RulesStorageError(f"Failed to load rules [Error ID: {error_id}]: {e}")
    
    def save_rules(self, rules_data: Dict[str, Any]) -> bool:
        """
        Save rules to storage with atomic operation
        
        Args:
            rules_data: Complete rules data structure
            
        Returns:
            True if successful
        """
        with self.lock:
            try:
                # Validate data structure
                self._validate_rules_data(rules_data)
                
                # Create backup before saving
                self._create_backup()
                
                # Update metadata
                rules_data["updated_at"] = datetime.now().isoformat()
                
                # Atomic save
                self._save_rules_data(rules_data)
                
                debug_log(f"💾 Saved {len(rules_data.get('rules', []))} rules to storage")
                return True
                
            except Exception as e:
                error_id = ErrorHandler.log_error_with_context(
                    e, ErrorType.FILE_OPERATION,
                    context={"operation": "save_rules", "file": str(self.rules_file)}
                )
                raise RulesStorageError(f"Failed to save rules [Error ID: {error_id}]: {e}")
    
    def _save_rules_data(self, data: Dict[str, Any]):
        """Atomic save operation"""
        temp_file = self.rules_file.with_suffix('.tmp')
        
        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Atomic move
            shutil.move(str(temp_file), str(self.rules_file))
            
        except Exception as e:
            # Clean up temp file if it exists
            if temp_file.exists():
                temp_file.unlink()
            raise e
    
    def _validate_rules_data(self, data: Dict[str, Any]):
        """Validate rules data structure"""
        if not isinstance(data, dict):
            raise ValueError("Rules data must be a dictionary")
        
        if "rules" not in data:
            raise ValueError("Rules data must contain 'rules' key")
        
        if not isinstance(data["rules"], list):
            raise ValueError("Rules must be a list")
        
        # Validate each rule
        for i, rule in enumerate(data["rules"]):
            self._validate_rule(rule, i)
    
    def _validate_rule(self, rule: Dict[str, Any], index: int):
        """Validate individual rule structure"""
        required_fields = ["id", "name", "message_type", "rule_type", "value"]
        
        for field in required_fields:
            if field not in rule:
                raise ValueError(f"Rule {index} missing required field: {field}")
        
        # Validate rule types
        valid_rule_types = ["auto_submit_override", "response_header", "response_footer", "timeout_override"]
        if rule["rule_type"] not in valid_rule_types:
            raise ValueError(f"Rule {index} has invalid rule_type: {rule['rule_type']}")
    
    def _validate_and_migrate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and migrate rules data if needed"""
        # Add version if missing
        if "version" not in data:
            data["version"] = "1.0"
        
        # Ensure rules list exists
        if "rules" not in data:
            data["rules"] = []
        
        # Migrate rules if needed (future versions)
        current_version = data.get("version", "1.0")
        if current_version != "1.0":
            debug_log(f"🔄 Migrating rules from version {current_version} to 1.0")
            # Add migration logic here for future versions
        
        return data
    
    def _create_backup(self):
        """Create backup of current rules file"""
        if not self.rules_file.exists():
            return
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f"rules_backup_{timestamp}.json"
            
            shutil.copy2(self.rules_file, backup_file)
            
            # Clean old backups (keep last 10)
            self._cleanup_old_backups()
            
            debug_log(f"📦 Created backup: {backup_file.name}")
            
        except Exception as e:
            debug_log(f"⚠️ Failed to create backup: {e}")
    
    def _cleanup_old_backups(self):
        """Remove old backup files, keeping the most recent 10"""
        try:
            backup_files = list(self.backup_dir.glob("rules_backup_*.json"))
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Remove files beyond the 10 most recent
            for old_backup in backup_files[10:]:
                old_backup.unlink()
                debug_log(f"🗑️ Removed old backup: {old_backup.name}")
                
        except Exception as e:
            debug_log(f"⚠️ Failed to cleanup old backups: {e}")
    
    def get_storage_info(self) -> Dict[str, Any]:
        """Get storage information and statistics"""
        try:
            rules_data = self.load_rules()
            backup_files = list(self.backup_dir.glob("rules_backup_*.json"))
            
            return {
                "storage_dir": str(self.storage_dir),
                "rules_file": str(self.rules_file),
                "rules_count": len(rules_data.get("rules", [])),
                "version": rules_data.get("version", "unknown"),
                "created_at": rules_data.get("created_at"),
                "updated_at": rules_data.get("updated_at"),
                "backup_count": len(backup_files),
                "file_size": self.rules_file.stat().st_size if self.rules_file.exists() else 0
            }
        except Exception as e:
            return {"error": str(e)}
