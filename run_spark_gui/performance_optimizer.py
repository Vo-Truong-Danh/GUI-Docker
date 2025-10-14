"""
Performance Optimizer - Intelligent Performance Analysis and Optimization
Version: 1.0.0

Features:
- Automated performance profiling
- Spark configuration optimization
- Resource usage recommendations
- Bottleneck detection
- Best practices checker
- Performance benchmarking
"""

import psutil
import platform
import subprocess
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class SystemInfo:
    """System information"""
    os: str
    cpu_count: int
    cpu_freq_mhz: float
    total_ram_gb: float
    available_ram_gb: float
    disk_total_gb: float
    disk_free_gb: float
    python_version: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'os': self.os,
            'cpu_count': self.cpu_count,
            'cpu_freq_mhz': self.cpu_freq_mhz,
            'total_ram_gb': self.total_ram_gb,
            'available_ram_gb': self.available_ram_gb,
            'disk_total_gb': self.disk_total_gb,
            'disk_free_gb': self.disk_free_gb,
            'python_version': self.python_version
        }


@dataclass
class PerformanceMetrics:
    """Performance metrics for a job"""
    job_name: str
    start_time: str
    end_time: str
    duration_seconds: float
    cpu_percent_avg: float
    memory_mb_avg: float
    disk_io_mb: float
    status: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'job_name': self.job_name,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'duration_seconds': self.duration_seconds,
            'cpu_percent_avg': self.cpu_percent_avg,
            'memory_mb_avg': self.memory_mb_avg,
            'disk_io_mb': self.disk_io_mb,
            'status': self.status
        }


class SystemAnalyzer:
    """Analyze system capabilities"""
    
    @staticmethod
    def get_system_info() -> SystemInfo:
        """Get comprehensive system information"""
        import sys
        
        # CPU info
        cpu_count = psutil.cpu_count(logical=False) or psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        cpu_freq_mhz = cpu_freq.current if cpu_freq else 0
        
        # Memory info
        mem = psutil.virtual_memory()
        total_ram_gb = mem.total / (1024 ** 3)
        available_ram_gb = mem.available / (1024 ** 3)
        
        # Disk info
        disk = psutil.disk_usage('/')
        disk_total_gb = disk.total / (1024 ** 3)
        disk_free_gb = disk.free / (1024 ** 3)
        
        return SystemInfo(
            os=f"{platform.system()} {platform.release()}",
            cpu_count=cpu_count,
            cpu_freq_mhz=cpu_freq_mhz,
            total_ram_gb=total_ram_gb,
            available_ram_gb=available_ram_gb,
            disk_total_gb=disk_total_gb,
            disk_free_gb=disk_free_gb,
            python_version=sys.version.split()[0]
        )
    
    @staticmethod
    def check_docker_resources() -> Dict[str, Any]:
        """Check Docker resource allocation"""
        try:
            # Get Docker info
            result = subprocess.run(
                ['docker', 'info', '--format', '{{json .}}'],
                capture_output=True,
                text=True,
                timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            
            if result.returncode == 0:
                import json
                docker_info = json.loads(result.stdout)
                
                return {
                    'containers_running': docker_info.get('ContainersRunning', 0),
                    'containers_total': docker_info.get('Containers', 0),
                    'images': docker_info.get('Images', 0),
                    'memory_limit': docker_info.get('MemTotal', 0) / (1024 ** 3),  # GB
                    'cpus': docker_info.get('NCPU', 0)
                }
        except Exception as e:
            print(f"⚠️ Could not get Docker info: {e}")
        
        return {
            'error': 'Could not retrieve Docker information'
        }
    
    @staticmethod
    def analyze_resource_usage() -> Dict[str, Any]:
        """Analyze current resource usage"""
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_per_core = psutil.cpu_percent(interval=1, percpu=True)
        
        # Memory usage
        mem = psutil.virtual_memory()
        
        # Disk usage
        disk = psutil.disk_usage('/')
        disk_io = psutil.disk_io_counters()
        
        # Network usage
        net_io = psutil.net_io_counters()
        
        return {
            'cpu_percent': cpu_percent,
            'cpu_per_core': cpu_per_core,
            'memory_percent': mem.percent,
            'memory_used_gb': mem.used / (1024 ** 3),
            'memory_available_gb': mem.available / (1024 ** 3),
            'disk_percent': disk.percent,
            'disk_read_mb': disk_io.read_bytes / (1024 ** 2) if disk_io else 0,
            'disk_write_mb': disk_io.write_bytes / (1024 ** 2) if disk_io else 0,
            'network_sent_mb': net_io.bytes_sent / (1024 ** 2),
            'network_recv_mb': net_io.bytes_recv / (1024 ** 2)
        }


class SparkOptimizer:
    """Optimize Spark configuration based on system resources"""
    
    @staticmethod
    def get_recommended_config(system_info: SystemInfo) -> Dict[str, Any]:
        """Generate recommended Spark configuration"""
        recommendations = {}
        
        # Executor memory (allocate 75% of available RAM, leave 25% for OS)
        executor_memory_gb = int(system_info.available_ram_gb * 0.75)
        executor_memory_gb = max(1, min(executor_memory_gb, 32))  # Between 1GB and 32GB
        
        recommendations['spark.executor.memory'] = f"{executor_memory_gb}g"
        
        # Executor cores (use all physical cores minus 1 for system)
        executor_cores = max(1, system_info.cpu_count - 1)
        recommendations['spark.executor.cores'] = str(executor_cores)
        
        # Driver memory (typically less than executor)
        driver_memory_gb = max(1, executor_memory_gb // 2)
        recommendations['spark.driver.memory'] = f"{driver_memory_gb}g"
        
        # Parallelism (2-3x number of cores)
        parallelism = executor_cores * 2
        recommendations['spark.default.parallelism'] = str(parallelism)
        recommendations['spark.sql.shuffle.partitions'] = str(parallelism)
        
        # Memory fraction
        recommendations['spark.memory.fraction'] = "0.8"
        recommendations['spark.memory.storageFraction'] = "0.3"
        
        return recommendations
    
    @staticmethod
    def check_configuration_issues(current_config: Dict[str, Any]) -> List[Tuple[str, str, str]]:
        """
        Check for configuration issues
        
        Returns:
            List of (issue_type, message, recommendation) tuples
        """
        issues = []
        system_info = SystemAnalyzer.get_system_info()
        
        # Check executor memory
        executor_mem = current_config.get('spark.executor.memory', '')
        if executor_mem:
            mem_value = int(executor_mem.rstrip('gGmM'))
            mem_unit = executor_mem[-1].lower()
            mem_gb = mem_value if mem_unit == 'g' else mem_value / 1024
            
            if mem_gb > system_info.available_ram_gb:
                issues.append((
                    'ERROR',
                    f'Executor memory ({mem_gb}GB) exceeds available RAM ({system_info.available_ram_gb:.1f}GB)',
                    f'Reduce executor memory to {int(system_info.available_ram_gb * 0.75)}g'
                ))
            elif mem_gb < 1:
                issues.append((
                    'WARNING',
                    'Executor memory is very low',
                    'Increase executor memory to at least 1g for better performance'
                ))
        
        # Check executor cores
        executor_cores = current_config.get('spark.executor.cores', '')
        if executor_cores and executor_cores.isdigit():
            cores = int(executor_cores)
            if cores > system_info.cpu_count:
                issues.append((
                    'WARNING',
                    f'Executor cores ({cores}) exceeds available CPUs ({system_info.cpu_count})',
                    f'Reduce executor cores to {system_info.cpu_count}'
                ))
        
        # Check shuffle partitions
        shuffle_partitions = current_config.get('spark.sql.shuffle.partitions', '200')
        if shuffle_partitions.isdigit():
            partitions = int(shuffle_partitions)
            if partitions < system_info.cpu_count * 2:
                issues.append((
                    'INFO',
                    f'Shuffle partitions ({partitions}) may be too low',
                    f'Consider increasing to {system_info.cpu_count * 2} for better parallelism'
                ))
            elif partitions > system_info.cpu_count * 10:
                issues.append((
                    'INFO',
                    f'Shuffle partitions ({partitions}) may be too high',
                    f'Consider reducing to {system_info.cpu_count * 3} to reduce overhead'
                ))
        
        return issues
    
    @staticmethod
    def get_performance_tips() -> List[str]:
        """Get general performance tips"""
        return [
            "💡 Use parquet format for better compression and performance",
            "💡 Partition large datasets by frequently filtered columns",
            "💡 Cache intermediate results that are reused multiple times",
            "💡 Avoid collect() on large datasets - use take() or show() instead",
            "💡 Use broadcast joins for small tables (< 10MB)",
            "💡 Persist DataFrames that are used multiple times",
            "💡 Use columnar storage formats (Parquet, ORC) instead of row-based (CSV)",
            "💡 Tune shuffle partitions based on data size (target: 128MB per partition)",
            "💡 Avoid UDFs when possible - use built-in functions instead",
            "💡 Use filter early to reduce data size before expensive operations",
            "💡 Monitor Spark UI to identify slow stages and skewed data",
            "💡 Enable dynamic allocation for variable workloads"
        ]


class PerformanceProfiler:
    """Profile job performance"""
    
    def __init__(self):
        self.metrics_history: List[PerformanceMetrics] = []
        self.monitoring_active = False
        self._start_metrics = {}
    
    def start_profiling(self, job_name: str):
        """Start profiling a job"""
        self._start_metrics = {
            'job_name': job_name,
            'start_time': datetime.now().isoformat(),
            'start_cpu': psutil.cpu_percent(interval=0.1),
            'start_memory': psutil.virtual_memory().used / (1024 ** 2),  # MB
            'start_disk_io': psutil.disk_io_counters()
        }
        self.monitoring_active = True
    
    def stop_profiling(self, status: str = 'success') -> PerformanceMetrics:
        """Stop profiling and get metrics"""
        if not self.monitoring_active or not self._start_metrics:
            raise RuntimeError("Profiling was not started")
        
        end_time = datetime.now()
        start_time = datetime.fromisoformat(self._start_metrics['start_time'])
        duration = (end_time - start_time).total_seconds()
        
        # Get end metrics
        end_cpu = psutil.cpu_percent(interval=0.1)
        end_memory = psutil.virtual_memory().used / (1024 ** 2)  # MB
        end_disk_io = psutil.disk_io_counters()
        
        # Calculate averages and differences
        cpu_avg = (self._start_metrics['start_cpu'] + end_cpu) / 2
        memory_avg = (self._start_metrics['start_memory'] + end_memory) / 2
        
        start_disk = self._start_metrics['start_disk_io']
        disk_io_mb = (
            (end_disk_io.read_bytes - start_disk.read_bytes +
             end_disk_io.write_bytes - start_disk.write_bytes) / (1024 ** 2)
        ) if start_disk and end_disk_io else 0
        
        metrics = PerformanceMetrics(
            job_name=self._start_metrics['job_name'],
            start_time=self._start_metrics['start_time'],
            end_time=end_time.isoformat(),
            duration_seconds=duration,
            cpu_percent_avg=cpu_avg,
            memory_mb_avg=memory_avg,
            disk_io_mb=disk_io_mb,
            status=status
        )
        
        self.metrics_history.append(metrics)
        self.monitoring_active = False
        self._start_metrics = {}
        
        return metrics
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of all profiled jobs"""
        if not self.metrics_history:
            return {'message': 'No profiling data available'}
        
        successful = [m for m in self.metrics_history if m.status == 'success']
        
        if not successful:
            return {'message': 'No successful jobs to analyze'}
        
        return {
            'total_jobs': len(self.metrics_history),
            'successful_jobs': len(successful),
            'avg_duration_seconds': sum(m.duration_seconds for m in successful) / len(successful),
            'avg_cpu_percent': sum(m.cpu_percent_avg for m in successful) / len(successful),
            'avg_memory_mb': sum(m.memory_mb_avg for m in successful) / len(successful),
            'total_disk_io_mb': sum(m.disk_io_mb for m in successful)
        }
    
    def generate_report(self) -> str:
        """Generate performance report"""
        report = []
        report.append("=" * 80)
        report.append("PERFORMANCE PROFILING REPORT")
        report.append("=" * 80)
        
        summary = self.get_metrics_summary()
        
        if 'message' in summary:
            report.append(f"\n{summary['message']}")
        else:
            report.append(f"\n📊 Summary:")
            report.append(f"   Total Jobs: {summary['total_jobs']}")
            report.append(f"   Successful: {summary['successful_jobs']}")
            report.append(f"   Avg Duration: {summary['avg_duration_seconds']:.2f}s")
            report.append(f"   Avg CPU: {summary['avg_cpu_percent']:.1f}%")
            report.append(f"   Avg Memory: {summary['avg_memory_mb']:.1f} MB")
            report.append(f"   Total Disk I/O: {summary['total_disk_io_mb']:.1f} MB")
            
            # Recent jobs
            report.append(f"\n🕒 Recent Jobs:")
            for metrics in self.metrics_history[-5:]:
                report.append(
                    f"   {metrics.job_name}: {metrics.duration_seconds:.2f}s "
                    f"(CPU: {metrics.cpu_percent_avg:.1f}%, "
                    f"Memory: {metrics.memory_mb_avg:.1f}MB) "
                    f"[{metrics.status}]"
                )
        
        report.append("\n" + "=" * 80)
        return "\n".join(report)


class PerformanceOptimizer:
    """Main performance optimizer class"""
    
    def __init__(self):
        self.system_analyzer = SystemAnalyzer()
        self.spark_optimizer = SparkOptimizer()
        self.profiler = PerformanceProfiler()
    
    def analyze_system(self) -> str:
        """Analyze system and provide recommendations"""
        system_info = self.system_analyzer.get_system_info()
        resource_usage = self.system_analyzer.analyze_resource_usage()
        docker_resources = self.system_analyzer.check_docker_resources()
        
        report = []
        report.append("=" * 80)
        report.append("SYSTEM ANALYSIS REPORT")
        report.append("=" * 80)
        
        # System info
        report.append(f"\n💻 System Information:")
        report.append(f"   OS: {system_info.os}")
        report.append(f"   CPUs: {system_info.cpu_count} @ {system_info.cpu_freq_mhz:.0f} MHz")
        report.append(f"   RAM: {system_info.total_ram_gb:.1f} GB (Available: {system_info.available_ram_gb:.1f} GB)")
        report.append(f"   Disk: {system_info.disk_total_gb:.1f} GB (Free: {system_info.disk_free_gb:.1f} GB)")
        report.append(f"   Python: {system_info.python_version}")
        
        # Current usage
        report.append(f"\n📊 Current Resource Usage:")
        report.append(f"   CPU: {resource_usage['cpu_percent']:.1f}%")
        report.append(f"   Memory: {resource_usage['memory_percent']:.1f}% ({resource_usage['memory_used_gb']:.1f} GB)")
        report.append(f"   Disk: {resource_usage['disk_percent']:.1f}%")
        
        # Docker resources
        if 'error' not in docker_resources:
            report.append(f"\n🐳 Docker Resources:")
            report.append(f"   Containers: {docker_resources['containers_running']}/{docker_resources['containers_total']}")
            report.append(f"   Images: {docker_resources['images']}")
            if docker_resources.get('memory_limit'):
                report.append(f"   Memory Limit: {docker_resources['memory_limit']:.1f} GB")
            if docker_resources.get('cpus'):
                report.append(f"   CPUs: {docker_resources['cpus']}")
        
        # Recommended Spark config
        recommended_config = self.spark_optimizer.get_recommended_config(system_info)
        report.append(f"\n⚙️ Recommended Spark Configuration:")
        for key, value in recommended_config.items():
            report.append(f"   {key}: {value}")
        
        # Performance tips
        report.append(f"\n💡 Performance Tips:")
        tips = self.spark_optimizer.get_performance_tips()
        for tip in tips[:5]:  # Show first 5 tips
            report.append(f"   {tip}")
        
        report.append("\n" + "=" * 80)
        return "\n".join(report)
    
    def check_config(self, config: Dict[str, Any]) -> str:
        """Check configuration and identify issues"""
        issues = self.spark_optimizer.check_configuration_issues(config)
        
        if not issues:
            return "✅ No configuration issues found!"
        
        report = []
        report.append("⚠️ Configuration Issues Found:")
        report.append("")
        
        for issue_type, message, recommendation in issues:
            emoji = {'ERROR': '❌', 'WARNING': '⚠️', 'INFO': '💡'}
            report.append(f"{emoji.get(issue_type, '•')} [{issue_type}] {message}")
            report.append(f"   → {recommendation}")
            report.append("")
        
        return "\n".join(report)


# Global optimizer instance
_optimizer = None


def get_optimizer() -> PerformanceOptimizer:
    """Get global optimizer instance"""
    global _optimizer
    if _optimizer is None:
        _optimizer = PerformanceOptimizer()
    return _optimizer


if __name__ == "__main__":
    print("Testing Performance Optimizer...")
    
    optimizer = get_optimizer()
    
    # Analyze system
    print(optimizer.analyze_system())
    
    # Test profiler
    print("\n=== Testing Profiler ===")
    optimizer.profiler.start_profiling("Test Job")
    
    # Simulate work
    import time
    time.sleep(2)
    
    metrics = optimizer.profiler.stop_profiling()
    print(f"Job completed in {metrics.duration_seconds:.2f}s")
    print(f"Avg CPU: {metrics.cpu_percent_avg:.1f}%")
    print(f"Avg Memory: {metrics.memory_mb_avg:.1f} MB")
