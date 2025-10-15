"""
System Health Check Module
Version: 5.0.0
Features:
- Docker daemon health check
- Container health monitoring
- HDFS connectivity check
- Network diagnostics
- Resource availability check
"""

import subprocess

# Import subprocess utilities for hidden console windows
try:
    from subprocess_utils import run_hidden, popen_hidden
except ImportError:
    # Safe fallbacks to avoid recursive calls when subprocess_utils is unavailable
    import subprocess as _subprocess
    import sys as _sys

    def _get_subprocess_params():
        params = {}
        if _sys.platform == 'win32':
            startupinfo = _subprocess.STARTUPINFO()
            startupinfo.dwFlags |= _subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = 0  # SW_HIDE
            params['startupinfo'] = startupinfo
            if hasattr(_subprocess, 'CREATE_NO_WINDOW'):
                params['creationflags'] = _subprocess.CREATE_NO_WINDOW
        return params

    def run_hidden(*args, **kwargs):
        params = _get_subprocess_params()
        kwargs.update(params)
        return _subprocess.run(*args, **kwargs)

    def popen_hidden(*args, **kwargs):
        params = _get_subprocess_params()
        kwargs.update(params)
        return _subprocess.Popen(*args, **kwargs)
import time
import socket
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
from pathlib import Path
import threading
import json


class HealthStatus:
    """Health status enumeration"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class HealthCheckResult:
    """Result of a health check"""
    
    def __init__(
        self,
        component: str,
        status: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None
    ):
        self.component = component
        self.status = status
        self.message = message
        self.details = details or {}
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'component': self.component,
            'status': self.status,
            'message': self.message,
            'details': self.details,
            'timestamp': self.timestamp.isoformat()
        }
    
    def __str__(self) -> str:
        emoji = {
            HealthStatus.HEALTHY: "✅",
            HealthStatus.DEGRADED: "⚠️",
            HealthStatus.UNHEALTHY: "❌",
            HealthStatus.UNKNOWN: "❓"
        }
        return f"{emoji.get(self.status, '❓')} {self.component}: {self.message}"


class HealthChecker:
    """Comprehensive health checker for the system"""
    
    def __init__(self):
        self.results: Dict[str, HealthCheckResult] = {}
        self.lock = threading.Lock()
    
    def check_docker_daemon(self, timeout: int = 5) -> HealthCheckResult:
        """
        Check if Docker daemon is running and responsive
        
        Args:
            timeout: Timeout in seconds
        
        Returns:
            HealthCheckResult
        """
        try:
            start_time = time.time()
            result = run_hidden(
                ['docker', 'info'],
                capture_output=True,
                timeout=timeout,
                text=True
            )
            elapsed = time.time() - start_time
            
            if result.returncode == 0:
                # Parse docker info
                info_lines = result.stdout.split('\n')
                containers = None
                running = None
                
                for line in info_lines:
                    if 'Containers:' in line:
                        containers = line.split(':')[1].strip()
                    elif 'Running:' in line:
                        running = line.split(':')[1].strip()
                
                return HealthCheckResult(
                    component='Docker Daemon',
                    status=HealthStatus.HEALTHY,
                    message='Docker is running and responsive',
                    details={
                        'response_time_ms': round(elapsed * 1000, 2),
                        'total_containers': containers,
                        'running_containers': running
                    }
                )
            else:
                return HealthCheckResult(
                    component='Docker Daemon',
                    status=HealthStatus.UNHEALTHY,
                    message='Docker command failed',
                    details={'error': result.stderr}
                )
        
        except subprocess.TimeoutExpired:
            return HealthCheckResult(
                component='Docker Daemon',
                status=HealthStatus.UNHEALTHY,
                message=f'Docker daemon not responding (timeout after {timeout}s)',
                details={'timeout': timeout}
            )
        
        except FileNotFoundError:
            return HealthCheckResult(
                component='Docker Daemon',
                status=HealthStatus.UNHEALTHY,
                message='Docker is not installed or not in PATH',
                details={'suggestion': 'Install Docker Desktop'}
            )
        
        except Exception as e:
            return HealthCheckResult(
                component='Docker Daemon',
                status=HealthStatus.UNKNOWN,
                message=f'Unexpected error: {str(e)}',
                details={'exception': type(e).__name__}
            )
    
    def check_container(self, container_name: str, timeout: int = 5) -> HealthCheckResult:
        """
        Check if a specific container is running and healthy
        
        Args:
            container_name: Name of container to check
            timeout: Timeout in seconds
        
        Returns:
            HealthCheckResult
        """
        try:
            # Check if container exists
            result = run_hidden(
                ['docker', 'inspect', container_name],
                capture_output=True,
                timeout=timeout,
                text=True
            )
            
            if result.returncode != 0:
                return HealthCheckResult(
                    component=f'Container: {container_name}',
                    status=HealthStatus.UNHEALTHY,
                    message='Container does not exist',
                    details={'container': container_name}
                )
            
            # Parse container state
            import json
            info = json.loads(result.stdout)[0]
            state = info.get('State', {})
            
            is_running = state.get('Running', False)
            status_str = state.get('Status', 'unknown')
            
            if is_running:
                # Check health if available
                health = state.get('Health', {})
                health_status = health.get('Status', 'none')
                
                if health_status == 'healthy':
                    status = HealthStatus.HEALTHY
                    message = 'Container is running and healthy'
                elif health_status == 'unhealthy':
                    status = HealthStatus.UNHEALTHY
                    message = 'Container is running but unhealthy'
                else:
                    status = HealthStatus.HEALTHY
                    message = 'Container is running (no health check configured)'
                
                return HealthCheckResult(
                    component=f'Container: {container_name}',
                    status=status,
                    message=message,
                    details={
                        'state': status_str,
                        'health_status': health_status,
                        'started_at': state.get('StartedAt', 'unknown')
                    }
                )
            else:
                return HealthCheckResult(
                    component=f'Container: {container_name}',
                    status=HealthStatus.UNHEALTHY,
                    message=f'Container is not running (status: {status_str})',
                    details={'state': status_str}
                )
        
        except subprocess.TimeoutExpired:
            return HealthCheckResult(
                component=f'Container: {container_name}',
                status=HealthStatus.UNKNOWN,
                message='Timeout checking container',
                details={'timeout': timeout}
            )
        
        except Exception as e:
            return HealthCheckResult(
                component=f'Container: {container_name}',
                status=HealthStatus.UNKNOWN,
                message=f'Error checking container: {str(e)}',
                details={'exception': type(e).__name__}
            )
    
    def check_hdfs_connectivity(
        self,
        container: str,
        hdfs_path: str = '/',
        timeout: int = 10
    ) -> HealthCheckResult:
        """
        Check HDFS connectivity through container
        
        Args:
            container: Container with HDFS client
            hdfs_path: HDFS path to test
            timeout: Timeout in seconds
        
        Returns:
            HealthCheckResult
        """
        try:
            # Test HDFS with simple ls command
            result = run_hidden(
                ['docker', 'exec', container, 'hdfs', 'dfs', '-ls', hdfs_path],
                capture_output=True,
                timeout=timeout,
                text=True
            )
            
            if result.returncode == 0:
                # Count files/directories
                lines = [l for l in result.stdout.split('\n') if l.strip() and not l.startswith('Found')]
                
                return HealthCheckResult(
                    component='HDFS',
                    status=HealthStatus.HEALTHY,
                    message='HDFS is accessible',
                    details={
                        'container': container,
                        'test_path': hdfs_path,
                        'entries_found': len(lines)
                    }
                )
            else:
                error = result.stderr.strip()
                
                # Determine if it's a connection issue or path issue
                if 'Connection refused' in error or 'could not be reached' in error:
                    status = HealthStatus.UNHEALTHY
                    message = 'Cannot connect to HDFS'
                elif 'No such file or directory' in error:
                    status = HealthStatus.HEALTHY
                    message = 'HDFS is accessible (test path does not exist)'
                else:
                    status = HealthStatus.DEGRADED
                    message = 'HDFS check failed'
                
                return HealthCheckResult(
                    component='HDFS',
                    status=status,
                    message=message,
                    details={'error': error, 'container': container}
                )
        
        except subprocess.TimeoutExpired:
            return HealthCheckResult(
                component='HDFS',
                status=HealthStatus.UNHEALTHY,
                message=f'HDFS not responding (timeout after {timeout}s)',
                details={'timeout': timeout, 'container': container}
            )
        
        except Exception as e:
            return HealthCheckResult(
                component='HDFS',
                status=HealthStatus.UNKNOWN,
                message=f'Error checking HDFS: {str(e)}',
                details={'exception': type(e).__name__}
            )
    
    def check_network_connectivity(
        self,
        host: str,
        port: int,
        timeout: int = 5
    ) -> HealthCheckResult:
        """
        Check network connectivity to a host:port
        
        Args:
            host: Hostname or IP
            port: Port number
            timeout: Timeout in seconds
        
        Returns:
            HealthCheckResult
        """
        try:
            start_time = time.time()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            
            result = sock.connect_ex((host, port))
            elapsed = time.time() - start_time
            sock.close()
            
            if result == 0:
                return HealthCheckResult(
                    component=f'Network: {host}:{port}',
                    status=HealthStatus.HEALTHY,
                    message='Port is reachable',
                    details={
                        'host': host,
                        'port': port,
                        'response_time_ms': round(elapsed * 1000, 2)
                    }
                )
            else:
                return HealthCheckResult(
                    component=f'Network: {host}:{port}',
                    status=HealthStatus.UNHEALTHY,
                    message='Port is not reachable',
                    details={
                        'host': host,
                        'port': port,
                        'error_code': result
                    }
                )
        
        except socket.timeout:
            return HealthCheckResult(
                component=f'Network: {host}:{port}',
                status=HealthStatus.UNHEALTHY,
                message=f'Connection timeout after {timeout}s',
                details={'host': host, 'port': port, 'timeout': timeout}
            )
        
        except Exception as e:
            return HealthCheckResult(
                component=f'Network: {host}:{port}',
                status=HealthStatus.UNKNOWN,
                message=f'Error: {str(e)}',
                details={'exception': type(e).__name__}
            )
    
    def check_docker_compose_file(self, compose_file: str) -> HealthCheckResult:
        """
        Check if docker-compose file is valid
        
        Args:
            compose_file: Path to docker-compose.yml
        
        Returns:
            HealthCheckResult
        """
        try:
            compose_path = Path(compose_file)
            
            if not compose_path.exists():
                return HealthCheckResult(
                    component='Docker Compose File',
                    status=HealthStatus.UNHEALTHY,
                    message='File does not exist',
                    details={'path': compose_file}
                )
            
            if not compose_path.is_file():
                return HealthCheckResult(
                    component='Docker Compose File',
                    status=HealthStatus.UNHEALTHY,
                    message='Path is not a file',
                    details={'path': compose_file}
                )
            
            # Try to validate with docker-compose
            result = run_hidden(
                ['docker-compose', '-f', compose_file, 'config'],
                capture_output=True,
                timeout=10,
                text=True
            )
            
            if result.returncode == 0:
                return HealthCheckResult(
                    component='Docker Compose File',
                    status=HealthStatus.HEALTHY,
                    message='File is valid',
                    details={'path': compose_file, 'size_bytes': compose_path.stat().st_size}
                )
            else:
                return HealthCheckResult(
                    component='Docker Compose File',
                    status=HealthStatus.UNHEALTHY,
                    message='File has syntax errors',
                    details={'path': compose_file, 'error': result.stderr}
                )
        
        except FileNotFoundError:
            return HealthCheckResult(
                component='Docker Compose File',
                status=HealthStatus.DEGRADED,
                message='docker-compose command not found (file exists but cannot validate)',
                details={'path': compose_file}
            )
        
        except Exception as e:
            return HealthCheckResult(
                component='Docker Compose File',
                status=HealthStatus.UNKNOWN,
                message=f'Error: {str(e)}',
                details={'exception': type(e).__name__}
            )
    
    def run_all_checks(self, config: dict) -> Dict[str, HealthCheckResult]:
        """
        Run all health checks based on configuration
        
        Args:
            config: Application configuration dictionary
        
        Returns:
            Dictionary of component name to HealthCheckResult
        """
        with self.lock:
            self.results.clear()
            
            # Check Docker daemon
            self.results['docker_daemon'] = self.check_docker_daemon()
            
            # Only continue if Docker is healthy
            if self.results['docker_daemon'].status == HealthStatus.HEALTHY:
                # Check containers
                if 'container' in config:
                    self.results['spark_container'] = self.check_container(config['container'])
                
                if 'hdfs_container' in config:
                    self.results['hdfs_container'] = self.check_container(config['hdfs_container'])
                    
                    # Check HDFS connectivity if container is healthy
                    if (self.results['hdfs_container'].status == HealthStatus.HEALTHY and
                        'hdfs_default_path' in config):
                        self.results['hdfs'] = self.check_hdfs_connectivity(
                            config['hdfs_container'],
                            config.get('hdfs_default_path', '/')
                        )
            
            # Check docker-compose file
            if 'compose_file' in config:
                self.results['compose_file'] = self.check_docker_compose_file(config['compose_file'])
            
            return self.results.copy()
    
    def get_overall_health(self) -> Tuple[str, str]:
        """
        Get overall system health status
        
        Returns:
            Tuple of (status, summary_message)
        """
        with self.lock:
            if not self.results:
                return HealthStatus.UNKNOWN, "No health checks have been run"
            
            statuses = [r.status for r in self.results.values()]
            
            if all(s == HealthStatus.HEALTHY for s in statuses):
                return HealthStatus.HEALTHY, "All systems operational"
            elif any(s == HealthStatus.UNHEALTHY for s in statuses):
                unhealthy_count = sum(1 for s in statuses if s == HealthStatus.UNHEALTHY)
                return HealthStatus.UNHEALTHY, f"{unhealthy_count} critical issue(s) detected"
            elif any(s == HealthStatus.DEGRADED for s in statuses):
                degraded_count = sum(1 for s in statuses if s == HealthStatus.DEGRADED)
                return HealthStatus.DEGRADED, f"{degraded_count} component(s) degraded"
            else:
                return HealthStatus.UNKNOWN, "System health unknown"
    
    def export_results(self, filepath: str):
        """Export health check results to JSON file"""
        with self.lock:
            data = {
                'timestamp': datetime.now().isoformat(),
                'overall_status': self.get_overall_health()[0],
                'results': {k: v.to_dict() for k, v in self.results.items()}
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)


# Global health checker instance
health_checker = HealthChecker()


# Example usage
if __name__ == '__main__':
    print("=" * 80)
    print("HEALTH CHECK SYSTEM TESTS")
    print("=" * 80)
    
    # Test Docker daemon
    print("\n1. Checking Docker Daemon...")
    result = health_checker.check_docker_daemon()
    print(f"   {result}")
    
    # Test container (example)
    print("\n2. Checking Container...")
    result = health_checker.check_container('spark-master')
    print(f"   {result}")
    
    # Test network connectivity
    print("\n3. Checking Network Connectivity...")
    result = health_checker.check_network_connectivity('localhost', 8080)
    print(f"   {result}")
    
    # Run all checks with example config
    print("\n4. Running All Health Checks...")
    test_config = {
        'container': 'spark-worker',
        'hdfs_container': 'namenode',
        'hdfs_default_path': '/',
        'compose_file': 'docker-compose.yml'
    }
    
    results = health_checker.run_all_checks(test_config)
    for component, result in results.items():
        print(f"   {result}")
    
    # Overall health
    status, message = health_checker.get_overall_health()
    print(f"\n📊 Overall Health: {status} - {message}")
    
    # Export results
    print("\n5. Exporting Results...")
    health_checker.export_results('health_check_results.json')
    print("   ✅ Results exported to health_check_results.json")
    
    print("\n" + "=" * 80)
    print("✅ All health check tests completed!")
    print("=" * 80)
