"""
Auto Recovery Manager
Provides automatic recovery mechanisms for common failures
"""
import os
import json
import time
from typing import Dict, Callable, Optional, List
from datetime import datetime, timedelta


class AutoRecoveryManager:
    """Manages automatic recovery from common failures"""
    
    def __init__(self, logger=None):
        self.logger = logger
        self.recovery_attempts = {}
        self.max_attempts = 3
        self.recovery_cooldown = 60  # seconds
        self.recovery_strategies = {}
        self._register_default_strategies()
    
    def _register_default_strategies(self):
        """Register default recovery strategies"""
        self.register_strategy('connection_lost', self._recover_connection)
        self.register_strategy('file_not_found', self._recover_file)
        self.register_strategy('permission_denied', self._recover_permission)
    
    def register_strategy(self, error_type: str, strategy: Callable):
        """Register a recovery strategy for an error type"""
        self.recovery_strategies[error_type] = strategy
        if self.logger:
            self.logger.info(f"Registered recovery strategy for: {error_type}")
    
    def can_attempt_recovery(self, error_type: str) -> bool:
        """Check if recovery can be attempted for this error type"""
        if error_type not in self.recovery_attempts:
            return True
        
        attempts = self.recovery_attempts[error_type]
        
        # Check attempt count
        if attempts['count'] >= self.max_attempts:
            # Check if cooldown period has passed
            last_attempt = datetime.fromisoformat(attempts['last_attempt'])
            if datetime.now() - last_attempt < timedelta(seconds=self.recovery_cooldown):
                return False
            else:
                # Reset after cooldown
                self.recovery_attempts[error_type] = {
                    'count': 0,
                    'last_attempt': datetime.now().isoformat()
                }
                return True
        
        return True
    
    def attempt_recovery(self, error_type: str, context: Dict = None) -> bool:
        """Attempt to recover from an error"""
        if not self.can_attempt_recovery(error_type):
            if self.logger:
                self.logger.warning(f"Recovery cooldown active for: {error_type}")
            return False
        
        # Update attempt tracking
        if error_type not in self.recovery_attempts:
            self.recovery_attempts[error_type] = {
                'count': 0,
                'last_attempt': datetime.now().isoformat()
            }
        
        self.recovery_attempts[error_type]['count'] += 1
        self.recovery_attempts[error_type]['last_attempt'] = datetime.now().isoformat()
        
        # Find and execute recovery strategy
        strategy = self.recovery_strategies.get(error_type)
        if strategy:
            try:
                if self.logger:
                    self.logger.info(f"Attempting recovery for: {error_type}")
                
                result = strategy(context or {})
                
                if result:
                    if self.logger:
                        self.logger.info(f"Recovery successful for: {error_type}")
                    # Reset attempts on success
                    self.recovery_attempts[error_type]['count'] = 0
                    return True
                else:
                    if self.logger:
                        self.logger.warning(f"Recovery failed for: {error_type}")
                    return False
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Recovery strategy error for {error_type}: {e}")
                return False
        else:
            if self.logger:
                self.logger.warning(f"No recovery strategy found for: {error_type}")
            return False
    
    def _recover_connection(self, context: Dict) -> bool:
        """Recover from connection loss"""
        # Wait and retry
        time.sleep(2)
        return True  # Assume connection will be retried
    
    def _recover_file(self, context: Dict) -> bool:
        """Recover from file not found"""
        file_path = context.get('file_path')
        if file_path:
            # Try to create directory if it doesn't exist
            try:
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                return True
            except:
                return False
        return False
    
    def _recover_permission(self, context: Dict) -> bool:
        """Recover from permission denied"""
        # Log the issue (admin action required)
        if self.logger:
            self.logger.error("Permission denied - manual intervention required")
        return False
    
    def get_stats(self) -> Dict:
        """Get recovery statistics"""
        return {
            'registered_strategies': list(self.recovery_strategies.keys()),
            'recovery_attempts': self.recovery_attempts,
            'max_attempts': self.max_attempts,
            'cooldown_seconds': self.recovery_cooldown
        }


# Global instance
_auto_recovery_manager = None


def get_auto_recovery_manager(logger=None) -> AutoRecoveryManager:
    """Get or create global auto recovery manager"""
    global _auto_recovery_manager
    if _auto_recovery_manager is None:
        _auto_recovery_manager = AutoRecoveryManager(logger)
    return _auto_recovery_manager
