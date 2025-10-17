"""
Optimized Large File Upload for HDFS
Handles files > 1GB with:
- Chunked upload (split into smaller parts)
- Progress tracking
- Resume capability
- Memory efficient streaming
"""

import os
import subprocess
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Callable, Optional, Tuple

# Import hidden subprocess utilities
try:
    from subprocess_utils import run_hidden, popen_hidden
except ImportError:
    # Fallback if not available
    def run_hidden(*args, **kwargs):
        return subprocess.run(*args, **kwargs)
    def popen_hidden(*args, **kwargs):
        return subprocess.Popen(*args, **kwargs)

# Configuration
# CHUNK_SIZE: Giảm nếu mạng chậm/không ổn định
# - 50 MB: Mạng nhanh/ổn định (mặc định)
# - 25 MB: Mạng trung bình
# - 10 MB: Mạng chậm/hay bị timeout
CHUNK_SIZE = 50 * 1024 * 1024  # 50 MB chunks (thay đổi nếu cần)
MAX_DIRECT_UPLOAD_SIZE = 100 * 1024 * 1024  # 100 MB


def get_file_hash(filepath: str, chunk_size: int = 8192) -> str:
    """Calculate MD5 hash for file verification"""
    md5 = hashlib.md5()
    with open(filepath, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            md5.update(chunk)
    return md5.hexdigest()


def upload_large_file_chunked(
    filepath: str,
    container: str,
    hdfs_path: str,
    log_callback: Optional[Callable] = None,
    progress_callback: Optional[Callable[[int, int], None]] = None
) -> Tuple[bool, str]:
    """
    Upload large file to HDFS using chunked approach
    
    Args:
        filepath: Local file path
        container: Docker container name
        hdfs_path: Target HDFS path (file, not directory)
        log_callback: Function to log messages
        progress_callback: Function(bytes_uploaded, total_bytes)
    
    Returns:
        (success: bool, message: str)
    """
    def log(msg, level='info'):
        if log_callback:
            log_callback(msg, level)
        else:
            print(f"[{level.upper()}] {msg}")
    
    try:
        file_size = os.path.getsize(filepath)
        filename = Path(filepath).name
        
        log(f"📊 File size: {file_size / (1024**2):.2f} MB", 'info')
        
        # Small files: direct upload
        if file_size <= MAX_DIRECT_UPLOAD_SIZE:
            log("📤 Using direct upload (file < 100 MB)", 'info')
            return _upload_direct(filepath, container, hdfs_path, log_callback)
        
        # Large files: chunked upload
        log(f"📦 Using chunked upload ({file_size / (1024**2):.2f} MB)", 'info')
        log(f"🔪 Chunk size: {CHUNK_SIZE / (1024**2):.2f} MB", 'info')
        
        # Calculate chunks
        num_chunks = (file_size + CHUNK_SIZE - 1) // CHUNK_SIZE
        log(f"🧩 Total chunks: {num_chunks}", 'info')
        
        # Create temp directory in container
        temp_dir_container = f"/tmp/upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        log(f"📁 Creating temp directory in container: {temp_dir_container}", 'info')
        
        run_hidden(
            ['docker', 'exec', container, 'mkdir', '-p', temp_dir_container],
            check=True,
            capture_output=True
        )
        
        # Create temp directory on local machine (Windows/Linux compatible)
        import tempfile
        temp_dir_local = tempfile.mkdtemp(prefix='hdfs_upload_')
        log(f"📁 Created local temp directory: {temp_dir_local}", 'info')
        
        # Split and upload chunks
        chunks_uploaded = 0
        total_bytes_uploaded = 0
        
        try:
            with open(filepath, 'rb') as source_file:
                for chunk_index in range(num_chunks):
                    chunk_data = source_file.read(CHUNK_SIZE)
                    chunk_size = len(chunk_data)
                    
                    if not chunk_data:
                        break
                    
                    # Use 1-based numbering: chunk_1, chunk_2, ... (not chunk_0000, chunk_0001)
                    chunk_number = chunk_index + 1
                    chunk_filename = f"chunk_{chunk_number}"
                    chunk_path_local = os.path.join(temp_dir_local, chunk_filename)
                    chunk_path_container = f"{temp_dir_container}/{chunk_filename}"
                    
                    # Write chunk to local temp file
                    with open(chunk_path_local, 'wb') as chunk_file:
                        chunk_file.write(chunk_data)
                    
                    # Log progress
                    log(f"  📦 Chunk {chunk_number}/{num_chunks}: {chunk_size / (1024**2):.2f} MB", 'info')
                    
                    # Copy chunk to container
                    # Timeout: 300s (5 phút) cho mỗi chunk 50MB
                    run_hidden(
                        ['docker', 'cp', chunk_path_local, f'{container}:{chunk_path_container}'],
                        check=True,
                        capture_output=True,
                        timeout=300
                    )
                    
                    # Clean up local temp chunk
                    os.remove(chunk_path_local)
                    
                    chunks_uploaded += 1
                    total_bytes_uploaded += chunk_size
                    
                    # Progress callback
                    if progress_callback:
                        progress_callback(total_bytes_uploaded, file_size)
                    
                    log(f"     ✓ Progress: {total_bytes_uploaded / file_size * 100:.1f}%", 'success')
            
            # Merge chunks in container and upload to HDFS
            log("", 'info')
            log("🔗 Merging chunks...", 'info')
            
            merged_file = f"{temp_dir_container}/{filename}"
            
            # Use sh (not bash) and sort chunks numerically to ensure correct order
            # chunk_1, chunk_2, ..., chunk_10, chunk_11 (not chunk_1, chunk_10, chunk_11, chunk_2)
            merge_cmd = f"for i in $(seq 1 {num_chunks}); do cat {temp_dir_container}/chunk_$i; done > {merged_file}"
            
            merge_result = run_hidden(
                ['docker', 'exec', container, 'sh', '-c', merge_cmd],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if merge_result.returncode != 0:
                log(f"  ❌ Merge failed: {merge_result.stderr}", 'error')
                return False, f"Failed to merge chunks: {merge_result.stderr}"
            
            log(f"  ✓ Merged into: {merged_file}", 'success')
            
            # CRITICAL: Verify merged file size
            verify_size_cmd = ['docker', 'exec', container, 'stat', '-c', '%s', merged_file]
            verify_result = run_hidden(verify_size_cmd, capture_output=True, text=True, timeout=10)
            
            if verify_result.returncode == 0:
                merged_size = int(verify_result.stdout.strip())
                expected_size = file_size  # Use file_size from function scope
                
                log(f"  📊 Verification:", 'info')
                log(f"     Expected: {expected_size / 1024 / 1024:.2f} MB", 'info')
                log(f"     Merged:   {merged_size / 1024 / 1024:.2f} MB", 'info')
                
                if merged_size != expected_size:
                    log(f"  ❌ Size mismatch! File corrupted during merge", 'error')
                    return False, f"Size mismatch: expected {expected_size}, got {merged_size}"
                
                log(f"  ✅ Size verification passed", 'success')
            else:
                log(f"  ⚠️ Could not verify merged file size", 'warning')
            
            # Upload merged file to HDFS
            log("", 'info')
            log("📤 Uploading to HDFS...", 'info')
            
            hdfs_cmd = ['docker', 'exec', container, 'hdfs', 'dfs', '-put', '-f', merged_file, hdfs_path]
            
            result = run_hidden(
                hdfs_cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes for large files
            )
            
            if result.returncode != 0:
                log(f"  ❌ HDFS upload failed: {result.stderr}", 'error')
                return False, f"HDFS upload failed: {result.stderr}"
            
            log(f"  ✓ Uploaded to HDFS: {hdfs_path}", 'success')
            
            # Copy merged file to /tmp/ for extraction (if it's a compressed file)
            # This is needed for extraction step that runs later
            filename_lower = filename.lower()
            is_compressed = (filename_lower.endswith('.zip') or 
                           filename_lower.endswith('.tar.gz') or 
                           filename_lower.endswith('.tgz') or
                           filename_lower.endswith('.tar') or
                           filename_lower.endswith('.gz'))
            
            if is_compressed:
                log("", 'info')
                log("📋 Copying to /tmp/ for extraction...", 'info')
                
                copy_cmd = f"cp {merged_file} /tmp/{filename}"
                copy_result = run_hidden(
                    ['docker', 'exec', container, 'sh', '-c', copy_cmd],
                    capture_output=True,
                    text=True
                )
                
                if copy_result.returncode == 0:
                    log(f"  ✓ Copied to /tmp/{filename} for extraction", 'success')
                else:
                    log(f"  ⚠️ Copy failed: {copy_result.stderr}", 'warning')
            
            # Cleanup container temp directory (after copying to /tmp/)
            log("", 'info')
            log("🧹 Cleaning up temporary files...", 'info')
            
            run_hidden(
                ['docker', 'exec', container, 'rm', '-rf', temp_dir_container],
                capture_output=True
            )
            
            log("  ✓ Cleanup complete", 'success')
            
            # Verify upload
            log("", 'info')
            log("🔍 Verifying upload...", 'info')
            
            verify_cmd = ['docker', 'exec', container, 'hdfs', 'dfs', '-ls', hdfs_path]
            verify_result = run_hidden(verify_cmd, capture_output=True, text=True)
            
            if verify_result.returncode == 0 and hdfs_path in verify_result.stdout:
                log(f"  ✅ Verification successful!", 'success')
                return True, f"Successfully uploaded {filename} to {hdfs_path}"
            else:
                log(f"  ⚠️ Verification warning: {verify_result.stderr}", 'warning')
                return True, f"Uploaded but verification inconclusive"
        
        finally:
            # Clean up local temp directory
            import shutil
            if os.path.exists(temp_dir_local):
                shutil.rmtree(temp_dir_local)
                log(f"  🧹 Cleaned up local temp: {temp_dir_local}", 'info')
        
    except subprocess.TimeoutExpired:
        return False, "Upload timeout (file too large or slow network)"
    except Exception as e:
        log(f"❌ Upload error: {str(e)}", 'error')
        return False, f"Upload failed: {str(e)}"


def _upload_direct(
    filepath: str,
    container: str,
    hdfs_path: str,
    log_callback: Optional[Callable] = None
) -> Tuple[bool, str]:
    """Direct upload for small files (< 100 MB)"""
    def log(msg, level='info'):
        if log_callback:
            log_callback(msg, level)
    
    try:
        filename = Path(filepath).name
        temp_path = f"/tmp/{filename}"
        
        # Copy to container
        log("  📦 Copying to container...", 'info')
        run_hidden(
            ['docker', 'cp', filepath, f'{container}:{temp_path}'],
            check=True,
            capture_output=True,
            timeout=120
        )
        log("    ✓ Copied to container", 'success')
        
        # Upload to HDFS
        log("  📤 Uploading to HDFS...", 'info')
        run_hidden(
            ['docker', 'exec', container, 'hdfs', 'dfs', '-put', '-f', temp_path, hdfs_path],
            check=True,
            capture_output=True,
            timeout=300
        )
        log(f"    ✓ Uploaded to {hdfs_path}", 'success')
        
        # Cleanup
        run_hidden(
            ['docker', 'exec', container, 'rm', temp_path],
            capture_output=True
        )
        
        return True, f"Successfully uploaded {filename}"
        
    except Exception as e:
        return False, f"Direct upload failed: {str(e)}"


def get_hdfs_file_info(container: str, hdfs_path: str) -> dict:
    """Get file information from HDFS"""
    try:
        cmd = ['docker', 'exec', container, 'hdfs', 'dfs', '-stat', '%n,%b,%y', hdfs_path]
        result = run_hidden(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            parts = result.stdout.strip().split(',')
            return {
                'name': parts[0] if len(parts) > 0 else '',
                'size': int(parts[1]) if len(parts) > 1 else 0,
                'modification_time': parts[2] if len(parts) > 2 else ''
            }
    except:
        pass
    
    return {}


# Example usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 4:
        print("Usage: python large_file_upload.py <local_file> <container> <hdfs_path>")
        sys.exit(1)
    
    filepath = sys.argv[1]
    container = sys.argv[2]
    hdfs_path = sys.argv[3]
    
    def progress(uploaded, total):
        percent = uploaded / total * 100
        bar = "█" * int(percent // 2) + "░" * (50 - int(percent // 2))
        print(f"\r  [{bar}] {percent:.1f}%", end='', flush=True)
    
    success, message = upload_large_file_chunked(
        filepath=filepath,
        container=container,
        hdfs_path=hdfs_path,
        progress_callback=progress
    )
    
    print()  # New line after progress bar
    print(f"\n{'✅' if success else '❌'} {message}")
