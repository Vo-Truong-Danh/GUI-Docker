"""
Advanced Metrics & Monitoring System
Version: 1.0.0

Features:
- Real-time metrics collection
- Time-series data storage
- Aggregation (min, max, avg, percentiles)
- Alert thresholds
- Export to JSON/CSV
- Dashboard data preparation
"""

import threading
import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from collections import deque, defaultdict
import json
import statistics


@dataclass
class MetricPoint:
    """Single metric data point"""
    timestamp: float
    value: float
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class MetricStats:
    """Statistical summary of metric"""
    name: str
    count: int
    min_value: float
    max_value: float
    avg_value: float
    median_value: float
    p95_value: float
    p99_value: float
    latest_value: float
    timestamp: str


class MetricCollector:
    """Collect and store metrics with time-series support"""
    
    def __init__(self, 
                 max_points: int = 1000,
                 retention_seconds: int = 3600):
        """
        Initialize metric collector
        
        Args:
            max_points: Maximum number of points to retain per metric
            retention_seconds: How long to retain data (default 1 hour)
        """
        self.max_points = max_points
        self.retention_seconds = retention_seconds
        
        # Thread-safe storage
        self._metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_points))
        self._lock = threading.RLock()
        
        # Alert thresholds
        self._alert_thresholds: Dict[str, Dict[str, float]] = {}
        self._alert_callbacks: Dict[str, List[Callable]] = defaultdict(list)
        
        # Start cleanup thread
        self._running = True
        self._cleanup_thread = threading.Thread(
            target=self._cleanup_loop,
            daemon=True,
            name="MetricCollector-Cleanup"
        )
        self._cleanup_thread.start()
    
    def record(self, 
               metric_name: str,
               value: float,
               tags: Optional[Dict[str, str]] = None):
        """
        Record a metric value
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            tags: Optional tags for categorization
        """
        point = MetricPoint(
            timestamp=time.time(),
            value=value,
            tags=tags or {}
        )
        
        with self._lock:
            self._metrics[metric_name].append(point)
            
            # Check alert thresholds
            if metric_name in self._alert_thresholds:
                self._check_alerts(metric_name, value)
    
    def record_duration(self, metric_name: str, duration: float, **tags):
        """Record a duration metric (convenience method)"""
        self.record(f"{metric_name}.duration", duration, tags)
    
    def record_count(self, metric_name: str, count: int = 1, **tags):
        """Record a counter metric (convenience method)"""
        self.record(f"{metric_name}.count", float(count), tags)
    
    def get_latest(self, metric_name: str) -> Optional[float]:
        """Get latest value for a metric"""
        with self._lock:
            if metric_name not in self._metrics or not self._metrics[metric_name]:
                return None
            return self._metrics[metric_name][-1].value
    
    def get_history(self, 
                    metric_name: str,
                    seconds: Optional[int] = None) -> List[MetricPoint]:
        """
        Get historical data for a metric
        
        Args:
            metric_name: Metric name
            seconds: How many seconds back to retrieve (None = all)
            
        Returns:
            List of MetricPoint
        """
        with self._lock:
            if metric_name not in self._metrics:
                return []
            
            points = list(self._metrics[metric_name])
            
            if seconds is not None:
                cutoff = time.time() - seconds
                points = [p for p in points if p.timestamp >= cutoff]
            
            return points
    
    def get_stats(self, metric_name: str, seconds: Optional[int] = None) -> Optional[MetricStats]:
        """
        Get statistical summary for a metric
        
        Args:
            metric_name: Metric name
            seconds: Time window (None = all data)
            
        Returns:
            MetricStats or None if no data
        """
        points = self.get_history(metric_name, seconds)
        
        if not points:
            return None
        
        values = [p.value for p in points]
        
        return MetricStats(
            name=metric_name,
            count=len(values),
            min_value=min(values),
            max_value=max(values),
            avg_value=statistics.mean(values),
            median_value=statistics.median(values),
            p95_value=self._percentile(values, 95),
            p99_value=self._percentile(values, 99),
            latest_value=values[-1],
            timestamp=datetime.now().isoformat()
        )
    
    def _percentile(self, values: List[float], p: int) -> float:
        """Calculate percentile"""
        if not values:
            return 0.0
        sorted_values = sorted(values)
        index = int(len(sorted_values) * p / 100)
        return sorted_values[min(index, len(sorted_values) - 1)]
    
    def set_alert_threshold(self,
                           metric_name: str,
                           min_value: Optional[float] = None,
                           max_value: Optional[float] = None,
                           callback: Optional[Callable] = None):
        """
        Set alert thresholds for a metric
        
        Args:
            metric_name: Metric name
            min_value: Minimum acceptable value
            max_value: Maximum acceptable value
            callback: Function to call when threshold exceeded
        """
        with self._lock:
            self._alert_thresholds[metric_name] = {}
            
            if min_value is not None:
                self._alert_thresholds[metric_name]['min'] = min_value
            
            if max_value is not None:
                self._alert_thresholds[metric_name]['max'] = max_value
            
            if callback is not None:
                self._alert_callbacks[metric_name].append(callback)
    
    def _check_alerts(self, metric_name: str, value: float):
        """Check if value exceeds thresholds"""
        thresholds = self._alert_thresholds[metric_name]
        
        alert_triggered = False
        alert_type = None
        
        if 'min' in thresholds and value < thresholds['min']:
            alert_triggered = True
            alert_type = 'below_min'
        elif 'max' in thresholds and value > thresholds['max']:
            alert_triggered = True
            alert_type = 'above_max'
        
        if alert_triggered:
            # Call alert callbacks
            for callback in self._alert_callbacks[metric_name]:
                try:
                    callback(metric_name, value, alert_type)
                except Exception as e:
                    print(f"⚠️ Alert callback error: {e}")
    
    def _cleanup_loop(self):
        """Background thread to clean up old data"""
        while self._running:
            try:
                time.sleep(60)  # Run every minute
                
                cutoff_time = time.time() - self.retention_seconds
                removed_count = 0
                
                with self._lock:
                    for metric_name, points in self._metrics.items():
                        # Remove old points
                        while points and points[0].timestamp < cutoff_time:
                            points.popleft()
                            removed_count += 1
                
                if removed_count > 0:
                    print(f"🗑️ Cleaned up {removed_count} old metric points")
                    
            except Exception as e:
                print(f"⚠️ Metric cleanup error: {e}")
    
    def export_to_json(self, 
                       metric_names: Optional[List[str]] = None,
                       seconds: Optional[int] = None) -> str:
        """
        Export metrics to JSON
        
        Args:
            metric_names: List of metrics to export (None = all)
            seconds: Time window (None = all data)
            
        Returns:
            JSON string
        """
        with self._lock:
            if metric_names is None:
                metric_names = list(self._metrics.keys())
            
            export_data = {}
            
            for name in metric_names:
                points = self.get_history(name, seconds)
                stats = self.get_stats(name, seconds)
                
                export_data[name] = {
                    'stats': asdict(stats) if stats else None,
                    'points': [
                        {
                            'timestamp': p.timestamp,
                            'value': p.value,
                            'tags': p.tags
                        }
                        for p in points
                    ]
                }
            
            return json.dumps(export_data, indent=2)
    
    def get_all_metric_names(self) -> List[str]:
        """Get list of all metric names"""
        with self._lock:
            return list(self._metrics.keys())
    
    def clear(self, metric_name: Optional[str] = None):
        """
        Clear metrics
        
        Args:
            metric_name: Specific metric to clear (None = all)
        """
        with self._lock:
            if metric_name:
                if metric_name in self._metrics:
                    self._metrics[metric_name].clear()
            else:
                self._metrics.clear()
    
    def stop(self):
        """Stop background threads"""
        self._running = False
        if self._cleanup_thread.is_alive():
            self._cleanup_thread.join(timeout=2)


class MetricsAggregator:
    """Aggregate metrics over time windows"""
    
    def __init__(self, collector: MetricCollector):
        self.collector = collector
    
    def aggregate(self,
                  metric_name: str,
                  window_seconds: int,
                  aggregation: str = 'avg') -> List[Dict[str, Any]]:
        """
        Aggregate metric data into time windows
        
        Args:
            metric_name: Metric to aggregate
            window_seconds: Size of time window
            aggregation: Type of aggregation ('avg', 'min', 'max', 'sum')
            
        Returns:
            List of aggregated data points
        """
        points = self.collector.get_history(metric_name)
        
        if not points:
            return []
        
        # Group points into windows
        windows: Dict[int, List[float]] = defaultdict(list)
        
        for point in points:
            window_id = int(point.timestamp // window_seconds)
            windows[window_id].append(point.value)
        
        # Aggregate each window
        result = []
        
        for window_id in sorted(windows.keys()):
            values = windows[window_id]
            timestamp = window_id * window_seconds
            
            if aggregation == 'avg':
                value = statistics.mean(values)
            elif aggregation == 'min':
                value = min(values)
            elif aggregation == 'max':
                value = max(values)
            elif aggregation == 'sum':
                value = sum(values)
            else:
                raise ValueError(f"Unknown aggregation: {aggregation}")
            
            result.append({
                'timestamp': timestamp,
                'value': value,
                'count': len(values)
            })
        
        return result


# Global metric collector
_global_collector: Optional[MetricCollector] = None


def get_metrics_collector() -> MetricCollector:
    """Get or create global metrics collector"""
    global _global_collector
    
    if _global_collector is None:
        _global_collector = MetricCollector(
            max_points=10000,
            retention_seconds=3600  # 1 hour
        )
    
    return _global_collector


# Convenience decorator for timing functions
def timed_metric(metric_name: str):
    """
    Decorator to automatically record function execution time
    
    Usage:
        @timed_metric('my_function')
        def my_function():
            pass
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                collector = get_metrics_collector()
                collector.record_duration(metric_name, duration)
        return wrapper
    return decorator


# Example usage
if __name__ == '__main__':
    print("Testing Metrics System...")
    
    # Create collector
    collector = MetricCollector(max_points=100, retention_seconds=60)
    
    # Record some metrics
    for i in range(50):
        collector.record('cpu_usage', 50 + i % 50, {'host': 'server1'})
        collector.record('memory_usage', 70 + i % 30, {'host': 'server1'})
        time.sleep(0.01)
    
    # Get stats
    cpu_stats = collector.get_stats('cpu_usage')
    if cpu_stats:
        print(f"\nCPU Stats:")
        print(f"  Count: {cpu_stats.count}")
        print(f"  Min: {cpu_stats.min_value:.2f}")
        print(f"  Max: {cpu_stats.max_value:.2f}")
        print(f"  Avg: {cpu_stats.avg_value:.2f}")
        print(f"  P95: {cpu_stats.p95_value:.2f}")
        print(f"  P99: {cpu_stats.p99_value:.2f}")
    
    # Test alerts
    def alert_handler(metric, value, alert_type):
        print(f"🚨 ALERT: {metric} = {value} ({alert_type})")
    
    collector.set_alert_threshold('cpu_usage', max_value=90, callback=alert_handler)
    collector.record('cpu_usage', 95)  # Should trigger alert
    
    # Test aggregation
    aggregator = MetricsAggregator(collector)
    aggregated = aggregator.aggregate('cpu_usage', window_seconds=5, aggregation='avg')
    print(f"\nAggregated data: {len(aggregated)} windows")
    
    # Export
    json_data = collector.export_to_json(seconds=60)
    print(f"\nExported {len(json_data)} bytes of JSON")
    
    # Cleanup
    collector.stop()
    print("\n✅ Metrics system test complete")
