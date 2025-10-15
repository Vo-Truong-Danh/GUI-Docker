"""
Compression Optimizer for Large File Upload
Nén file trước khi upload → Giảm 70-90% dung lượng!
"""

import os
import gzip
import shutil
import subprocess
from pathlib import Path
from typing import Tuple, Optional, Callable


def compress_file_gzip(
    input_file: str,
    output_file: Optional[str] = None,
    compression_level: int = 6,
    progress_callback: Optional[Callable[[int, int], None]] = None
) -> Tuple[bool, str, str]:
    """
    Nén file bằng gzip
    
    Args:
        input_file: Đường dẫn file gốc
        output_file: Đường dẫn file nén (None = auto)
        compression_level: 1-9 (1=nhanh nhất, 9=nén tốt nhất)
        progress_callback: Callback(bytes_processed, total_bytes)
    
    Returns:
        (success, output_path, message)
    """
    try:
        if not os.path.exists(input_file):
            return False, "", f"File không tồn tại: {input_file}"
        
        # Auto output file
        if output_file is None:
            output_file = f"{input_file}.gz"
        
        # Get file size
        file_size = os.path.getsize(input_file)
        processed = 0
        
        # Compress with streaming
        CHUNK_SIZE = 10 * 1024 * 1024  # 10 MB chunks
        
        with open(input_file, 'rb') as f_in:
            with gzip.open(output_file, 'wb', compresslevel=compression_level) as f_out:
                while True:
                    chunk = f_in.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    f_out.write(chunk)
                    processed += len(chunk)
                    
                    if progress_callback:
                        progress_callback(processed, file_size)
        
        # Get compressed size
        compressed_size = os.path.getsize(output_file)
        ratio = (1 - compressed_size / file_size) * 100
        
        msg = (f"✅ Nén thành công!\n"
               f"   📄 File gốc: {file_size / (1024**2):.2f} MB\n"
               f"   📦 File nén: {compressed_size / (1024**2):.2f} MB\n"
               f"   💾 Tiết kiệm: {ratio:.1f}%")
        
        return True, output_file, msg
        
    except Exception as e:
        return False, "", f"❌ Lỗi nén: {str(e)}"


def compress_file_7zip(
    input_file: str,
    output_file: Optional[str] = None,
    compression_level: str = "5",  # 0-9
    method: str = "LZMA2"  # LZMA2, LZMA, PPMd, BZip2
) -> Tuple[bool, str, str]:
    """
    Nén file bằng 7-Zip (nén tốt hơn gzip nhưng cần cài 7-Zip)
    
    Download 7-Zip: https://www.7-zip.org/download.html
    """
    try:
        if not os.path.exists(input_file):
            return False, "", f"File không tồn tại: {input_file}"
        
        # Check 7z
        try:
            subprocess.run(['7z'], capture_output=True, timeout=1)
        except FileNotFoundError:
            return False, "", "❌ Chưa cài 7-Zip! Download: https://www.7-zip.org/"
        
        # Auto output file
        if output_file is None:
            output_file = f"{input_file}.7z"
        
        # Get original size
        original_size = os.path.getsize(input_file)
        
        # Compress
        cmd = [
            '7z', 'a',  # Add to archive
            f'-mx={compression_level}',  # Compression level
            f'-m0={method}',  # Compression method
            output_file,
            input_file
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
        
        if result.returncode != 0:
            return False, "", f"❌ Lỗi 7z: {result.stderr}"
        
        # Get compressed size
        compressed_size = os.path.getsize(output_file)
        ratio = (1 - compressed_size / original_size) * 100
        
        msg = (f"✅ Nén 7-Zip thành công!\n"
               f"   📄 File gốc: {original_size / (1024**2):.2f} MB\n"
               f"   📦 File nén: {compressed_size / (1024**2):.2f} MB\n"
               f"   💾 Tiết kiệm: {ratio:.1f}%")
        
        return True, output_file, msg
        
    except subprocess.TimeoutExpired:
        return False, "", "❌ Timeout nén file (quá 30 phút)"
    except Exception as e:
        return False, "", f"❌ Lỗi: {str(e)}"


def estimate_compression_ratio(file_path: str, sample_size: int = 10 * 1024 * 1024) -> float:
    """
    Ước tính tỷ lệ nén bằng cách nén 10MB đầu
    
    Returns:
        Tỷ lệ nén ước tính (0-1, ví dụ 0.7 = nén còn 70%)
    """
    try:
        file_size = os.path.getsize(file_path)
        sample_size = min(sample_size, file_size)
        
        # Read sample
        with open(file_path, 'rb') as f:
            sample = f.read(sample_size)
        
        # Compress sample
        compressed = gzip.compress(sample, compresslevel=6)
        
        ratio = len(compressed) / len(sample)
        return ratio
        
    except Exception:
        return 0.8  # Default estimate


def should_compress(file_path: str, threshold: float = 0.85) -> Tuple[bool, str]:
    """
    Kiểm tra xem có nên nén file không
    
    Args:
        file_path: Đường dẫn file
        threshold: Nén nếu tỷ lệ < threshold (mặc định: nén nếu giảm > 15%)
    
    Returns:
        (should_compress, reason)
    """
    try:
        # Check file type
        ext = os.path.splitext(file_path)[1].lower()
        
        # Already compressed formats
        compressed_formats = {
            '.gz', '.zip', '.7z', '.rar', '.bz2', '.xz',
            '.jpg', '.jpeg', '.png', '.mp4', '.mp3', '.avi'
        }
        
        if ext in compressed_formats:
            return False, f"File {ext} đã được nén rồi"
        
        # Text/CSV files → nén rất tốt
        text_formats = {'.txt', '.csv', '.json', '.xml', '.log', '.sql'}
        if ext in text_formats:
            return True, f"File {ext} → Nén được 70-90%"
        
        # Estimate compression
        ratio = estimate_compression_ratio(file_path)
        
        if ratio < threshold:
            savings = (1 - ratio) * 100
            return True, f"Ước tính tiết kiệm: {savings:.0f}%"
        else:
            return False, f"Nén không hiệu quả ({ratio*100:.0f}% kích thước gốc)"
        
    except Exception as e:
        return False, f"Không thể kiểm tra: {str(e)}"


# Example usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python compression_optimizer.py <file_path> [method]")
        print("Methods: gzip (default), 7z")
        sys.exit(1)
    
    file_path = sys.argv[1]
    method = sys.argv[2] if len(sys.argv) > 2 else "gzip"
    
    # Check if should compress
    should, reason = should_compress(file_path)
    print(f"📊 {reason}")
    
    if not should:
        print("⚠️ Không khuyến nghị nén file này")
        sys.exit(0)
    
    print(f"\n🗜️ Đang nén {os.path.basename(file_path)}...")
    
    if method == "7z":
        success, output, msg = compress_file_7zip(file_path)
    else:
        def progress(current, total):
            pct = (current / total) * 100
            print(f"\r   📊 {pct:.1f}%", end='', flush=True)
        
        success, output, msg = compress_file_gzip(
            file_path,
            progress_callback=progress
        )
        print()  # New line
    
    print(msg)
    
    if success:
        print(f"\n📁 File nén: {output}")
