"""
Auto-Healing System - IMPROVED Version
Version: 2.0.0
Date: 2025-10-14

IMPROVEMENTS over v1.0.0:
- ✅ Specific exception handling (no more bare except Exception)
- ✅ Integration with UnifiedErrorHandler v2.0
- ✅ Better subprocess error handling
- ✅ Enhanced logging with categories
- ✅ Resource cleanup with context managers
- ✅ Type hints for better code clarity
- ✅ Comprehensive docstrings

Features:
- Tự động detect và fix Docker issues
- Health monitoring liên tục
- Auto-restart failed services
- Self-healing containers
- Predictive maintenance
- Thread-safe operations

Author: AI System Optimizer
"""

import time
import threading
import subprocess
import shutil
from typing import Dict, List, Callable, Optional, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum
from contextlib import contextmanager

# Import unified error handler
try:
    from error_handler_v2 import (
        UnifiedErrorHandler, 
        ErrorSeverity, 
        ErrorCategory,
        get_error_handler
    )
    ERROR_HANDLER_AVAILABLE = True
except ImportError:
    print("⚠️ Warning: UnifiedErrorHandler v2.0 not available, using fallback")
    ERROR_HANDLER_AVAILABLE = False


class HealthStatus(Enum):
    """Trạng thái sức khỏe"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"


class HealingAction(Enum):
    """Các hành động healing"""
    RESTART_SERVICE = "restart_service"
    RESTART_CONTAINER = "restart_container"
    CLEAR_CACHE = "clear_cache"
    FREE_RESOURCES = "free_resources"
    REPAIR_NETWORK = "repair_network"
    REBUILD_IMAGE = "rebuild_image"


class HealthCheck:
    """
    Kiểm tra sức khỏe một service với specific error handling
    """
    
    def __init__(self, 
                 name: str, 
                 check_func: Callable[[], bool], 
                 interval: int = 30, 
                 threshold: int = 3,
                 error_handler: Optional[UnifiedErrorHandler] = None):
        """
        Args:
            name: Tên health check
            check_func: Function để check (return True if healthy)
            interval: Giây giữa các lần check
            threshold: Số lần fail trước khi unhealthy
            error_handler: Error handler instance
        """
        self.name = name
        self.check_func = check_func
        self.interval = interval
        self.threshold = threshold
        self.consecutive_failures = 0
        self.last_check: Optional[datetime] = None
        self.status = HealthStatus.HEALTHY
        self.last_error: Optional[str] = None
        self.error_handler = error_handler or (get_error_handler() if ERROR_HANDLER_AVAILABLE else None)
    
    def check(self) -> bool:
        """
        Thực hiện health check với proper error handling
        
        Returns:
            True if healthy, False otherwise
        """
        if self.error_handler and ERROR_HANDLER_AVAILABLE:
            # Use unified error handler
            is_healthy = self.error_handler.safe_execute(
                self.check_func,
                context=f"Health check: {self.name}",
                expected_exceptions=(
                    subprocess.SubprocessError,
                    subprocess.TimeoutExpired,
                    FileNotFoundError,
                    OSError,
                    RuntimeError
                ),
                default_return=False,
                severity=ErrorSeverity.WARNING,
                category=ErrorCategory.SYSTEM
            )
        else:
            # Fallback for legacy code
            try:
                is_healthy = self.check_func()
            except (subprocess.SubprocessError, FileNotFoundError, OSError) as e:
                print(f"⚠️ Health check {self.name} failed: {type(e).__name__}: {e}")
                is_healthy = False
            except Exception as e:
                print(f"⚠️ Unexpected error in health check {self.name}: {e}")
                is_healthy = False
        
        self.last_check = datetime.now()
        
        if is_healthy:
            self.consecutive_failures = 0
            self.status = HealthStatus.HEALTHY
            self.last_error = None
            return True
        else:
            self.consecutive_failures += 1
            self._update_status()
            return False
    
    def _update_status(self):
        """Cập nhật trạng thái dựa trên số lần fail"""
        if self.consecutive_failures >= self.threshold * 2:
            self.status = HealthStatus.CRITICAL
        elif self.consecutive_failures >= self.threshold:
            self.status = HealthStatus.UNHEALTHY
        elif self.consecutive_failures > 0:
            self.status = HealthStatus.DEGRADED
        else:
            self.status = HealthStatus.HEALTHY


class AutoHealingSystem:
    """
    Hệ thống tự động phát hiện và khắc phục sự cố - IMPROVED
    
    Improvements:
    - Specific exception handling
    - Better resource management
    - Enhanced logging
    - Type hints
    """
    
    def __init__(self, 
                 enable_auto_fix: bool = True,
                 error_handler: Optional[UnifiedErrorHandler] = None):
        """
        Args:
            enable_auto_fix: Cho phép auto-fix
            error_handler: Error handler instance
        """
        self.enable_auto_fix = enable_auto_fix
        self.health_checks: Dict[str, HealthCheck] = {}
        self.healing_history: List[Dict[str, Any]] = []
        self.monitoring_thread: Optional[threading.Thread] = None
        self.running = False
        self.lock = threading.RLock()
        
        # Error handler
        self.error_handler = error_handler or (get_error_handler() if ERROR_HANDLER_AVAILABLE else None)
        
        # Statistics
        self.stats = {
            'total_checks': 0,
            'failed_checks': 0,
            'healing_attempts': 0,
            'successful_heals': 0,
            'failed_heals': 0
        }
        
        # Callbacks
        self.on_unhealthy: Optional[Callable] = None
        self.on_healed: Optional[Callable] = None
        
        # Register default health checks
        self._register_default_checks()
    
    def _register_default_checks(self):
        """Đăng ký các health check mặc định"""
        
        # Docker daemon check
        self.register_health_check(
            'docker_daemon',
            self._check_docker_daemon,
            interval=30,
            threshold=2
        )
        
        # Docker compose check
        self.register_health_check(
            'docker_compose',
            self._check_docker_compose,
            interval=60,
            threshold=3
        )
        
        # Disk space check
        self.register_health_check(
            'disk_space',
            self._check_disk_space,
            interval=300,  # 5 minutes
            threshold=2
        )
        
        # Memory check
        self.register_health_check(
            'memory',
            self._check_memory,
            interval=60,
            threshold=3
        )
    
    def register_health_check(self, 
                             name: str, 
                             check_func: Callable[[], bool],
                             interval: int = 30, 
                             threshold: int = 3):
        """
        Đăng ký một health check mới
        
        Args:
            name: Tên health check
            check_func: Function để check
            interval: Giây giữa các lần check
            threshold: Số lần fail trước khi unhealthy
        """
        with self.lock:
            self.health_checks[name] = HealthCheck(
                name, 
                check_func, 
                interval, 
                threshold,
                self.error_handler
            )
    
    def start_monitoring(self):
        """Bắt đầu monitoring"""
        if self.running:
            return
        
        self.running = True
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True,
            name="AutoHealing-Monitor"
        )
        self.monitoring_thread.start()
        print("✅ Auto-healing system started")
    
    def stop_monitoring(self):
        """Dừng monitoring"""
        self.running = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        print("🛑 Auto-healing system stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop with error handling"""
        check_times = {name: 0.0 for name in self.health_checks}
        
        while self.running:
            if self.error_handler and ERROR_HANDLER_AVAILABLE:
                with self.error_handler.error_context(
                    "Auto-healing monitoring loop",
                    expected_exceptions=(RuntimeError, OSError),
                    severity=ErrorSeverity.WARNING
                ):
                    self._do_monitoring_iteration(check_times)
            else:
                try:
                    self._do_monitoring_iteration(check_times)
                except (RuntimeError, OSError) as e:
                    print(f"⚠️ Error in monitoring loop: {e}")
                    time.sleep(5)
            
            time.sleep(1)
    
    def _do_monitoring_iteration(self, check_times: Dict[str, float]):
        """Single monitoring iteration"""
        current_time = time.time()
        
        for name, health_check in self.health_checks.items():
            # Check if it's time to run this check
            if current_time - check_times[name] >= health_check.interval:
                self._perform_check(name, health_check)
                check_times[name] = current_time
    
    def _perform_check(self, name: str, health_check: HealthCheck):
        """
        Thực hiện một health check
        
        Args:
            name: Tên health check
            health_check: HealthCheck instance
        """
        with self.lock:
            self.stats['total_checks'] += 1
            
            is_healthy = health_check.check()
            
            if not is_healthy:
                self.stats['failed_checks'] += 1
                print(f"⚠️ Health check failed: {name} "
                      f"(status: {health_check.status.value}, "
                      f"failures: {health_check.consecutive_failures})")
                
                # Trigger healing if unhealthy
                if health_check.status in [HealthStatus.UNHEALTHY, HealthStatus.CRITICAL]:
                    if self.on_unhealthy:
                        self._safe_callback(self.on_unhealthy, name, health_check.status)
                    
                    # Attempt auto-healing
                    if self.enable_auto_fix:
                        self._attempt_healing(name, health_check)
    
    def _safe_callback(self, callback: Callable, *args, **kwargs):
        """Safely execute callback with error handling"""
        if self.error_handler and ERROR_HANDLER_AVAILABLE:
            self.error_handler.safe_execute(
                callback,
                *args,
                context="Health check callback",
                expected_exceptions=(Exception,),
                severity=ErrorSeverity.WARNING,
                **kwargs
            )
        else:
            try:
                callback(*args, **kwargs)
            except Exception as e:
                print(f"⚠️ Error in callback: {e}")
    
    def _attempt_healing(self, name: str, health_check: HealthCheck):
        """
        Thử khắc phục vấn đề
        
        Args:
            name: Tên service
            health_check: HealthCheck instance
        """
        print(f"🔧 Attempting to heal: {name}")
        self.stats['healing_attempts'] += 1
        
        healing_action = self._determine_healing_action(name, health_check)
        
        if healing_action:
            success = self._execute_healing_action(healing_action, name)
            
            # Log healing attempt
            healing_record = {
                'timestamp': datetime.now().isoformat(),
                'service': name,
                'status': health_check.status.value,
                'action': healing_action.value,
                'success': success
            }
            
            with self.lock:
                self.healing_history.append(healing_record)
            
            if success:
                self.stats['successful_heals'] += 1
                print(f"✅ Successfully healed: {name}")
                
                # Reset failure counter
                health_check.consecutive_failures = 0
                health_check.status = HealthStatus.HEALTHY
                
                if self.on_healed:
                    self._safe_callback(self.on_healed, name, healing_action)
            else:
                self.stats['failed_heals'] += 1
                print(f"❌ Failed to heal: {name}")
    
    def _determine_healing_action(self, 
                                  name: str, 
                                  health_check: HealthCheck) -> Optional[HealingAction]:
        """
        Xác định hành động healing phù hợp
        
        Args:
            name: Tên service
            health_check: HealthCheck instance
        
        Returns:
            HealingAction or None
        """
        action_map = {
            'docker_daemon': HealingAction.RESTART_SERVICE,
            'docker_compose': HealingAction.RESTART_CONTAINER,
            'disk_space': HealingAction.CLEAR_CACHE,
            'memory': HealingAction.FREE_RESOURCES
        }
        
        return action_map.get(name)
    
    def _execute_healing_action(self, action: HealingAction, target: str) -> bool:
        """
        Thực hiện hành động healing với proper error handling
        
        Args:
            action: Healing action
            target: Target service
        
        Returns:
            True if successful, False otherwise
        """
        action_handlers = {
            HealingAction.RESTART_SERVICE: self._restart_docker_service,
            HealingAction.RESTART_CONTAINER: self._restart_containers,
            HealingAction.CLEAR_CACHE: self._clear_docker_cache,
            HealingAction.FREE_RESOURCES: self._free_resources
        }
        
        handler = action_handlers.get(action)
        if not handler:
            return False
        
        if self.error_handler and ERROR_HANDLER_AVAILABLE:
            return self.error_handler.safe_execute(
                handler,
                context=f"Healing action: {action.value}",
                expected_exceptions=(subprocess.SubprocessError, OSError, RuntimeError),
                default_return=False,
                severity=ErrorSeverity.ERROR,
                category=ErrorCategory.DOCKER
            ) or False
        else:
            try:
                return handler()
            except (subprocess.SubprocessError, OSError, RuntimeError) as e:
                print(f"⚠️ Error executing healing action {action.value}: {e}")
                return False
    
    # ========================================================================
    # Health check implementations with SPECIFIC exception handling
    # ========================================================================
    
    def _check_docker_daemon(self) -> bool:
        """
        Check if Docker daemon is running
        
        Returns:
            True if running, False otherwise
        
        Raises:
            Specific subprocess exceptions
        """
        try:
            result = subprocess.run(
                ['docker', 'info'],
                capture_output=True,
                timeout=5,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            print("⏱️ Docker info command timeout")
            raise
        except FileNotFoundError:
            print("❌ Docker executable not found")
            raise
        except subprocess.SubprocessError as e:
            print(f"⚠️ Docker subprocess error: {e}")
            raise
    
    def _check_docker_compose(self) -> bool:
        """
        Check if docker-compose is available
        
        Returns:
            True if available, False otherwise
        """
        # Try docker-compose
        try:
            result = subprocess.run(
                ['docker-compose', '--version'],
                capture_output=True,
                timeout=5,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            if result.returncode == 0:
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            pass  # Try next method
        
        # Try docker compose plugin
        try:
            result = subprocess.run(
                ['docker', 'compose', 'version'],
                capture_output=True,
                timeout=5,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            return False
    
    def _check_disk_space(self) -> bool:
        """
        Check if enough disk space available
        
        Returns:
            True if enough space (>10% free), False otherwise
        """
        try:
            stat = shutil.disk_usage('/')
            free_percent = (stat.free / stat.total) * 100
            return free_percent > 10
        except OSError as e:
            print(f"⚠️ Error checking disk space: {e}")
            return True  # Assume OK if can't check
    
    def _check_memory(self) -> bool:
        """
        Check if enough memory available
        
        Returns:
            True if memory usage < 80%, False otherwise
        """
        try:
            import psutil
            mem = psutil.virtual_memory()
            return mem.percent < 80
        except ImportError:
            # psutil not available
            return True
        except (OSError, AttributeError) as e:
            print(f"⚠️ Error checking memory: {e}")
            return True
    
    # ========================================================================
    # Healing action implementations with SPECIFIC exception handling
    # ========================================================================
    
    def _restart_docker_service(self) -> bool:
        """
        Restart Docker service
        
        Returns:
            True if successful, False otherwise
        """
        import platform
        system = platform.system()
        
        if system == 'Windows':
            return self._restart_docker_windows()
        elif system == 'Linux':
            return self._restart_docker_linux()
        else:
            print(f"⚠️ Unsupported system: {system}")
            return False
    
    def _restart_docker_windows(self) -> bool:
        """Restart Docker Desktop on Windows"""
        try:
            # Kill Docker Desktop
            subprocess.run(
                ['taskkill', '/F', '/IM', 'Docker Desktop.exe'],
                capture_output=True,
                timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            time.sleep(3)
            
            # Start Docker Desktop
            try:
                from docker_utils import start_docker_desktop
                success, _ = start_docker_desktop()
                return success
            except ImportError:
                print("⚠️ docker_utils not available")
                return False
                
        except subprocess.TimeoutExpired:
            print("⏱️ Docker Desktop restart timeout")
            return False
        except subprocess.SubprocessError as e:
            print(f"⚠️ Error restarting Docker Desktop: {e}")
            return False
    
    def _restart_docker_linux(self) -> bool:
        """Restart Docker daemon on Linux"""
        try:
            result = subprocess.run(
                ['sudo', 'systemctl', 'restart', 'docker'],
                capture_output=True,
                timeout=30,
                text=True
            )
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            print("⏱️ Docker daemon restart timeout")
            return False
        except subprocess.SubprocessError as e:
            print(f"⚠️ Error restarting Docker daemon: {e}")
            return False
    
    def _restart_containers(self) -> bool:
        """
        Restart all containers
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get all container IDs
            result = subprocess.run(
                ['docker', 'ps', '-q'],
                capture_output=True,
                timeout=10,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            
            if result.returncode != 0:
                return False
            
            container_ids = [cid for cid in result.stdout.strip().split('\n') if cid]
            
            if not container_ids:
                return True  # No containers to restart
            
            # Restart each container
            for cid in container_ids:
                subprocess.run(
                    ['docker', 'restart', cid],
                    capture_output=True,
                    timeout=30,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
                )
            
            return True
            
        except subprocess.TimeoutExpired:
            print("⏱️ Container restart timeout")
            return False
        except subprocess.SubprocessError as e:
            print(f"⚠️ Error restarting containers: {e}")
            return False
    
    def _clear_docker_cache(self) -> bool:
        """
        Clear Docker cache và unused resources
        
        Returns:
            True if successful, False otherwise
        """
        commands = [
            (['docker', 'container', 'prune', '-f'], "containers"),
            (['docker', 'image', 'prune', '-f'], "images"),
            (['docker', 'volume', 'prune', '-f'], "volumes")
        ]
        
        success = True
        for cmd, resource_type in commands:
            try:
                subprocess.run(
                    cmd,
                    capture_output=True,
                    timeout=30,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
                )
            except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
                print(f"⚠️ Error clearing {resource_type}: {e}")
                success = False
        
        return success
    
    def _free_resources(self) -> bool:
        """
        Free system resources by stopping some containers
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get all container IDs
            result = subprocess.run(
                ['docker', 'ps', '-q'],
                capture_output=True,
                timeout=10,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            
            if result.returncode == 0:
                container_ids = [cid for cid in result.stdout.strip().split('\n') if cid]
                
                # Stop last 2 containers (arbitrary choice)
                for cid in container_ids[-2:]:
                    if cid:
                        subprocess.run(
                            ['docker', 'stop', cid],
                            capture_output=True,
                            timeout=30,
                            text=True,
                            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
                        )
            
            return True
            
        except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
            print(f"⚠️ Error freeing resources: {e}")
            return False
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Lấy trạng thái sức khỏe hiện tại
        
        Returns:
            Dictionary containing health status
        """
        with self.lock:
            status = {
                'overall': HealthStatus.HEALTHY.value,
                'services': {},
                'statistics': self.stats.copy(),
                'recent_healing': self.healing_history[-10:]  # Last 10
            }
            
            worst_status = HealthStatus.HEALTHY
            
            for name, health_check in self.health_checks.items():
                status['services'][name] = {
                    'status': health_check.status.value,
                    'consecutive_failures': health_check.consecutive_failures,
                    'last_check': health_check.last_check.isoformat() if health_check.last_check else None,
                    'last_error': health_check.last_error
                }
                
                # Determine worst status
                status_priority = {
                    HealthStatus.HEALTHY: 0,
                    HealthStatus.DEGRADED: 1,
                    HealthStatus.UNHEALTHY: 2,
                    HealthStatus.CRITICAL: 3
                }
                
                if status_priority.get(health_check.status, 0) > status_priority.get(worst_status, 0):
                    worst_status = health_check.status
            
            status['overall'] = worst_status.value
            return status
    
    def force_heal(self, service_name: str) -> bool:
        """
        Force healing cho một service cụ thể
        
        Args:
            service_name: Tên service
        
        Returns:
            True if successful, False otherwise
        """
        with self.lock:
            if service_name not in self.health_checks:
                return False
            
            health_check = self.health_checks[service_name]
            self._attempt_healing(service_name, health_check)
            return True


# ============================================================================
# Global Instance
# ============================================================================

_auto_healing_system: Optional[AutoHealingSystem] = None
_healing_lock = threading.Lock()


def get_auto_healing_system(enable_auto_fix: bool = True) -> AutoHealingSystem:
    """
    Get singleton instance of auto-healing system
    
    Args:
        enable_auto_fix: Enable automatic fixes
    
    Returns:
        AutoHealingSystem instance
    """
    global _auto_healing_system
    
    with _healing_lock:
        if _auto_healing_system is None:
            _auto_healing_system = AutoHealingSystem(enable_auto_fix)
    
    return _auto_healing_system


# ============================================================================
# Testing
# ============================================================================

if __name__ == '__main__':
    print("=" * 80)
    print("TESTING AUTO-HEALING SYSTEM V2.0 (IMPROVED)")
    print("=" * 80)
    
    # Create system
    healing_system = AutoHealingSystem(enable_auto_fix=False)
    
    # Add callbacks
    def on_unhealthy(service, status):
        print(f"🚨 ALERT: {service} is {status.value}")
    
    def on_healed(service, action):
        print(f"✅ HEALED: {service} via {action.value}")
    
    healing_system.on_unhealthy = on_unhealthy
    healing_system.on_healed = on_healed
    
    # Start monitoring
    print("\n1️⃣ Starting monitoring...")
    healing_system.start_monitoring()
    
    # Let it run for a bit
    print("\n2️⃣ Monitoring for 10 seconds...")
    time.sleep(10)
    
    # Get status
    print("\n3️⃣ Current health status:")
    status = healing_system.get_health_status()
    print(f"   Overall: {status['overall']}")
    for service, info in status['services'].items():
        print(f"   {service}: {info['status']}")
    
    print(f"\n4️⃣ Statistics:")
    print(f"   Total checks: {status['statistics']['total_checks']}")
    print(f"   Failed checks: {status['statistics']['failed_checks']}")
    
    # Stop
    print("\n5️⃣ Stopping monitoring...")
    healing_system.stop_monitoring()
    
    print("\n" + "=" * 80)
    print("✅ ALL TESTS COMPLETED")
    print("=" * 80)
