"""
System Health Dashboard - Real-time System Monitoring
Version: 1.0.0

Features:
- Real-time system metrics
- Resource usage monitoring
- Docker container health
- Performance analytics
- Alert system
- Historical data tracking
"""

import psutil
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import deque
from pathlib import Path
import json


@dataclass
class SystemMetrics:
    """System metrics snapshot"""
    timestamp: str
    cpu_percent: float
    memory_percent: float
    memory_used_gb: float
    memory_total_gb: float
    disk_percent: float
    disk_used_gb: float
    disk_total_gb: float
    network_sent_mb: float
    network_recv_mb: float
    process_count: int
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class ContainerMetrics:
    """Docker container metrics"""
    container_id: str
    name: str
    status: str
    cpu_percent: float
    memory_mb: float
    memory_limit_mb: float
    network_sent_kb: float
    network_recv_kb: float
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class HealthAlert:
    """Health alert"""
    timestamp: str
    severity: str  # 'info', 'warning', 'critical'
    category: str
    message: str
    value: float
    threshold: float
    
    def to_dict(self) -> Dict:
        return asdict(self)


class SystemHealthMonitor:
    """Monitor system health in real-time"""
    
    def __init__(self, history_size: int = 1000):
        self.history_size = history_size
        self.metrics_history: deque = deque(maxlen=history_size)
        self.alerts_history: deque = deque(maxlen=100)
        
        # Thresholds for alerts
        self.thresholds = {
            'cpu_warning': 70.0,
            'cpu_critical': 90.0,
            'memory_warning': 70.0,
            'memory_critical': 85.0,
            'disk_warning': 80.0,
            'disk_critical': 90.0,
        }
        
        # Monitoring state
        self.is_monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.monitor_interval = 5  # seconds
        
        # Statistics
        self.stats = {
            'uptime_seconds': 0,
            'total_samples': 0,
            'alerts_generated': 0,
            'max_cpu': 0.0,
            'max_memory': 0.0,
            'max_disk': 0.0,
        }
        
        self._lock = threading.RLock()
        self._start_time = time.time()
    
    def start_monitoring(self, interval: int = 5):
        """Start background monitoring"""
        if self.is_monitoring:
            print("⚠️ Monitoring already active")
            return
        
        self.monitor_interval = interval
        self.is_monitoring = True
        self._start_time = time.time()
        
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True,
            name="HealthMonitor"
        )
        self.monitor_thread.start()
        
        print(f"✅ Health monitoring started (interval: {interval}s)")
    
    def stop_monitoring(self):
        """Stop background monitoring"""
        if not self.is_monitoring:
            return
        
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        print("🛑 Health monitoring stopped")
    
    def _monitoring_loop(self):
        """Background monitoring loop"""
        while self.is_monitoring:
            try:
                # Collect metrics
                metrics = self.collect_metrics()
                
                # Check thresholds and generate alerts
                self._check_thresholds(metrics)
                
                # Update statistics
                self._update_statistics(metrics)
                
            except Exception as e:
                print(f"⚠️ Error in monitoring loop: {e}")
            
            time.sleep(self.monitor_interval)
    
    def collect_metrics(self) -> SystemMetrics:
        """Collect current system metrics"""
        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory
        memory = psutil.virtual_memory()
        memory_used_gb = memory.used / (1024**3)
        memory_total_gb = memory.total / (1024**3)
        
        # Disk
        disk = psutil.disk_usage('/')
        disk_used_gb = disk.used / (1024**3)
        disk_total_gb = disk.total / (1024**3)
        
        # Network
        net_io = psutil.net_io_counters()
        network_sent_mb = net_io.bytes_sent / (1024**2)
        network_recv_mb = net_io.bytes_recv / (1024**2)
        
        # Processes
        process_count = len(psutil.pids())
        
        metrics = SystemMetrics(
            timestamp=datetime.now().isoformat(),
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            memory_used_gb=round(memory_used_gb, 2),
            memory_total_gb=round(memory_total_gb, 2),
            disk_percent=disk.percent,
            disk_used_gb=round(disk_used_gb, 2),
            disk_total_gb=round(disk_total_gb, 2),
            network_sent_mb=round(network_sent_mb, 2),
            network_recv_mb=round(network_recv_mb, 2),
            process_count=process_count
        )
        
        with self._lock:
            self.metrics_history.append(metrics)
            self.stats['total_samples'] += 1
        
        return metrics
    
    def _check_thresholds(self, metrics: SystemMetrics):
        """Check metrics against thresholds and generate alerts"""
        alerts = []
        
        # CPU check
        if metrics.cpu_percent >= self.thresholds['cpu_critical']:
            alerts.append(HealthAlert(
                timestamp=metrics.timestamp,
                severity='critical',
                category='CPU',
                message=f'CPU usage critical: {metrics.cpu_percent:.1f}%',
                value=metrics.cpu_percent,
                threshold=self.thresholds['cpu_critical']
            ))
        elif metrics.cpu_percent >= self.thresholds['cpu_warning']:
            alerts.append(HealthAlert(
                timestamp=metrics.timestamp,
                severity='warning',
                category='CPU',
                message=f'CPU usage high: {metrics.cpu_percent:.1f}%',
                value=metrics.cpu_percent,
                threshold=self.thresholds['cpu_warning']
            ))
        
        # Memory check
        if metrics.memory_percent >= self.thresholds['memory_critical']:
            alerts.append(HealthAlert(
                timestamp=metrics.timestamp,
                severity='critical',
                category='Memory',
                message=f'Memory usage critical: {metrics.memory_percent:.1f}%',
                value=metrics.memory_percent,
                threshold=self.thresholds['memory_critical']
            ))
        elif metrics.memory_percent >= self.thresholds['memory_warning']:
            alerts.append(HealthAlert(
                timestamp=metrics.timestamp,
                severity='warning',
                category='Memory',
                message=f'Memory usage high: {metrics.memory_percent:.1f}%',
                value=metrics.memory_percent,
                threshold=self.thresholds['memory_warning']
            ))
        
        # Disk check
        if metrics.disk_percent >= self.thresholds['disk_critical']:
            alerts.append(HealthAlert(
                timestamp=metrics.timestamp,
                severity='critical',
                category='Disk',
                message=f'Disk usage critical: {metrics.disk_percent:.1f}%',
                value=metrics.disk_percent,
                threshold=self.thresholds['disk_critical']
            ))
        elif metrics.disk_percent >= self.thresholds['disk_warning']:
            alerts.append(HealthAlert(
                timestamp=metrics.timestamp,
                severity='warning',
                category='Disk',
                message=f'Disk usage high: {metrics.disk_percent:.1f}%',
                value=metrics.disk_percent,
                threshold=self.thresholds['disk_warning']
            ))
        
        # Store alerts
        if alerts:
            with self._lock:
                self.alerts_history.extend(alerts)
                self.stats['alerts_generated'] += len(alerts)
            
            # Print alerts
            for alert in alerts:
                severity_emoji = {
                    'info': 'ℹ️',
                    'warning': '⚠️',
                    'critical': '🔴'
                }
                print(f"{severity_emoji.get(alert.severity, '❓')} {alert.message}")
    
    def _update_statistics(self, metrics: SystemMetrics):
        """Update monitoring statistics"""
        with self._lock:
            self.stats['uptime_seconds'] = int(time.time() - self._start_time)
            self.stats['max_cpu'] = max(self.stats['max_cpu'], metrics.cpu_percent)
            self.stats['max_memory'] = max(self.stats['max_memory'], metrics.memory_percent)
            self.stats['max_disk'] = max(self.stats['max_disk'], metrics.disk_percent)
    
    def get_current_status(self) -> Dict:
        """Get current system status"""
        if not self.metrics_history:
            metrics = self.collect_metrics()
        else:
            with self._lock:
                metrics = self.metrics_history[-1]
        
        # Determine overall health
        health_score = 100.0
        health_status = "healthy"
        
        if metrics.cpu_percent > self.thresholds['cpu_warning']:
            health_score -= (metrics.cpu_percent - self.thresholds['cpu_warning']) * 0.5
        
        if metrics.memory_percent > self.thresholds['memory_warning']:
            health_score -= (metrics.memory_percent - self.thresholds['memory_warning']) * 0.5
        
        if metrics.disk_percent > self.thresholds['disk_warning']:
            health_score -= (metrics.disk_percent - self.thresholds['disk_warning']) * 0.3
        
        health_score = max(0, health_score)
        
        if health_score < 50:
            health_status = "critical"
        elif health_score < 70:
            health_status = "warning"
        elif health_score < 90:
            health_status = "degraded"
        
        return {
            'timestamp': datetime.now().isoformat(),
            'health_status': health_status,
            'health_score': round(health_score, 1),
            'metrics': metrics.to_dict(),
            'is_monitoring': self.is_monitoring,
            'uptime_seconds': self.stats['uptime_seconds']
        }
    
    def get_statistics(self) -> Dict:
        """Get monitoring statistics"""
        with self._lock:
            recent_alerts = list(self.alerts_history)[-10:]
            
            return {
                'uptime_seconds': self.stats['uptime_seconds'],
                'total_samples': self.stats['total_samples'],
                'alerts_generated': self.stats['alerts_generated'],
                'max_cpu': self.stats['max_cpu'],
                'max_memory': self.stats['max_memory'],
                'max_disk': self.stats['max_disk'],
                'recent_alerts': [alert.to_dict() for alert in recent_alerts],
                'history_size': len(self.metrics_history)
            }
    
    def get_historical_data(self, minutes: int = 10) -> List[Dict]:
        """Get historical metrics for specified time range"""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        
        with self._lock:
            filtered = [
                m.to_dict() for m in self.metrics_history
                if datetime.fromisoformat(m.timestamp) >= cutoff_time
            ]
        
        return filtered
    
    def export_report(self, filepath: str):
        """Export monitoring report to file"""
        report = {
            'generated': datetime.now().isoformat(),
            'status': self.get_current_status(),
            'statistics': self.get_statistics(),
            'thresholds': self.thresholds,
            'recent_metrics': [m.to_dict() for m in list(self.metrics_history)[-100:]]
        }
        
        path = Path(filepath)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        print(f"📊 Report exported to: {filepath}")
    
    def print_dashboard(self):
        """Print system health dashboard"""
        status = self.get_current_status()
        stats = self.get_statistics()
        metrics = status['metrics']
        
        # Status emoji
        status_emoji = {
            'healthy': '✅',
            'degraded': '⚠️',
            'warning': '⚠️',
            'critical': '🔴'
        }
        
        print("\n" + "="*80)
        print("🏥 SYSTEM HEALTH DASHBOARD")
        print("="*80)
        
        print(f"\n{status_emoji.get(status['health_status'], '❓')} Overall Health: "
              f"{status['health_status'].upper()} (Score: {status['health_score']:.1f}/100)")
        
        print(f"\n📊 Current Metrics:")
        print(f"  🖥️  CPU: {metrics['cpu_percent']:.1f}% "
              f"{'🔴' if metrics['cpu_percent'] > self.thresholds['cpu_critical'] else '🟢'}")
        print(f"  💾 Memory: {metrics['memory_percent']:.1f}% "
              f"({metrics['memory_used_gb']:.1f} / {metrics['memory_total_gb']:.1f} GB) "
              f"{'🔴' if metrics['memory_percent'] > self.thresholds['memory_critical'] else '🟢'}")
        print(f"  💿 Disk: {metrics['disk_percent']:.1f}% "
              f"({metrics['disk_used_gb']:.1f} / {metrics['disk_total_gb']:.1f} GB) "
              f"{'🔴' if metrics['disk_percent'] > self.thresholds['disk_critical'] else '🟢'}")
        print(f"  🌐 Network: ↑ {metrics['network_sent_mb']:.1f} MB  ↓ {metrics['network_recv_mb']:.1f} MB")
        print(f"  📊 Processes: {metrics['process_count']}")
        
        print(f"\n📈 Statistics:")
        print(f"  Uptime: {stats['uptime_seconds']} seconds")
        print(f"  Samples collected: {stats['total_samples']}")
        print(f"  Alerts generated: {stats['alerts_generated']}")
        print(f"  Max CPU: {stats['max_cpu']:.1f}%")
        print(f"  Max Memory: {stats['max_memory']:.1f}%")
        print(f"  Max Disk: {stats['max_disk']:.1f}%")
        
        # Recent alerts
        if stats['recent_alerts']:
            print(f"\n🚨 Recent Alerts:")
            for alert in stats['recent_alerts'][-5:]:
                severity_emoji = {
                    'info': 'ℹ️',
                    'warning': '⚠️',
                    'critical': '🔴'
                }
                print(f"  {severity_emoji.get(alert['severity'], '❓')} {alert['message']}")
        
        print("\n" + "="*80)


# Global instance
_health_monitor = None


def get_health_monitor() -> SystemHealthMonitor:
    """Get global health monitor instance"""
    global _health_monitor
    if _health_monitor is None:
        _health_monitor = SystemHealthMonitor()
    return _health_monitor


if __name__ == "__main__":
    print("Testing System Health Monitor...")
    
    monitor = SystemHealthMonitor()
    
    # Start monitoring
    monitor.start_monitoring(interval=2)
    
    try:
        # Monitor for 10 seconds
        time.sleep(10)
        
        # Print dashboard
        monitor.print_dashboard()
        
        # Export report
        monitor.export_report("health_report.json")
        
    finally:
        # Stop monitoring
        monitor.stop_monitoring()
