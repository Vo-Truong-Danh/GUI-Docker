"""
System Optimizer Module
Comprehensive system optimization and health monitoring
Version: 1.0.0
"""
import os
import sys
import gc
import psutil
import threading
import time
from typing import Dict, List, Optional, Callable
from datetime import datetime
from pathlib import Path


class SystemOptimizer:
    """Comprehensive system optimization and monitoring"""
    
    def __init__(self, logger=None):
        self.logger = logger
        self.monitoring_active = False
        self.monitor_thread = None
        self.metrics_history = []
        self.max_history = 1000
        self.optimization_stats = {
            'memory_cleanups': 0,
            'cache_clears': 0,
            'resource_releases': 0
        }
    
    def get_system_metrics(self) -> Dict:
        """Get current system metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            process = psutil.Process()
            process_memory = process.memory_info()
            
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'cpu': {
                    'percent': cpu_percent,
                    'count': psutil.cpu_count(),
                    'freq': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
                },
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'percent': memory.percent,
                    'used': memory.used,
                    'free': memory.free
                },
                'disk': {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percent': disk.percent
                },
                'process': {
                    'memory_rss': process_memory.rss,
                    'memory_vms': process_memory.vms,
                    'cpu_percent': process.cpu_percent(interval=0.1),
                    'num_threads': process.num_threads(),
                    'num_fds': process.num_fds() if hasattr(process, 'num_fds') else 0
                }
            }
            
            return metrics
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to get system metrics: {e}")
            return {}
    
    def optimize_memory(self) -> Dict:
        """Optimize memory usage"""
        try:
            before = psutil.virtual_memory().percent
            
            # Force garbage collection
            collected = gc.collect()
            
            # Clear unreferenced cycles
            gc.collect(generation=2)
            
            after = psutil.virtual_memory().percent
            
            self.optimization_stats['memory_cleanups'] += 1
            
            result = {
                'success': True,
                'objects_collected': collected,
                'memory_before': before,
                'memory_after': after,
                'improvement': before - after
            }
            
            if self.logger:
                self.logger.info(f"Memory optimization: {collected} objects collected, "
                               f"{result['improvement']:.2f}% memory freed")
            
            return result
        except Exception as e:
            if self.logger:
                self.logger.error(f"Memory optimization failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def clear_temp_files(self, temp_dirs: List[str] = None) -> Dict:
        """Clear temporary files"""
        if temp_dirs is None:
            temp_dirs = [
                'logs',
                '__pycache__',
                '.cache'
            ]
        
        cleared_count = 0
        freed_space = 0
        errors = []
        
        try:
            for temp_dir in temp_dirs:
                if not os.path.exists(temp_dir):
                    continue
                
                try:
                    for root, dirs, files in os.walk(temp_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            try:
                                size = os.path.getsize(file_path)
                                
                                # Only delete old files (>7 days)
                                mtime = os.path.getmtime(file_path)
                                age_days = (time.time() - mtime) / (24 * 3600)
                                
                                if age_days > 7:
                                    os.remove(file_path)
                                    cleared_count += 1
                                    freed_space += size
                            except Exception as e:
                                errors.append(f"{file_path}: {str(e)}")
                except Exception as e:
                    errors.append(f"{temp_dir}: {str(e)}")
            
            self.optimization_stats['cache_clears'] += 1
            
            result = {
                'success': True,
                'files_cleared': cleared_count,
                'space_freed': freed_space,
                'space_freed_mb': freed_space / (1024 * 1024),
                'errors': errors
            }
            
            if self.logger:
                self.logger.info(f"Cleared {cleared_count} temp files, "
                               f"freed {result['space_freed_mb']:.2f} MB")
            
            return result
        except Exception as e:
            if self.logger:
                self.logger.error(f"Temp file cleanup failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def check_resource_leaks(self) -> Dict:
        """Check for potential resource leaks"""
        try:
            process = psutil.Process()
            
            # Get open files
            open_files = []
            try:
                open_files = process.open_files()
            except:
                pass
            
            # Get connections
            connections = []
            try:
                connections = process.connections()
            except:
                pass
            
            # Get threads
            threads = process.threads()
            
            # Analyze for leaks
            warnings = []
            
            if len(open_files) > 100:
                warnings.append(f"High number of open files: {len(open_files)}")
            
            if len(connections) > 50:
                warnings.append(f"High number of connections: {len(connections)}")
            
            if len(threads) > 20:
                warnings.append(f"High number of threads: {len(threads)}")
            
            result = {
                'open_files': len(open_files),
                'connections': len(connections),
                'threads': len(threads),
                'warnings': warnings,
                'has_leaks': len(warnings) > 0
            }
            
            if warnings and self.logger:
                for warning in warnings:
                    self.logger.warning(f"Resource leak warning: {warning}")
            
            return result
        except Exception as e:
            if self.logger:
                self.logger.error(f"Resource leak check failed: {e}")
            return {'error': str(e)}
    
    def start_monitoring(self, interval: int = 60):
        """Start continuous system monitoring"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        
        def monitor():
            while self.monitoring_active:
                metrics = self.get_system_metrics()
                if metrics:
                    self.metrics_history.append(metrics)
                    
                    # Limit history size
                    if len(self.metrics_history) > self.max_history:
                        self.metrics_history.pop(0)
                    
                    # Auto-optimize if memory is high
                    if metrics.get('memory', {}).get('percent', 0) > 85:
                        if self.logger:
                            self.logger.warning("High memory usage detected, optimizing...")
                        self.optimize_memory()
                
                time.sleep(interval)
        
        self.monitor_thread = threading.Thread(target=monitor, daemon=True)
        self.monitor_thread.start()
        
        if self.logger:
            self.logger.info(f"System monitoring started (interval: {interval}s)")
    
    def stop_monitoring(self):
        """Stop system monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        if self.logger:
            self.logger.info("System monitoring stopped")
    
    def get_optimization_report(self) -> Dict:
        """Get comprehensive optimization report"""
        current_metrics = self.get_system_metrics()
        resource_leaks = self.check_resource_leaks()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'current_metrics': current_metrics,
            'resource_leaks': resource_leaks,
            'optimization_stats': self.optimization_stats.copy(),
            'metrics_history_size': len(self.metrics_history),
            'monitoring_active': self.monitoring_active
        }
        
        # Add recommendations
        recommendations = []
        
        if current_metrics.get('memory', {}).get('percent', 0) > 80:
            recommendations.append("High memory usage - consider optimizing or restarting")
        
        if current_metrics.get('cpu', {}).get('percent', 0) > 80:
            recommendations.append("High CPU usage - check for intensive operations")
        
        if resource_leaks.get('has_leaks'):
            recommendations.append("Potential resource leaks detected - investigate warnings")
        
        report['recommendations'] = recommendations
        
        return report
    
    def auto_optimize(self) -> Dict:
        """Run automatic optimization"""
        results = {}
        
        # Memory optimization
        results['memory'] = self.optimize_memory()
        
        # Clear temp files
        results['temp_files'] = self.clear_temp_files()
        
        # Check for leaks
        results['resource_check'] = self.check_resource_leaks()
        
        if self.logger:
            self.logger.info("Auto-optimization completed")
        
        return results


# Global instance
_system_optimizer = None


def get_system_optimizer(logger=None) -> SystemOptimizer:
    """Get or create global system optimizer"""
    global _system_optimizer
    if _system_optimizer is None:
        _system_optimizer = SystemOptimizer(logger)
    return _system_optimizer
