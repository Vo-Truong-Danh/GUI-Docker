"""
Parallel Upload Optimizer
Upload nhiều chunks cùng lúc → Nhanh gấp 3-5 lần!
"""

import os
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Callable, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading


# Configuration
CHUNK_SIZE = 50 * 1024 * 1024  # 50 MB
MAX_PARALLEL_UPLOADS = 4  # Upload tối đa 4 chunks cùng lúc


def upload_chunk_parallel(
    chunk_data: Tuple[int, str, str, str, str]
) -> Tuple[int, bool, str]:
    """
    Upload 1 chunk (dùng cho parallel execution)
    
    Args:
        chunk_data: (chunk_num, local_path, container, remote_path, chunk_name)
    
    Returns:
        (chunk_num, success, message)
    """
    chunk_num, local_path, container, remote_path, chunk_name = chunk_data
    
    try:
        # Copy to container
        cp_cmd = [
            'docker', 'cp',
            local_path,
            f"{container}:{remote_path}"
        ]
        
        result = subprocess.run(
            cp_cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes per chunk
        )
        
        if result.returncode != 0:
            return chunk_num, False, f"Docker cp failed: {result.stderr}"
        
        return chunk_num, True, "OK"
        
    except subprocess.TimeoutExpired:
        return chunk_num, False, "Timeout"
    except Exception as e:
        return chunk_num, False, str(e)


def upload_large_file_parallel(
    filepath: str,
    container: str,
    hdfs_path: str,
    max_workers: int = 4,
    chunk_size: int = CHUNK_SIZE,
    log_callback: Optional[Callable[[str, str], None]] = None,
    progress_callback: Optional[Callable[[int, int], None]] = None
) -> Tuple[bool, str]:
    """
    Upload file lớn với parallel chunks
    
    Args:
        filepath: Đường dẫn file local
        container: Tên Docker container
        hdfs_path: Đường dẫn HDFS đích
        max_workers: Số chunks upload song song (mặc định: 4)
        chunk_size: Kích thước mỗi chunk (mặc định: 50MB)
        log_callback: Callback(message, tag)
        progress_callback: Callback(uploaded_bytes, total_bytes)
    
    Returns:
        (success, message)
    """
    
    def log(msg: str, tag: str = 'info'):
        if log_callback:
            log_callback(msg, tag)
    
    try:
        # Validate file
        if not os.path.exists(filepath):
            return False, f"File không tồn tại: {filepath}"
        
        file_size = os.path.getsize(filepath)
        filename = os.path.basename(filepath)
        
        # Calculate chunks
        total_chunks = (file_size + chunk_size - 1) // chunk_size
        
        log(f"📦 Parallel upload: {max_workers} workers", 'info')
        log(f"🔪 Chunk size: {chunk_size / (1024**2):.2f} MB", 'info')
        log(f"🧩 Total chunks: {total_chunks}", 'info')
        
        # Create temp directories
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        temp_dir_container = f"/tmp/upload_{timestamp}"
        temp_dir_local = tempfile.mkdtemp(prefix='hdfs_upload_')
        
        log(f"📁 Local temp: {temp_dir_local}", 'info')
        log(f"📁 Container temp: {temp_dir_container}", 'info')
        
        # Create container temp dir
        subprocess.run(
            ['docker', 'exec', container, 'mkdir', '-p', temp_dir_container],
            check=True,
            capture_output=True,
            timeout=30
        )
        
        # Split file into chunks
        log("🔪 Splitting file...", 'info')
        chunk_files = []
        
        with open(filepath, 'rb') as f:
            for i in range(total_chunks):
                chunk_data = f.read(chunk_size)
                if not chunk_data:
                    break
                
                chunk_filename = f"chunk_{i:04d}"
                chunk_path_local = os.path.join(temp_dir_local, chunk_filename)
                
                # Write chunk
                with open(chunk_path_local, 'wb') as chunk_file:
                    chunk_file.write(chunk_data)
                
                chunk_path_container = f"{temp_dir_container}/{chunk_filename}"
                chunk_files.append((i, chunk_path_local, container, chunk_path_container, chunk_filename))
        
        log(f"✅ Created {len(chunk_files)} chunks", 'info')
        
        # Upload chunks in parallel
        log(f"⚡ Uploading {max_workers} chunks at a time...", 'info')
        
        uploaded_bytes = 0
        upload_lock = threading.Lock()
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all chunk uploads
            futures = {
                executor.submit(upload_chunk_parallel, chunk_data): chunk_data
                for chunk_data in chunk_files
            }
            
            # Process results as they complete
            for future in as_completed(futures):
                chunk_num, success, msg = future.result()
                
                if not success:
                    log(f"❌ Chunk {chunk_num} failed: {msg}", 'error')
                    # Cancel remaining uploads
                    for f in futures:
                        f.cancel()
                    return False, f"Upload chunk {chunk_num} failed: {msg}"
                
                # Update progress
                with upload_lock:
                    uploaded_bytes += chunk_size
                    if progress_callback:
                        progress_callback(
                            min(uploaded_bytes, file_size),
                            file_size
                        )
                
                pct = (chunk_num + 1) / total_chunks * 100
                log(f"✓ Chunk {chunk_num+1}/{total_chunks} ({pct:.1f}%)", 'info')
        
        log("✅ All chunks uploaded", 'success')
        
        # Merge chunks in container
        log("🔗 Merging chunks...", 'info')
        merged_file = f"{temp_dir_container}/{filename}"
        merge_cmd = f"cat {temp_dir_container}/chunk_* > {merged_file}"
        
        result = subprocess.run(
            ['docker', 'exec', container, 'bash', '-c', merge_cmd],
            capture_output=True,
            text=True,
            timeout=600
        )
        
        if result.returncode != 0:
            return False, f"Merge failed: {result.stderr}"
        
        log("✅ Chunks merged", 'success')
        
        # Upload to HDFS
        log(f"📤 Uploading to HDFS: {hdfs_path}", 'info')
        
        upload_cmd = [
            'docker', 'exec', container,
            'hdfs', 'dfs', '-put', '-f',
            merged_file,
            hdfs_path
        ]
        
        result = subprocess.run(
            upload_cmd,
            capture_output=True,
            text=True,
            timeout=1800
        )
        
        if result.returncode != 0:
            return False, f"HDFS upload failed: {result.stderr}"
        
        log("✅ Uploaded to HDFS", 'success')
        
        # Cleanup
        log("🧹 Cleaning up...", 'info')
        
        subprocess.run(
            ['docker', 'exec', container, 'rm', '-rf', temp_dir_container],
            capture_output=True,
            timeout=60
        )
        
        import shutil
        if os.path.exists(temp_dir_local):
            shutil.rmtree(temp_dir_local)
        
        log("✅ Cleanup complete", 'success')
        
        return True, f"Successfully uploaded {filename} to {hdfs_path}"
        
    except Exception as e:
        return False, f"Error: {str(e)}"
    finally:
        # Ensure local cleanup
        import shutil
        if 'temp_dir_local' in locals() and os.path.exists(temp_dir_local):
            shutil.rmtree(temp_dir_local)


# Example usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 4:
        print("Usage: python parallel_upload.py <file> <container> <hdfs_path> [workers]")
        print("Example: python parallel_upload.py data.csv namenode /input/data.csv 4")
        sys.exit(1)
    
    filepath = sys.argv[1]
    container = sys.argv[2]
    hdfs_path = sys.argv[3]
    workers = int(sys.argv[4]) if len(sys.argv) > 4 else 4
    
    def log_callback(msg, tag):
        tags = {'error': '❌', 'success': '✅', 'info': 'ℹ️'}
        print(f"{tags.get(tag, 'ℹ️')} {msg}")
    
    def progress_callback(current, total):
        pct = (current / total) * 100
        print(f"📊 Progress: {pct:.1f}%")
    
    success, message = upload_large_file_parallel(
        filepath=filepath,
        container=container,
        hdfs_path=hdfs_path,
        max_workers=workers,
        log_callback=log_callback,
        progress_callback=progress_callback
    )
    
    if success:
        print(f"\n✅ {message}")
    else:
        print(f"\n❌ {message}")
        sys.exit(1)
