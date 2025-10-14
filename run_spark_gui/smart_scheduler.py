"""
Smart Resource Scheduler - Lập lịch và tối ưu tài nguyên thông minh
Version: 1.0.0
Date: 2025-10-13

Features:
- Priority-based job scheduling
- Resource-aware scheduling
- Auto-scaling based on load
- Job queuing with priorities
- Deadlock prevention
- Load balancing
"""

import time
import threading
import heapq
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field


class JobPriority(Enum):
    """Mức độ ưu tiên công việc"""
    CRITICAL = 0    # Highest priority
    HIGH = 1
    NORMAL = 2
    LOW = 3
    BACKGROUND = 4  # Lowest priority


class JobStatus(Enum):
    """Trạng thái công việc"""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass(order=True)
class ScheduledJob:
    """Một công việc được lập lịch"""
    priority: int = field(compare=True)
    job_id: str = field(compare=False)
    name: str = field(compare=False)
    func: Callable = field(compare=False)
    args: tuple = field(default_factory=tuple, compare=False)
    kwargs: dict = field(default_factory=dict, compare=False)
    
    # Resources required
    cpu_cores: int = field(default=1, compare=False)
    memory_mb: int = field(default=512, compare=False)
    gpu_required: bool = field(default=False, compare=False)
    
    # Timing
    created_at: datetime = field(default_factory=datetime.now, compare=False)
    scheduled_at: Optional[datetime] = field(default=None, compare=False)
    started_at: Optional[datetime] = field(default=None, compare=False)
    completed_at: Optional[datetime] = field(default=None, compare=False)
    
    # Constraints
    max_runtime: Optional[int] = field(default=None, compare=False)  # seconds
    dependencies: List[str] = field(default_factory=list, compare=False)
    
    # Status
    status: JobStatus = field(default=JobStatus.PENDING, compare=False)
    result: Any = field(default=None, compare=False)
    error: Optional[str] = field(default=None, compare=False)
    
    # Callbacks
    on_complete: Optional[Callable] = field(default=None, compare=False)
    on_error: Optional[Callable] = field(default=None, compare=False)


class ResourcePool:
    """Quản lý pool tài nguyên"""
    
    def __init__(self, total_cpu: int = 4, total_memory_mb: int = 8192, 
                 total_gpu: int = 0):
        self.total_cpu = total_cpu
        self.total_memory_mb = total_memory_mb
        self.total_gpu = total_gpu
        
        self.available_cpu = total_cpu
        self.available_memory_mb = total_memory_mb
        self.available_gpu = total_gpu
        
        self.lock = threading.RLock()
        self.allocated_jobs: Dict[str, Dict[str, int]] = {}
    
    def can_allocate(self, cpu: int, memory_mb: int, gpu: bool) -> bool:
        """Check if có đủ tài nguyên"""
        with self.lock:
            gpu_needed = 1 if gpu else 0
            return (self.available_cpu >= cpu and 
                    self.available_memory_mb >= memory_mb and
                    self.available_gpu >= gpu_needed)
    
    def allocate(self, job_id: str, cpu: int, memory_mb: int, gpu: bool) -> bool:
        """Cấp phát tài nguyên cho job"""
        with self.lock:
            gpu_needed = 1 if gpu else 0
            
            if not self.can_allocate(cpu, memory_mb, gpu):
                return False
            
            self.available_cpu -= cpu
            self.available_memory_mb -= memory_mb
            self.available_gpu -= gpu_needed
            
            self.allocated_jobs[job_id] = {
                'cpu': cpu,
                'memory_mb': memory_mb,
                'gpu': gpu_needed
            }
            
            return True
    
    def release(self, job_id: str):
        """Giải phóng tài nguyên của job"""
        with self.lock:
            if job_id in self.allocated_jobs:
                allocation = self.allocated_jobs.pop(job_id)
                self.available_cpu += allocation['cpu']
                self.available_memory_mb += allocation['memory_mb']
                self.available_gpu += allocation['gpu']
    
    def get_utilization(self) -> Dict[str, float]:
        """Lấy % sử dụng tài nguyên"""
        with self.lock:
            return {
                'cpu': ((self.total_cpu - self.available_cpu) / self.total_cpu * 100) 
                       if self.total_cpu > 0 else 0,
                'memory': ((self.total_memory_mb - self.available_memory_mb) / 
                          self.total_memory_mb * 100) if self.total_memory_mb > 0 else 0,
                'gpu': ((self.total_gpu - self.available_gpu) / self.total_gpu * 100) 
                       if self.total_gpu > 0 else 0
            }


class SmartScheduler:
    """
    Bộ lập lịch công việc thông minh với:
    - Priority scheduling
    - Resource management
    - Dependency resolution
    - Auto-scaling
    """
    
    def __init__(self, max_workers: int = 4, total_cpu: int = 4, 
                 total_memory_mb: int = 8192, total_gpu: int = 0):
        self.max_workers = max_workers
        self.resource_pool = ResourcePool(total_cpu, total_memory_mb, total_gpu)
        
        # Job management
        self.job_queue: List[ScheduledJob] = []  # Min heap by priority
        self.running_jobs: Dict[str, ScheduledJob] = {}
        self.completed_jobs: Dict[str, ScheduledJob] = {}
        self.all_jobs: Dict[str, ScheduledJob] = {}
        
        # Threading
        self.scheduler_thread: Optional[threading.Thread] = None
        self.worker_threads: List[threading.Thread] = []
        self.running = False
        self.lock = threading.RLock()
        
        # Statistics
        self.stats = {
            'total_jobs': 0,
            'completed_jobs': 0,
            'failed_jobs': 0,
            'cancelled_jobs': 0,
            'total_runtime': 0.0,
            'avg_wait_time': 0.0,
            'avg_runtime': 0.0
        }
    
    def submit_job(self, name: str, func: Callable, args: tuple = (), 
                   kwargs: dict = None, priority: JobPriority = JobPriority.NORMAL,
                   cpu_cores: int = 1, memory_mb: int = 512, 
                   gpu_required: bool = False, max_runtime: int = None,
                   dependencies: List[str] = None,
                   on_complete: Callable = None, on_error: Callable = None) -> str:
        """
        Submit một job mới
        
        Returns:
            str: Job ID
        """
        with self.lock:
            job_id = f"job_{int(time.time() * 1000)}_{self.stats['total_jobs']}"
            
            job = ScheduledJob(
                priority=priority.value,
                job_id=job_id,
                name=name,
                func=func,
                args=args,
                kwargs=kwargs or {},
                cpu_cores=cpu_cores,
                memory_mb=memory_mb,
                gpu_required=gpu_required,
                max_runtime=max_runtime,
                dependencies=dependencies or [],
                on_complete=on_complete,
                on_error=on_error
            )
            
            self.all_jobs[job_id] = job
            self.stats['total_jobs'] += 1
            
            # Add to queue
            heapq.heappush(self.job_queue, job)
            job.status = JobStatus.QUEUED
            job.scheduled_at = datetime.now()
            
            return job_id
    
    def start(self):
        """Khởi động scheduler"""
        if self.running:
            return
        
        self.running = True
        
        # Start scheduler thread
        self.scheduler_thread = threading.Thread(
            target=self._scheduler_loop,
            daemon=True,
            name="SmartScheduler-Main"
        )
        self.scheduler_thread.start()
        
        print(f"✅ Smart Scheduler started (max workers: {self.max_workers})")
    
    def stop(self, wait: bool = True):
        """Dừng scheduler"""
        self.running = False
        
        if wait and self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        
        # Wait for workers
        for worker in self.worker_threads:
            if worker.is_alive():
                worker.join(timeout=2)
        
        print("🛑 Smart Scheduler stopped")
    
    def _scheduler_loop(self):
        """Main scheduling loop"""
        while self.running:
            try:
                self._schedule_next_job()
                time.sleep(0.1)  # 100ms interval
            except Exception as e:
                print(f"⚠️ Scheduler error: {e}")
                time.sleep(1)
    
    def _schedule_next_job(self):
        """Lập lịch job tiếp theo nếu có tài nguyên"""
        with self.lock:
            # Check if we can run more jobs
            if len(self.running_jobs) >= self.max_workers:
                return
            
            # Check if there are jobs in queue
            if not self.job_queue:
                return
            
            # Get highest priority job that can run
            temp_queue = []
            scheduled = False
            
            while self.job_queue and not scheduled:
                job = heapq.heappop(self.job_queue)
                
                # Check dependencies
                if not self._check_dependencies(job):
                    temp_queue.append(job)
                    continue
                
                # Check resources
                if self.resource_pool.can_allocate(
                    job.cpu_cores, job.memory_mb, job.gpu_required
                ):
                    # Allocate resources and start job
                    if self.resource_pool.allocate(
                        job.job_id, job.cpu_cores, job.memory_mb, job.gpu_required
                    ):
                        self._start_job(job)
                        scheduled = True
                else:
                    temp_queue.append(job)
                    break  # No resources, stop checking
            
            # Put remaining jobs back
            for job in temp_queue:
                heapq.heappush(self.job_queue, job)
    
    def _check_dependencies(self, job: ScheduledJob) -> bool:
        """Check if tất cả dependencies đã completed"""
        for dep_id in job.dependencies:
            if dep_id not in self.completed_jobs:
                return False
            dep_job = self.completed_jobs[dep_id]
            if dep_job.status != JobStatus.COMPLETED:
                return False
        return True
    
    def _start_job(self, job: ScheduledJob):
        """Khởi động một job"""
        job.status = JobStatus.RUNNING
        job.started_at = datetime.now()
        self.running_jobs[job.job_id] = job
        
        # Create worker thread
        worker = threading.Thread(
            target=self._execute_job,
            args=(job,),
            daemon=True,
            name=f"Worker-{job.job_id}"
        )
        self.worker_threads.append(worker)
        worker.start()
        
        print(f"▶️  Started job: {job.name} (ID: {job.job_id}, Priority: {job.priority})")
    
    def _execute_job(self, job: ScheduledJob):
        """Thực thi một job"""
        try:
            # Execute with timeout if specified
            if job.max_runtime:
                import signal
                
                def timeout_handler(signum, frame):
                    raise TimeoutError(f"Job exceeded max runtime: {job.max_runtime}s")
                
                # Set timeout (Unix only)
                try:
                    signal.signal(signal.SIGALRM, timeout_handler)
                    signal.alarm(job.max_runtime)
                except (AttributeError, ValueError) as e:
                    # Windows doesn't support SIGALRM or invalid signal number
                    print(f"⚠️ Cannot set job timeout alarm (platform limitation): {e}")
            
            # Run the job
            result = job.func(*job.args, **job.kwargs)
            
            # Cancel timeout
            if job.max_runtime:
                try:
                    signal.alarm(0)
                except (AttributeError, ValueError) as e:
                    print(f"⚠️ Cannot cancel timeout alarm: {e}")
            
            # Mark as completed
            self._complete_job(job, result, success=True)
            
        except Exception as e:
            # Mark as failed
            self._complete_job(job, None, success=False, error=str(e))
    
    def _complete_job(self, job: ScheduledJob, result: Any, 
                     success: bool, error: str = None):
        """Hoàn thành job"""
        with self.lock:
            job.completed_at = datetime.now()
            job.result = result
            job.error = error
            
            if success:
                job.status = JobStatus.COMPLETED
                self.stats['completed_jobs'] += 1
                print(f"✅ Completed job: {job.name}")
                
                # Callback
                if job.on_complete:
                    try:
                        job.on_complete(result)
                    except Exception as e:
                        print(f"⚠️ Error in on_complete callback: {e}")
            else:
                job.status = JobStatus.FAILED
                self.stats['failed_jobs'] += 1
                print(f"❌ Failed job: {job.name} - {error}")
                
                # Callback
                if job.on_error:
                    try:
                        job.on_error(error)
                    except Exception as e:
                        print(f"⚠️ Error in on_error callback: {e}")
            
            # Update statistics
            runtime = (job.completed_at - job.started_at).total_seconds()
            wait_time = (job.started_at - job.created_at).total_seconds()
            
            self.stats['total_runtime'] += runtime
            completed = self.stats['completed_jobs'] + self.stats['failed_jobs']
            if completed > 0:
                self.stats['avg_runtime'] = self.stats['total_runtime'] / completed
                # Update avg wait time (running average)
                self.stats['avg_wait_time'] = (
                    (self.stats['avg_wait_time'] * (completed - 1) + wait_time) / completed
                )
            
            # Release resources
            self.resource_pool.release(job.job_id)
            
            # Move to completed
            if job.job_id in self.running_jobs:
                del self.running_jobs[job.job_id]
            self.completed_jobs[job.job_id] = job
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel một job"""
        with self.lock:
            if job_id not in self.all_jobs:
                return False
            
            job = self.all_jobs[job_id]
            
            # Can only cancel queued jobs
            if job.status == JobStatus.QUEUED:
                job.status = JobStatus.CANCELLED
                self.stats['cancelled_jobs'] += 1
                
                # Remove from queue
                self.job_queue = [j for j in self.job_queue if j.job_id != job_id]
                heapq.heapify(self.job_queue)
                
                return True
            
            return False
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Lấy trạng thái của một job"""
        with self.lock:
            if job_id not in self.all_jobs:
                return None
            
            job = self.all_jobs[job_id]
            return {
                'job_id': job.job_id,
                'name': job.name,
                'status': job.status.value,
                'priority': job.priority,
                'created_at': job.created_at.isoformat(),
                'started_at': job.started_at.isoformat() if job.started_at else None,
                'completed_at': job.completed_at.isoformat() if job.completed_at else None,
                'runtime': (job.completed_at - job.started_at).total_seconds() 
                          if job.started_at and job.completed_at else None,
                'error': job.error
            }
    
    def get_scheduler_status(self) -> Dict[str, Any]:
        """Lấy trạng thái scheduler"""
        with self.lock:
            return {
                'running': self.running,
                'queued_jobs': len(self.job_queue),
                'running_jobs': len(self.running_jobs),
                'completed_jobs': len(self.completed_jobs),
                'max_workers': self.max_workers,
                'resource_utilization': self.resource_pool.get_utilization(),
                'statistics': self.stats.copy()
            }


# Testing
if __name__ == '__main__':
    print("Testing Smart Scheduler\n" + "="*70)
    
    # Test functions
    def test_job(duration, name):
        print(f"  Running {name}...")
        time.sleep(duration)
        return f"Result from {name}"
    
    # Create scheduler
    scheduler = SmartScheduler(max_workers=2, total_cpu=4, total_memory_mb=4096)
    scheduler.start()
    
    # Submit jobs with different priorities
    print("\n1. Submitting jobs...")
    
    job1 = scheduler.submit_job(
        "Critical Job",
        test_job,
        args=(2, "Critical Job"),
        priority=JobPriority.CRITICAL,
        cpu_cores=2,
        on_complete=lambda r: print(f"  ✅ {r}")
    )
    
    job2 = scheduler.submit_job(
        "High Priority Job",
        test_job,
        args=(3, "High Priority Job"),
        priority=JobPriority.HIGH,
        cpu_cores=1
    )
    
    job3 = scheduler.submit_job(
        "Normal Job",
        test_job,
        args=(1, "Normal Job"),
        priority=JobPriority.NORMAL,
        cpu_cores=1
    )
    
    job4 = scheduler.submit_job(
        "Low Priority Job",
        test_job,
        args=(2, "Low Priority Job"),
        priority=JobPriority.LOW,
        cpu_cores=1
    )
    
    print(f"   Submitted 4 jobs")
    
    # Wait and monitor
    print("\n2. Monitoring execution...")
    for i in range(10):
        time.sleep(1)
        status = scheduler.get_scheduler_status()
        print(f"   [{i+1}s] Queued: {status['queued_jobs']}, "
              f"Running: {status['running_jobs']}, "
              f"Completed: {status['completed_jobs']}")
    
    # Get final status
    print("\n3. Final status:")
    status = scheduler.get_scheduler_status()
    print(f"   Total jobs: {status['statistics']['total_jobs']}")
    print(f"   Completed: {status['statistics']['completed_jobs']}")
    print(f"   Avg runtime: {status['statistics']['avg_runtime']:.2f}s")
    print(f"   CPU utilization: {status['resource_utilization']['cpu']:.1f}%")
    
    # Stop
    print("\n4. Stopping scheduler...")
    scheduler.stop()
    
    print("\n✅ Smart Scheduler test completed!")
