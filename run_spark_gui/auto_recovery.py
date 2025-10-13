"""
Auto-Recovery System
Version: 1.0.1 - Fixed type hints compatibility

Provides automatic recovery from common failures:
- Docker connection issues
- File system errors
- Network timeouts
- Configuration errors
"""

import time
import threading
from typing import Callable, Optional, Any, Dict, Tuple
from datetime import datetime, timedelta


class RecoveryAction:
    """Represents a recovery action with metadata"""
    
    def __init__(self, name: str, action: Callable, 
                 cooldown: int = 300, max_attempts: int = 3):
        self.name = name
        self.action = action
        self.cooldown = cooldown  # Seconds before retry
        self.max_attempts = max_attempts
        self.last_attempt = None
        self.attempt_count = 0
        self.success_count = 0
        self.failure_count = 0
    
    def can_retry(self) -> bool:
        """Check if enough time has passed since last attempt"""
        if self.last_attempt is None:
            return True
        
        elapsed = (datetime.now() - self.last_attempt).total_seconds()
        return elapsed >= self.cooldown and self.attempt_count < self.max_attempts
    
    def execute(self) -> Tuple[bool, str]:
        """Execute recovery action"""
        if not self.can_retry():
            cooldown_remaining = self.cooldown - (datetime.now() - self.last_attempt).total_seconds()
            return False, f"Recovery on cooldown ({cooldown_remaining:.0f}s remaining)"
        
        self.last_attempt = datetime.now()
        self.attempt_count += 1
        
        try:
            result = self.action()
            self.success_count += 1
            self.attempt_count = 0  # Reset on success
            return True, f"Recovery '{self.name}' succeeded"
        except Exception as e:
            self.failure_count += 1
            return False, f"Recovery '{self.name}' failed: {e}"
    
    def reset(self):
        """Reset attempt counter"""
        self.attempt_count = 0
        self.last_attempt = None


class AutoRecoveryManager:
    """Manages automatic recovery actions"""
    
    def __init__(self, logger=None):
        self.logger = logger
        self.recovery_actions: Dict[str, RecoveryAction] = {}
        self.enabled = True
        self.lock = threading.Lock()
        self._register_default_actions()
    
    def _register_default_actions(self):
        """Register common recovery actions"""
        
        # Docker restart recovery
        def restart_docker():
            try:
                from docker_utils import ensure_docker_running
                success, message = ensure_docker_running(
                    log_callback=lambda msg, tag: self._log(msg) if self.logger else None,
                    auto_start=True,
                    wait=True
                )
                if not success:
                    raise Exception(message)
                return True
            except Exception as e:
                raise Exception(f"Failed to restart Docker: {e}")
        
        self.register_action(
            'restart_docker',
            restart_docker,
            cooldown=300,  # 5 minutes
            max_attempts=3
        )
        
        # Cache clear recovery
        def clear_cache():
            try:
                from system_utils import cache_manager
                cache_manager.clear_all()
                self._log("🗑️ Cache cleared successfully")
                return True
            except Exception as e:
                raise Exception(f"Failed to clear cache: {e}")
        
        self.register_action(
            'clear_cache',
            clear_cache,
            cooldown=60,  # 1 minute
            max_attempts=5
        )
        
        # Database reset recovery
        def reset_database():
            try:
                from database import db
                # Don't actually reset, just verify connection
                stats = db.get_job_stats()
                self._log("✅ Database connection verified")
                return True
            except Exception as e:
                raise Exception(f"Database verification failed: {e}")
        
        self.register_action(
            'verify_database',
            reset_database,
            cooldown=120,  # 2 minutes
            max_attempts=3
        )
    
    def register_action(self, name: str, action: Callable, 
                       cooldown: int = 300, max_attempts: int = 3):
        """Register a recovery action"""
        with self.lock:
            self.recovery_actions[name] = RecoveryAction(
                name=name,
                action=action,
                cooldown=cooldown,
                max_attempts=max_attempts
            )
            self._log(f"📝 Registered recovery action: {name}")
    
    def trigger_recovery(self, action_name: str) -> tuple[bool, str]:
        """
        Trigger a specific recovery action
        
        Returns:
            tuple: (success: bool, message: str)
        """
        if not self.enabled:
            return False, "Auto-recovery is disabled"
        
        with self.lock:
            if action_name not in self.recovery_actions:
                return False, f"Unknown recovery action: {action_name}"
            
            action = self.recovery_actions[action_name]
        
        self._log(f"🔄 Triggering recovery: {action_name}")
        success, message = action.execute()
        
        if success:
            self._log(f"✅ {message}")
        else:
            self._log(f"❌ {message}")
        
        return success, message
    
    def auto_recover_from_error(self, error: Exception, context: str = "") -> bool:
        """
        Automatically attempt recovery based on error type
        
        Returns:
            bool: True if recovery succeeded
        """
        if not self.enabled:
            return False
        
        error_msg = str(error).lower()
        error_type = type(error).__name__
        
        # Match error patterns to recovery actions
        recovery_map = {
            'docker': 'restart_docker',
            'connection': 'restart_docker',
            'daemon': 'restart_docker',
            'cache': 'clear_cache',
            'database': 'verify_database',
            'locked': 'verify_database',
        }
        
        # Find matching recovery action
        action_name = None
        for keyword, action in recovery_map.items():
            if keyword in error_msg or keyword in error_type.lower():
                action_name = action
                break
        
        if action_name:
            self._log(f"🔍 Detected {error_type}, attempting {action_name}...")
            success, message = self.trigger_recovery(action_name)
            return success
        
        self._log(f"⚠️ No recovery action for error type: {error_type}")
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get recovery statistics"""
        with self.lock:
            stats = {}
            for name, action in self.recovery_actions.items():
                stats[name] = {
                    'success_count': action.success_count,
                    'failure_count': action.failure_count,
                    'last_attempt': action.last_attempt.isoformat() if action.last_attempt else None,
                    'can_retry': action.can_retry()
                }
            return stats
    
    def enable(self):
        """Enable auto-recovery"""
        self.enabled = True
        self._log("✅ Auto-recovery enabled")
    
    def disable(self):
        """Disable auto-recovery"""
        self.enabled = False
        self._log("⚠️ Auto-recovery disabled")
    
    def _log(self, message: str):
        """Internal logging"""
        if self.logger:
            self.logger.info(message)
        else:
            print(f"[AutoRecovery] {message}")


# Global instance
_auto_recovery_manager = None


def get_auto_recovery_manager(logger=None) -> AutoRecoveryManager:
    """Get global auto-recovery manager"""
    global _auto_recovery_manager
    if _auto_recovery_manager is None:
        _auto_recovery_manager = AutoRecoveryManager(logger)
    return _auto_recovery_manager


if __name__ == '__main__':
    # Test auto-recovery system
    print("Testing Auto-Recovery System...")
    print("=" * 70)
    
    manager = get_auto_recovery_manager()
    
    # Test Docker recovery
    print("\n1. Testing Docker recovery...")
    success, message = manager.trigger_recovery('restart_docker')
    print(f"   Result: {message}")
    
    # Test cache clear
    print("\n2. Testing cache clear...")
    success, message = manager.trigger_recovery('clear_cache')
    print(f"   Result: {message}")
    
    # Test auto-recovery from error
    print("\n3. Testing auto-recovery from simulated error...")
    class DockerError(Exception):
        pass
    
    try:
        raise DockerError("Cannot connect to Docker daemon")
    except Exception as e:
        recovered = manager.auto_recover_from_error(e, "Docker connection test")
        print(f"   Recovered: {recovered}")
    
    # Show stats
    print("\n4. Recovery statistics:")
    stats = manager.get_stats()
    for action, data in stats.items():
        print(f"   {action}:")
        print(f"     - Success: {data['success_count']}, Failures: {data['failure_count']}")
        print(f"     - Can retry: {data['can_retry']}")
    
    print("\n" + "=" * 70)
    print("✅ Auto-recovery tests completed!")
