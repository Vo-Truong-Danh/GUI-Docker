"""
Constants Module
Version: 1.0.0

Centralized constants to replace magic numbers throughout the codebase.
This improves code maintainability and readability.
"""

# ============================================================================
# TIMEOUT CONSTANTS (in seconds)
# ============================================================================

# Docker command timeouts
DOCKER_INFO_TIMEOUT = 10
DOCKER_COMMAND_TIMEOUT = 30
DOCKER_COPY_TIMEOUT = 30
DOCKER_EXEC_TIMEOUT = 10
DOCKER_COMPOSE_TIMEOUT = 5

# Spark job timeouts
SPARK_SUBMIT_TIMEOUT = 300  # 5 minutes
SPARK_JOB_DEFAULT_TIMEOUT = 600  # 10 minutes

# HDFS operation timeouts
HDFS_SAFE_MODE_CHECK_TIMEOUT = 10
HDFS_SAFE_MODE_MAX_WAIT = 60
HDFS_MKDIR_TIMEOUT = 30
HDFS_PUT_TIMEOUT = 120  # 2 minutes
HDFS_RM_TIMEOUT = 30
HDFS_LS_TIMEOUT = 10

# Network/Connection timeouts
CONNECTION_TIMEOUT = 10
SOCKET_TIMEOUT = 3
HEALTH_CHECK_TIMEOUT = 10

# Package installation timeouts
PACKAGE_INSTALL_TIMEOUT = 60  # 1 minute
JAVA_COMPILE_TIMEOUT = 30
JAVA_UNZIP_TIMEOUT = 300  # 5 minutes

# ============================================================================
# RETRY/WAIT CONSTANTS
# ============================================================================

# Retry attempts
MAX_RETRY_ATTEMPTS = 3
MAX_DB_RETRY_ATTEMPTS = 3
MAX_RECOVERY_ATTEMPTS = 3

# Wait/sleep durations
DOCKER_RESTART_DELAY = 3  # seconds
HDFS_STABILIZE_DELAY = 2  # seconds
RETRY_BACKOFF_BASE = 0.1  # Base delay for exponential backoff
WAIT_BETWEEN_CHECKS = 2  # seconds

# Cooldown periods
RECOVERY_COOLDOWN = 300  # 5 minutes
CIRCUIT_BREAKER_TIMEOUT = 60  # 1 minute

# Docker startup wait
DOCKER_STARTUP_TIMEOUT = 90  # 90 seconds
DOCKER_CHECK_INTERVAL = 2  # seconds

# ============================================================================
# SIZE/LENGTH LIMITS
# ============================================================================

# History limits
MAX_HISTORY_SIZE = 10
MAX_ERROR_HISTORY = 100
MAX_LOG_FILES = 5

# String lengths
MAX_INPUT_LENGTH = 1000
MAX_FILENAME_LENGTH = 255
MAX_PATH_LENGTH = 4096

# File sizes
MAX_LOG_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_UPLOAD_FILE_SIZE = 1024 * 1024 * 1024  # 1 GB (for display purposes)

# ============================================================================
# DATABASE CONSTANTS
# ============================================================================

DB_CONNECTION_TIMEOUT = 10.0  # seconds
DB_MAX_CONNECTIONS = 5
DB_CLEANUP_DAYS = 30  # Keep records for 30 days

# ============================================================================
# LOGGING CONSTANTS
# ============================================================================

LOG_CLEANUP_DAYS = 7
LOG_FILE_SIZE_MB = 10
LOG_BACKUP_COUNT = 5

# ============================================================================
# PORT NUMBERS
# ============================================================================

SPARK_MASTER_PORT = 7077
SPARK_MASTER_WEB_UI_PORT = 8080
SPARK_WORKER_WEB_UI_PORT = 8081
HDFS_NAMENODE_PORT = 8020
HDFS_NAMENODE_WEB_UI_PORT = 9870
DOCKER_DAEMON_PORT = 2375
DOCKER_DAEMON_TLS_PORT = 2376

# Valid port range
MIN_PORT = 1
MAX_PORT = 65535

# ============================================================================
# CIRCUIT BREAKER CONSTANTS
# ============================================================================

CIRCUIT_BREAKER_FAILURE_THRESHOLD = 5
CIRCUIT_BREAKER_SUCCESS_THRESHOLD = 2

# ============================================================================
# PERFORMANCE MONITORING
# ============================================================================

PERFORMANCE_SAMPLE_INTERVAL = 1.0  # seconds
PERFORMANCE_HISTORY_SIZE = 100

# ============================================================================
# UI/DISPLAY CONSTANTS
# ============================================================================

PROGRESS_BAR_WIDTH = 50
MAX_DISPLAY_LINES = 1000
REFRESH_INTERVAL_MS = 100  # milliseconds

# ============================================================================
# VALIDATION PATTERNS
# ============================================================================

# Container name pattern (Docker specification)
CONTAINER_NAME_PATTERN = r'^[a-zA-Z0-9][a-zA-Z0-9_.-]{0,254}$'

# Safe filename pattern
SAFE_FILENAME_PATTERN = r'^[a-zA-Z0-9_\-\.]+$'

# Spark master URL pattern
SPARK_MASTER_PATTERN = r'^spark://[a-zA-Z0-9\-\.]+:\d+$'

# HDFS URL pattern
HDFS_URL_PATTERN = r'^hdfs://[a-zA-Z0-9\-\.]+:\d+/.*$'

# ============================================================================
# ERROR MESSAGES
# ============================================================================

ERROR_DOCKER_NOT_RUNNING = "Docker is not running. Please start Docker Desktop."
ERROR_DOCKER_NOT_FOUND = "Docker command not found. Please install Docker."
ERROR_CONTAINER_NOT_FOUND = "Container not found: {container}"
ERROR_FILE_NOT_FOUND = "File not found: {filepath}"
ERROR_PERMISSION_DENIED = "Permission denied: {resource}"
ERROR_TIMEOUT = "Operation timed out after {timeout}s"
ERROR_INVALID_INPUT = "Invalid input: {detail}"
ERROR_CONNECTION_FAILED = "Connection failed: {detail}"

# ============================================================================
# SUCCESS MESSAGES
# ============================================================================

SUCCESS_DOCKER_RUNNING = "Docker is running"
SUCCESS_FILE_COPIED = "File copied successfully"
SUCCESS_JOB_COMPLETED = "Spark job completed successfully"
SUCCESS_UPLOAD_COMPLETED = "Upload completed successfully"

# ============================================================================
# DEFAULT VALUES
# ============================================================================

DEFAULT_CONTAINER = 'spark-worker'
DEFAULT_MASTER = 'spark://spark-master:7077'
DEFAULT_HDFS_CONTAINER = 'namenode'
DEFAULT_HDFS_HOST = 'hdfs://namenode:8020'
DEFAULT_HDFS_PATH = '/user/spark/data'

# ============================================================================
# FILE EXTENSIONS
# ============================================================================

PYTHON_EXTENSIONS = ['.py']
JAVA_EXTENSIONS = ['.java', '.jar']
SCALA_EXTENSIONS = ['.scala']
ARCHIVE_EXTENSIONS = ['.zip', '.tar', '.tar.gz', '.tgz', '.tar.bz2']
DATA_EXTENSIONS = ['.csv', '.json', '.txt', '.parquet']

ALL_SUPPORTED_EXTENSIONS = (
    PYTHON_EXTENSIONS + 
    JAVA_EXTENSIONS + 
    SCALA_EXTENSIONS + 
    ARCHIVE_EXTENSIONS + 
    DATA_EXTENSIONS
)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_timeout(operation: str) -> int:
    """
    Get timeout for specific operation
    
    Args:
        operation: Operation name
        
    Returns:
        Timeout in seconds
    """
    timeout_map = {
        'docker_info': DOCKER_INFO_TIMEOUT,
        'docker_command': DOCKER_COMMAND_TIMEOUT,
        'docker_copy': DOCKER_COPY_TIMEOUT,
        'docker_exec': DOCKER_EXEC_TIMEOUT,
        'spark_submit': SPARK_SUBMIT_TIMEOUT,
        'hdfs_mkdir': HDFS_MKDIR_TIMEOUT,
        'hdfs_put': HDFS_PUT_TIMEOUT,
        'package_install': PACKAGE_INSTALL_TIMEOUT,
    }
    
    return timeout_map.get(operation, DOCKER_COMMAND_TIMEOUT)


def is_valid_port(port: int) -> bool:
    """Check if port number is valid"""
    return MIN_PORT <= port <= MAX_PORT


def is_supported_extension(filename: str) -> bool:
    """Check if file extension is supported"""
    from pathlib import Path
    ext = Path(filename).suffix.lower()
    return ext in ALL_SUPPORTED_EXTENSIONS


# ============================================================================
# TESTING
# ============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("CONSTANTS MODULE TEST")
    print("=" * 70)
    
    print(f"\n📦 Timeout Constants:")
    print(f"   Docker Info: {DOCKER_INFO_TIMEOUT}s")
    print(f"   Spark Submit: {SPARK_SUBMIT_TIMEOUT}s")
    print(f"   HDFS Put: {HDFS_PUT_TIMEOUT}s")
    
    print(f"\n🔄 Retry Constants:")
    print(f"   Max Retries: {MAX_RETRY_ATTEMPTS}")
    print(f"   Backoff Base: {RETRY_BACKOFF_BASE}s")
    
    print(f"\n📊 Size Limits:")
    print(f"   Max History: {MAX_HISTORY_SIZE}")
    print(f"   Max Log Size: {MAX_LOG_FILE_SIZE / 1024 / 1024:.0f}MB")
    
    print(f"\n🔌 Port Numbers:")
    print(f"   Spark Master: {SPARK_MASTER_PORT}")
    print(f"   HDFS NameNode: {HDFS_NAMENODE_PORT}")
    
    print(f"\n✅ Test get_timeout():")
    print(f"   docker_info: {get_timeout('docker_info')}s")
    print(f"   spark_submit: {get_timeout('spark_submit')}s")
    print(f"   unknown: {get_timeout('unknown')}s (default)")
    
    print(f"\n✅ Test is_valid_port():")
    print(f"   Port 8080: {is_valid_port(8080)}")
    print(f"   Port 0: {is_valid_port(0)}")
    print(f"   Port 70000: {is_valid_port(70000)}")
    
    print(f"\n✅ Test is_supported_extension():")
    print(f"   test.py: {is_supported_extension('test.py')}")
    print(f"   data.csv: {is_supported_extension('data.csv')}")
    print(f"   file.exe: {is_supported_extension('file.exe')}")
    
    print("\n" + "=" * 70)
    print("✅ All constants loaded successfully!")
    print("=" * 70)
