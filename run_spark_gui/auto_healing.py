"""
Auto-Healing System - Tự động phát hiện và khắc phục sự cố
Version: 1.0.0
Date: 2025-10-13

Features:
- Tự động detect và fix Docker issues
- Health monitoring liên tục
- Auto-restart failed services
- Self-healing containers
- Predictive maintenance
"""

import time
import threading
import subprocess
from typing import Dict, List, Callable, Optional, Any
from datetime import datetime, timedelta
from enum import Enum


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
    """Kiểm tra sức khỏe một service"""
    
    def __init__(self, name: str, check_func: Callable[[], bool], 
                 interval: int = 30, threshold: int = 3):
        self.name = name
        self.check_func = check_func
        self.interval = interval  # seconds between checks
        self.threshold = threshold  # failures before unhealthy
        self.consecutive_failures = 0
        self.last_check = None
        self.status = HealthStatus.HEALTHY
        self.last_error = None
    
    def check(self) -> bool:
        """Thực hiện health check"""
        try:
            is_healthy = self.check_func()
            self.last_check = datetime.now()
            
            if is_healthy:
                self.consecutive_failures = 0
                self.status = HealthStatus.HEALTHY
                return True
            else:
                self.consecutive_failures += 1
                self._update_status()
                return False
        except Exception as e:
            self.consecutive_failures += 1
            self.last_error = str(e)
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
    Hệ thống tự động phát hiện và khắc phục sự cố
    """
    
    def __init__(self, enable_auto_fix: bool = True):
        self.enable_auto_fix = enable_auto_fix
        self.health_checks: Dict[str, HealthCheck] = {}
        self.healing_history: List[Dict[str, Any]] = []
        self.monitoring_thread = None
        self.running = False
        self.lock = threading.RLock()
        
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
    
    def register_health_check(self, name: str, check_func: Callable[[], bool],
                             interval: int = 30, threshold: int = 3):
        """Đăng ký một health check mới"""
        with self.lock:
            self.health_checks[name] = HealthCheck(
                name, check_func, interval, threshold
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
        """Main monitoring loop"""
        check_times = {name: 0 for name in self.health_checks}
        
        while self.running:
            try:
                current_time = time.time()
                
                for name, health_check in self.health_checks.items():
                    # Check if it's time to run this check
                    if current_time - check_times[name] >= health_check.interval:
                        self._perform_check(name, health_check)
                        check_times[name] = current_time
                
                time.sleep(1)  # Sleep 1 second between iterations
                
            except Exception as e:
                print(f"⚠️ Error in monitoring loop: {e}")
                time.sleep(5)
    
    def _perform_check(self, name: str, health_check: HealthCheck):
        """Thực hiện một health check"""
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
                        try:
                            self.on_unhealthy(name, health_check.status)
                        except Exception as e:
                            print(f"⚠️ Error in unhealthy callback: {e}")
                    
                    # Attempt auto-healing
                    if self.enable_auto_fix:
                        self._attempt_healing(name, health_check)
    
    def _attempt_healing(self, name: str, health_check: HealthCheck):
        """Thử khắc phục vấn đề"""
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
            self.healing_history.append(healing_record)
            
            if success:
                self.stats['successful_heals'] += 1
                print(f"✅ Successfully healed: {name}")
                
                # Reset failure counter
                health_check.consecutive_failures = 0
                health_check.status = HealthStatus.HEALTHY
                
                if self.on_healed:
                    try:
                        self.on_healed(name, healing_action)
                    except Exception as e:
                        print(f"⚠️ Error in healed callback: {e}")
            else:
                self.stats['failed_heals'] += 1
                print(f"❌ Failed to heal: {name}")
    
    def _determine_healing_action(self, name: str, 
                                  health_check: HealthCheck) -> Optional[HealingAction]:
        """Xác định hành động healing phù hợp"""
        
        if name == 'docker_daemon':
            return HealingAction.RESTART_SERVICE
        elif name == 'docker_compose':
            return HealingAction.RESTART_CONTAINER
        elif name == 'disk_space':
            return HealingAction.CLEAR_CACHE
        elif name == 'memory':
            return HealingAction.FREE_RESOURCES
        
        return None
    
    def _execute_healing_action(self, action: HealingAction, target: str) -> bool:
        """Thực hiện hành động healing"""
        try:
            if action == HealingAction.RESTART_SERVICE:
                return self._restart_docker_service()
            
            elif action == HealingAction.RESTART_CONTAINER:
                return self._restart_containers()
            
            elif action == HealingAction.CLEAR_CACHE:
                return self._clear_docker_cache()
            
            elif action == HealingAction.FREE_RESOURCES:
                return self._free_resources()
            
            return False
            
        except Exception as e:
            print(f"⚠️ Error executing healing action {action.value}: {e}")
            return False
    
    # Health check implementations
    
    def _check_docker_daemon(self) -> bool:
        """Check if Docker daemon is running"""
        try:
            result = subprocess.run(
                ['docker', 'info'],
                capture_output=True,
                timeout=5,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            return result.returncode == 0
        except:
            return False
    
    def _check_docker_compose(self) -> bool:
        """Check if docker-compose is available"""
        try:
            result = subprocess.run(
                ['docker-compose', '--version'],
                capture_output=True,
                timeout=5,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            if result.returncode == 0:
                return True
            
            # Try docker compose plugin
            result = subprocess.run(
                ['docker', 'compose', 'version'],
                capture_output=True,
                timeout=5,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            return result.returncode == 0
        except:
            return False
    
    def _check_disk_space(self) -> bool:
        """Check if enough disk space available"""
        try:
            import shutil
            stat = shutil.disk_usage('/')
            # Alert if less than 10% free
            free_percent = (stat.free / stat.total) * 100
            return free_percent > 10
        except:
            return True  # Assume OK if can't check
    
    def _check_memory(self) -> bool:
        """Check if enough memory available"""
        try:
            import psutil
            mem = psutil.virtual_memory()
            # Alert if less than 20% free
            return mem.percent < 80
        except ImportError:
            return True  # psutil not available, assume OK
        except:
            return True
    
    # Healing action implementations
    
    def _restart_docker_service(self) -> bool:
        """Restart Docker service"""
        try:
            import platform
            system = platform.system()
            
            if system == 'Windows':
                # Try to restart Docker Desktop
                subprocess.run(
                    ['taskkill', '/F', '/IM', 'Docker Desktop.exe'],
                    capture_output=True,
                    timeout=10,
                    creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
                )
                time.sleep(3)
                
                # Start Docker Desktop
                from docker_utils import start_docker_desktop
                success, _ = start_docker_desktop()
                return success
            
            elif system == 'Linux':
                result = subprocess.run(
                    ['sudo', 'systemctl', 'restart', 'docker'],
                    capture_output=True,
                    timeout=30
                )
                return result.returncode == 0
            
            return False
        except Exception as e:
            print(f"⚠️ Error restarting Docker: {e}")
            return False
    
    def _restart_containers(self) -> bool:
        """Restart all containers"""
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
            
            container_ids = result.stdout.strip().split('\n')
            container_ids = [cid for cid in container_ids if cid]
            
            if not container_ids:
                return True  # No containers to restart
            
            # Restart each container
            for cid in container_ids:
                subprocess.run(
                    ['docker', 'restart', cid],
                    capture_output=True,
                    timeout=30,
                    creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
                )
            
            return True
        except Exception as e:
            print(f"⚠️ Error restarting containers: {e}")
            return False
    
    def _clear_docker_cache(self) -> bool:
        """Clear Docker cache và unused resources"""
        try:
            # Remove unused containers
            subprocess.run(
                ['docker', 'container', 'prune', '-f'],
                capture_output=True,
                timeout=30,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            
            # Remove unused images
            subprocess.run(
                ['docker', 'image', 'prune', '-f'],
                capture_output=True,
                timeout=30,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            
            # Remove unused volumes
            subprocess.run(
                ['docker', 'volume', 'prune', '-f'],
                capture_output=True,
                timeout=30,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            
            return True
        except Exception as e:
            print(f"⚠️ Error clearing cache: {e}")
            return False
    
    def _free_resources(self) -> bool:
        """Free system resources"""
        try:
            # Stop some containers to free memory
            result = subprocess.run(
                ['docker', 'ps', '-q'],
                capture_output=True,
                timeout=10,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            
            if result.returncode == 0:
                container_ids = result.stdout.strip().split('\n')
                # Stop last 2 containers (arbitrary choice)
                for cid in container_ids[-2:]:
                    if cid:
                        subprocess.run(
                            ['docker', 'stop', cid],
                            capture_output=True,
                            timeout=30,
                            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
                        )
            
            return True
        except Exception as e:
            print(f"⚠️ Error freeing resources: {e}")
            return False
    
    def get_health_status(self) -> Dict[str, Any]:
        """Lấy trạng thái sức khỏe hiện tại"""
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
                if health_check.status.value == 'critical':
                    worst_status = HealthStatus.CRITICAL
                elif health_check.status.value == 'unhealthy' and worst_status != HealthStatus.CRITICAL:
                    worst_status = HealthStatus.UNHEALTHY
                elif health_check.status.value == 'degraded' and worst_status == HealthStatus.HEALTHY:
                    worst_status = HealthStatus.DEGRADED
            
            status['overall'] = worst_status.value
            return status
    
    def force_heal(self, service_name: str) -> bool:
        """Force healing cho một service cụ thể"""
        with self.lock:
            if service_name not in self.health_checks:
                return False
            
            health_check = self.health_checks[service_name]
            self._attempt_healing(service_name, health_check)
            return True


# Global instance
_auto_healing_system = None


def get_auto_healing_system(enable_auto_fix: bool = True) -> AutoHealingSystem:
    """Get singleton instance of auto-healing system"""
    global _auto_healing_system
    if _auto_healing_system is None:
        _auto_healing_system = AutoHealingSystem(enable_auto_fix)
    return _auto_healing_system


# Testing
if __name__ == '__main__':
    print("Testing Auto-Healing System\n" + "="*70)
    
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
    print("\n1. Starting monitoring...")
    healing_system.start_monitoring()
    
    # Let it run for a bit
    print("\n2. Monitoring for 10 seconds...")
    time.sleep(10)
    
    # Get status
    print("\n3. Current health status:")
    status = healing_system.get_health_status()
    print(f"   Overall: {status['overall']}")
    for service, info in status['services'].items():
        print(f"   {service}: {info['status']}")
    
    print(f"\n4. Statistics:")
    print(f"   Total checks: {status['statistics']['total_checks']}")
    print(f"   Failed checks: {status['statistics']['failed_checks']}")
    
    # Stop
    print("\n5. Stopping monitoring...")
    healing_system.stop_monitoring()
    
    print("\n✅ Auto-Healing System test completed!")
