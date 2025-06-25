#!/usr/bin/env python3
"""
Message Type Rules Engine
=========================

Core rules engine for applying message-type-based rules and configurations.
Handles rule matching, priority resolution, and configuration application.
"""

import fnmatch
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..debug import debug_log
from .error_handler import ErrorHandler, ErrorType
from .rules_storage import RulesStorage, RulesStorageError


class RulesEngineError(Exception):
    """Rules engine specific errors"""
    pass


class MessageTypeRulesEngine:
    """
    Core rules engine for message type rules
    
    Features:
    - Rule matching based on message type and project
    - Priority-based rule resolution
    - Project filtering with patterns
    - Configuration merging and overrides
    """
    
    def __init__(self, storage_dir: Optional[str] = None):
        """
        Initialize rules engine
        
        Args:
            storage_dir: Custom storage directory for rules
        """
        self.storage = RulesStorage(storage_dir)
        self._rules_cache = None
        self._cache_timestamp = 0
        
        debug_log("🔧 Rules engine initialized")
    
    def apply_rules(self, message_type: str, project_directory: str, base_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply rules to base configuration
        
        Args:
            message_type: Type of message (e.g., 'error_report', 'code_review')
            project_directory: Project directory path
            base_config: Base configuration to modify
            
        Returns:
            Modified configuration with rules applied
        """
        try:
            debug_log(f"🎯 Applying rules for message_type='{message_type}', project='{project_directory}'")
            
            # Get applicable rules
            applicable_rules = self.find_applicable_rules(message_type, project_directory)
            
            if not applicable_rules:
                debug_log("📝 No applicable rules found")
                return base_config.copy()
            
            # Apply rules in priority order
            config = base_config.copy()
            applied_rules = []
            
            for rule in applicable_rules:
                try:
                    self._apply_single_rule(rule, config)
                    applied_rules.append(rule["id"])
                except Exception as e:
                    debug_log(f"⚠️ Failed to apply rule {rule.get('id', 'unknown')}: {e}")
            
            debug_log(f"✅ Applied {len(applied_rules)} rules: {applied_rules}")
            return config
            
        except Exception as e:
            error_id = ErrorHandler.log_error_with_context(
                e, ErrorType.BUSINESS_LOGIC,
                context={
                    "message_type": message_type,
                    "project_directory": project_directory,
                    "operation": "apply_rules"
                }
            )
            debug_log(f"❌ Rules application failed [Error ID: {error_id}]: {e}")
            return base_config.copy()
    
    def find_applicable_rules(self, message_type: str, project_directory: str) -> List[Dict[str, Any]]:
        """
        Find rules applicable to the given message type and project
        
        Args:
            message_type: Type of message
            project_directory: Project directory path
            
        Returns:
            List of applicable rules sorted by priority (highest first)
        """
        try:
            rules_data = self._get_rules()
            applicable_rules = []
            
            for rule in rules_data.get("rules", []):
                if self._is_rule_applicable(rule, message_type, project_directory):
                    applicable_rules.append(rule)
            
            # Sort by priority (highest first)
            applicable_rules.sort(key=lambda r: r.get("priority", 0), reverse=True)
            
            debug_log(f"🔍 Found {len(applicable_rules)} applicable rules")
            return applicable_rules
            
        except Exception as e:
            debug_log(f"❌ Failed to find applicable rules: {e}")
            return []
    
    def _is_rule_applicable(self, rule: Dict[str, Any], message_type: str, project_directory: str) -> bool:
        """Check if a rule is applicable to the given context"""
        # Check if rule is enabled
        if not rule.get("enabled", True):
            return False
        
        # Check message type match
        rule_message_type = rule.get("message_type")
        if rule_message_type and rule_message_type != message_type:
            return False
        
        # Check project filter
        project_filter = rule.get("project_filter", {})
        if not self._matches_project_filter(project_filter, project_directory):
            return False
        
        return True
    
    def _matches_project_filter(self, project_filter: Dict[str, Any], project_directory: str) -> bool:
        """Check if project directory matches the project filter"""
        filter_type = project_filter.get("type", "all")
        
        if filter_type == "all":
            return True
        
        elif filter_type == "specific":
            patterns = project_filter.get("patterns", [])
            return self._matches_any_pattern(project_directory, patterns)
        
        elif filter_type == "exclude":
            patterns = project_filter.get("patterns", [])
            return not self._matches_any_pattern(project_directory, patterns)
        
        elif filter_type == "regex":
            pattern = project_filter.get("pattern", "")
            try:
                return bool(re.search(pattern, project_directory))
            except re.error:
                debug_log(f"⚠️ Invalid regex pattern: {pattern}")
                return False
        
        return False
    
    def _matches_any_pattern(self, project_directory: str, patterns: List[str]) -> bool:
        """Check if project directory matches any of the given patterns"""
        project_path = Path(project_directory)
        project_name = project_path.name
        project_str = str(project_path)
        
        for pattern in patterns:
            # Try matching against full path, project name, and normalized path
            if (fnmatch.fnmatch(project_str, pattern) or
                fnmatch.fnmatch(project_name, pattern) or
                fnmatch.fnmatch(project_str.replace("\\", "/"), pattern)):
                return True
        
        return False
    
    def _apply_single_rule(self, rule: Dict[str, Any], config: Dict[str, Any]):
        """Apply a single rule to the configuration"""
        rule_type = rule.get("rule_type")
        rule_value = rule.get("value")
        
        if rule_type == "auto_submit_override":
            config["auto_submit"] = bool(rule_value)
            # Also apply timeout override if specified
            if "timeout_override" in rule:
                config["timeout"] = rule["timeout_override"]
        
        elif rule_type == "timeout_override":
            config["timeout"] = rule_value
        
        elif rule_type == "response_header":
            # Prepend to existing response or create new
            existing_response = config.get("response_text", "")
            config["response_text"] = str(rule_value) + existing_response
        
        elif rule_type == "response_footer":
            # Append to existing response or create new
            existing_response = config.get("response_text", "")
            config["response_text"] = existing_response + str(rule_value)
        
        elif rule_type == "template_override":
            config["template_id"] = rule_value
        
        elif rule_type == "custom_config":
            # Merge custom configuration
            if isinstance(rule_value, dict):
                config.update(rule_value)
        
        debug_log(f"📋 Applied rule '{rule.get('id')}' of type '{rule_type}'")
    
    def _get_rules(self) -> Dict[str, Any]:
        """Get rules with caching"""
        try:
            # Simple cache to avoid repeated file reads
            current_time = self.storage.rules_file.stat().st_mtime if self.storage.rules_file.exists() else 0
            
            if self._rules_cache is None or current_time > self._cache_timestamp:
                self._rules_cache = self.storage.load_rules()
                self._cache_timestamp = current_time
                debug_log("🔄 Rules cache refreshed")
            
            return self._rules_cache
            
        except Exception as e:
            debug_log(f"❌ Failed to get rules: {e}")
            return {"rules": []}
    
    def add_rule(self, rule: Dict[str, Any]) -> bool:
        """
        Add a new rule
        
        Args:
            rule: Rule configuration
            
        Returns:
            True if successful
        """
        try:
            rules_data = self.storage.load_rules()
            
            # Validate rule
            self._validate_rule(rule)
            
            # Check for duplicate IDs
            existing_ids = {r["id"] for r in rules_data["rules"]}
            if rule["id"] in existing_ids:
                raise ValueError(f"Rule ID '{rule['id']}' already exists")
            
            # Add timestamps
            from datetime import datetime
            rule["created_at"] = datetime.now().isoformat()
            
            # Add rule
            rules_data["rules"].append(rule)
            
            # Save
            success = self.storage.save_rules(rules_data)
            if success:
                self._invalidate_cache()
                debug_log(f"➕ Added rule: {rule['id']}")
            
            return success
            
        except Exception as e:
            debug_log(f"❌ Failed to add rule: {e}")
            return False
    
    def update_rule(self, rule_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update an existing rule
        
        Args:
            rule_id: ID of rule to update
            updates: Fields to update
            
        Returns:
            True if successful
        """
        try:
            rules_data = self.storage.load_rules()
            
            # Find rule
            rule_index = None
            for i, rule in enumerate(rules_data["rules"]):
                if rule["id"] == rule_id:
                    rule_index = i
                    break
            
            if rule_index is None:
                raise ValueError(f"Rule '{rule_id}' not found")
            
            # Update rule
            rule = rules_data["rules"][rule_index]
            rule.update(updates)
            
            # Add update timestamp
            from datetime import datetime
            rule["updated_at"] = datetime.now().isoformat()
            
            # Validate updated rule
            self._validate_rule(rule)
            
            # Save
            success = self.storage.save_rules(rules_data)
            if success:
                self._invalidate_cache()
                debug_log(f"✏️ Updated rule: {rule_id}")
            
            return success
            
        except Exception as e:
            debug_log(f"❌ Failed to update rule: {e}")
            return False
    
    def delete_rule(self, rule_id: str) -> bool:
        """
        Delete a rule
        
        Args:
            rule_id: ID of rule to delete
            
        Returns:
            True if successful
        """
        try:
            rules_data = self.storage.load_rules()
            
            # Find and remove rule
            original_count = len(rules_data["rules"])
            rules_data["rules"] = [r for r in rules_data["rules"] if r["id"] != rule_id]
            
            if len(rules_data["rules"]) == original_count:
                raise ValueError(f"Rule '{rule_id}' not found")
            
            # Save
            success = self.storage.save_rules(rules_data)
            if success:
                self._invalidate_cache()
                debug_log(f"🗑️ Deleted rule: {rule_id}")
            
            return success
            
        except Exception as e:
            debug_log(f"❌ Failed to delete rule: {e}")
            return False
    
    def _validate_rule(self, rule: Dict[str, Any]):
        """Validate rule structure and values"""
        required_fields = ["id", "name", "message_type", "rule_type", "value"]
        
        for field in required_fields:
            if field not in rule:
                raise ValueError(f"Rule missing required field: {field}")
        
        # Validate rule types
        valid_rule_types = [
            "auto_submit_override", "timeout_override", "response_header", 
            "response_footer", "template_override", "custom_config"
        ]
        if rule["rule_type"] not in valid_rule_types:
            raise ValueError(f"Invalid rule_type: {rule['rule_type']}")
        
        # Validate message types
        valid_message_types = [
            "general", "code_review", "error_report", "feature_request",
            "documentation", "testing", "deployment", "security"
        ]
        if rule["message_type"] not in valid_message_types:
            raise ValueError(f"Invalid message_type: {rule['message_type']}")
    
    def _invalidate_cache(self):
        """Invalidate rules cache"""
        self._rules_cache = None
        self._cache_timestamp = 0
    
    def get_rules_summary(self) -> Dict[str, Any]:
        """Get summary of all rules"""
        try:
            rules_data = self._get_rules()
            rules = rules_data.get("rules", [])
            
            summary = {
                "total_rules": len(rules),
                "enabled_rules": len([r for r in rules if r.get("enabled", True)]),
                "by_message_type": {},
                "by_rule_type": {},
                "storage_info": self.storage.get_storage_info()
            }
            
            # Count by message type
            for rule in rules:
                msg_type = rule.get("message_type", "unknown")
                summary["by_message_type"][msg_type] = summary["by_message_type"].get(msg_type, 0) + 1
            
            # Count by rule type
            for rule in rules:
                rule_type = rule.get("rule_type", "unknown")
                summary["by_rule_type"][rule_type] = summary["by_rule_type"].get(rule_type, 0) + 1
            
            return summary
            
        except Exception as e:
            return {"error": str(e)}
    
    def test_rule_matching(self, message_type: str, project_directory: str) -> Dict[str, Any]:
        """
        Test rule matching for debugging
        
        Args:
            message_type: Message type to test
            project_directory: Project directory to test
            
        Returns:
            Test results with matching details
        """
        try:
            rules_data = self._get_rules()
            results = {
                "message_type": message_type,
                "project_directory": project_directory,
                "total_rules": len(rules_data.get("rules", [])),
                "matching_rules": [],
                "non_matching_rules": []
            }
            
            for rule in rules_data.get("rules", []):
                rule_info = {
                    "id": rule.get("id"),
                    "name": rule.get("name"),
                    "enabled": rule.get("enabled", True),
                    "message_type": rule.get("message_type"),
                    "rule_type": rule.get("rule_type"),
                    "priority": rule.get("priority", 0)
                }
                
                if self._is_rule_applicable(rule, message_type, project_directory):
                    results["matching_rules"].append(rule_info)
                else:
                    # Add reason for non-match
                    reasons = []
                    if not rule.get("enabled", True):
                        reasons.append("disabled")
                    if rule.get("message_type") != message_type:
                        reasons.append("message_type_mismatch")
                    if not self._matches_project_filter(rule.get("project_filter", {}), project_directory):
                        reasons.append("project_filter_mismatch")
                    
                    rule_info["non_match_reasons"] = reasons
                    results["non_matching_rules"].append(rule_info)
            
            return results
            
        except Exception as e:
            return {"error": str(e)}
