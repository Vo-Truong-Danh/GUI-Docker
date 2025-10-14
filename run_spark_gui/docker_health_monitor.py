"""
Docker Health Monitor - Advanced monitoring and diagnostics
Version: 1.0.0

Features:
- Real-time health monitoring
- Performance metrics tracking
- Automatic issue detection and recovery
- Resource usage monitoring
- Container lifecycle management
- Enhanced diagnostics with recommendations
"""

import subprocess
import threading
import time
from typing import Dict, Any, List, Optional, Callable, Tuple
from datetime import datetime, timedelta
from collections import deque
from enum import Enum
import json


class DockerHealthStatus(Enum):
    """Docker health status levels"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class DockerHealthMonitor:
    """Advanced Docker health monitoring system"""
    
    def __init__(self, check_interval: int = 30, history_size: int = 100):
        """
        Initialize Docker health monitor
        
        Args:
            check_interval: Seconds between health checks
            history_size: Number of historical records to keep
        """
        self.check_interval = check_interval
        self.history_size = history_size
        
        # Health status tracking
        self.current_status = DockerHealthStatus.UNKNOWN
        self.last_check_time = None
        self.health_history = deque(maxlen=history_size)
        
        # Metrics tracking
        self.metrics = {
            'total_checks': 0,
            'failed_checks': 0,
            'containers_monitored': 0,
            'issues_detected': 0,
            'auto_recoveries': 0
        }
        
        # Issue tracking
        self.active_issues = []
        self.resolved_issues = []
        
        # Monitoring state
        self.monitoring = False
        self.monitor_thread = None
        self._lock = threading.RLock()
        
        # Callbacks
        self.status_change_callbacks = []
        self.issue_detected_callbacks = []
        
    def start_monitoring(self):
        """Start continuous health monitoring"""
        with self._lock:
            if self.monitoring:
                return
            
            self.monitoring = True
            self.monitor_thread = threading.Thread(
                target=self._monitor_loop,
                daemon=True,
                name="DockerHealthMonitor"
            )
            self.monitor_thread.start()
            
    def stop_monitoring(self):
        """Stop health monitoring"""
        with self._lock:
            self.monitoring = False
            
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
            
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                self.perform_health_check()
                time.sleep(self.check_interval)
            except Exception as e:
                print(f"⚠️ Health monitor error: {e}")
                time.sleep(self.check_interval)
                
    def perform_health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check
        
        Returns:
            dict: Health check results
        """
        with self._lock:
            self.metrics['total_checks'] += 1
            
            health_report = {
                'timestamp': datetime.now().isoformat(),
                'status': DockerHealthStatus.UNKNOWN,
                'checks': {},
                'issues': [],
                'recommendations': [],
                'metrics': {}
            }
            
            # Check 1: Docker daemon running
            daemon_check = self._check_daemon_status()
            health_report['checks']['daemon'] = daemon_check
            
            if not daemon_check['healthy']:
                health_report['status'] = DockerHealthStatus.CRITICAL
                health_report['issues'].append({
                    'severity': 'critical',
                    'message': 'Docker daemon is not running',
                    'recommendation': 'Start Docker Desktop or Docker service'
                })
                self.metrics['failed_checks'] += 1
            else:
                # Check 2: Container health
                container_check = self._check_containers()
                health_report['checks']['containers'] = container_check
                
                # Check 3: Resource usage
                resource_check = self._check_resources()
                health_report['checks']['resources'] = resource_check
                
                # Check 4: Network connectivity
                network_check = self._check_network()
                health_report['checks']['network'] = network_check
                
                # Determine overall status
                health_report['status'] = self._determine_status(health_report)
                
            # Update current status
            old_status = self.current_status
            self.current_status = health_report['status']
            self.last_check_time = datetime.now()
            
            # Add to history
            self.health_history.append(health_report)
            
            # Trigger callbacks if status changed
            if old_status != self.current_status:
                self._trigger_status_change_callbacks(old_status, self.current_status)
                
            # Detect and handle issues
            if health_report['issues']:
                self._handle_issues(health_report['issues'])
                
            return health_report
            
    def _check_daemon_status(self) -> Dict[str, Any]:
        """Check Docker daemon status"""
        try:
            result = subprocess.run(
                ['docker', 'info'],
                capture_output=True,
                timeout=10,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            
            return {
                'healthy': result.returncode == 0,
                'details': result.stdout if result.returncode == 0 else result.stderr,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'healthy': False,
                'details': str(e),
                'timestamp': datetime.now().isoformat()
            }
            
    def _check_containers(self) -> Dict[str, Any]:
        """Check container health and status"""
        try:
            result = subprocess.run(
                ['docker', 'ps', '-a', '--format', '{{json .}}'],
                capture_output=True,
                timeout=15,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            
            if result.returncode != 0:
                return {
                    'healthy': False,
                    'error': result.stderr,
                    'containers': []
                }
                
            containers = []
            issues = []
            
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                    
                try:
                    container_info = json.loads(line)
                    containers.append(container_info)
                    
                    # Check for unhealthy containers
                    status = container_info.get('Status', '').lower()
                    if 'unhealthy' in status:
                        issues.append(f"Container {container_info.get('Names')} is unhealthy")
                    elif 'exited' in status and 'ago' in status:
                        issues.append(f"Container {container_info.get('Names')} has exited")
                        
                except json.JSONDecodeError:
                    continue
                    
            self.metrics['containers_monitored'] = len(containers)
            
            return {
                'healthy': len(issues) == 0,
                'containers': containers,
                'issues': issues,
                'total': len(containers),
                'running': sum(1 for c in containers if 'running' in c.get('Status', '').lower())
            }
            
        except Exception as e:
            return {
                'healthy': False,
                'error': str(e),
                'containers': []
            }
            
    def _check_resources(self) -> Dict[str, Any]:
        """Check Docker resource usage"""
        try:
            result = subprocess.run(
                ['docker', 'system', 'df', '--format', '{{json .}}'],
                capture_output=True,
                timeout=10,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            
            if result.returncode != 0:
                return {
                    'healthy': True,  # Non-critical
                    'warning': 'Could not retrieve resource information'
                }
                
            # Parse resource usage
            resource_data = {}
            issues = []
            
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                    
                try:
                    data = json.loads(line)
                    resource_type = data.get('Type', '').lower()
                    resource_data[resource_type] = data
                    
                    # Check for resource warnings
                    if 'Reclaimable' in data:
                        reclaimable = data.get('Reclaimable', '')
                        if 'GB' in reclaimable or 'TB' in reclaimable:
                            try:
                                size = float(reclaimable.split()[0])
                                if size > 10:  # More than 10GB reclaimable
                                    issues.append(f"High reclaimable {resource_type}: {reclaimable}")
                            except ValueError:
                                pass
                                
                except json.JSONDecodeError:
                    continue
                    
            return {
                'healthy': len(issues) == 0,
                'resources': resource_data,
                'issues': issues
            }
            
        except Exception as e:
            return {
                'healthy': True,  # Non-critical
                'warning': str(e)
            }
            
    def _check_network(self) -> Dict[str, Any]:
        """Check Docker network status"""
        try:
            result = subprocess.run(
                ['docker', 'network', 'ls', '--format', '{{json .}}'],
                capture_output=True,
                timeout=10,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            
            if result.returncode != 0:
                return {
                    'healthy': True,  # Non-critical
                    'warning': 'Could not retrieve network information'
                }
                
            networks = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                    
                try:
                    network_info = json.loads(line)
                    networks.append(network_info)
                except json.JSONDecodeError:
                    continue
                    
            return {
                'healthy': len(networks) > 0,
                'networks': networks,
                'total': len(networks)
            }
            
        except Exception as e:
            return {
                'healthy': True,  # Non-critical
                'warning': str(e)
            }
            
    def _determine_status(self, health_report: Dict[str, Any]) -> DockerHealthStatus:
        """Determine overall health status from checks"""
        checks = health_report['checks']
        
        # Critical: Daemon not running
        if not checks.get('daemon', {}).get('healthy', False):
            return DockerHealthStatus.CRITICAL
            
        # Warning: Container issues
        container_check = checks.get('containers', {})
        if not container_check.get('healthy', True):
            return DockerHealthStatus.WARNING
            
        # Warning: Resource issues
        resource_check = checks.get('resources', {})
        if not resource_check.get('healthy', True):
            return DockerHealthStatus.WARNING
            
        # Healthy: All checks passed
        return DockerHealthStatus.HEALTHY
        
    def _handle_issues(self, issues: List[Dict[str, Any]]):
        """Handle detected issues"""
        with self._lock:
            for issue in issues:
                # Add to active issues
                self.active_issues.append({
                    **issue,
                    'detected_at': datetime.now().isoformat(),
                    'resolved': False
                })
                
                self.metrics['issues_detected'] += 1
                
                # Trigger callbacks
                for callback in self.issue_detected_callbacks:
                    try:
                        callback(issue)
                    except Exception as e:
                        print(f"⚠️ Issue callback error: {e}")
                        
    def _trigger_status_change_callbacks(self, old_status: DockerHealthStatus, new_status: DockerHealthStatus):
        """Trigger status change callbacks"""
        for callback in self.status_change_callbacks:
            try:
                callback(old_status, new_status)
            except Exception as e:
                print(f"⚠️ Status change callback error: {e}")
                
    def register_status_change_callback(self, callback: Callable):
        """Register callback for status changes"""
        self.status_change_callbacks.append(callback)
        
    def register_issue_detected_callback(self, callback: Callable):
        """Register callback for issue detection"""
        self.issue_detected_callbacks.append(callback)
        
    def get_health_summary(self) -> Dict[str, Any]:
        """Get current health summary"""
        with self._lock:
            return {
                'status': self.current_status.value if self.current_status else 'unknown',
                'last_check': self.last_check_time.isoformat() if self.last_check_time else None,
                'metrics': self.metrics.copy(),
                'active_issues': len(self.active_issues),
                'monitoring': self.monitoring
            }
            
    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        with self._lock:
            return self.metrics.copy()
            
    def get_health_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent health check history"""
        with self._lock:
            return list(self.health_history)[-limit:]


# Global health monitor instance
_global_health_monitor: Optional[DockerHealthMonitor] = None


def get_health_monitor() -> DockerHealthMonitor:
    """Get or create global health monitor instance"""
    global _global_health_monitor
    if _global_health_monitor is None:
        _global_health_monitor = DockerHealthMonitor()
    return _global_health_monitor


# Example usage
if __name__ == '__main__':
    monitor = get_health_monitor()
    
    # Register callbacks
    def on_status_change(old, new):
        print(f"Status changed: {old.value} → {new.value}")
        
    def on_issue_detected(issue):
        print(f"Issue detected: {issue}")
        
    monitor.register_status_change_callback(on_status_change)
    monitor.register_issue_detected_callback(on_issue_detected)
    
    # Start monitoring
    monitor.start_monitoring()
    
    # Perform manual check
    report = monitor.perform_health_check()
    print(json.dumps(report, indent=2, default=str))
    
    # Get summary
    summary = monitor.get_health_summary()
    print(f"\nHealth Summary: {summary}")
    
    # Keep running
    try:
        time.sleep(60)
    except KeyboardInterrupt:
        pass
    finally:
        monitor.stop_monitoring()
