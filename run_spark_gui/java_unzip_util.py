"""
Java-based Unzip Utility for Hadoop Containers
Version: 5.1.1

This module provides ZIP extraction using Java (which is already available in Hadoop containers)
instead of requiring the 'unzip' command to be installed.

Author: GitHub Copilot
Date: October 13, 2025
"""

import subprocess

# Import subprocess utilities for hidden console windows
try:
    from subprocess_utils import run_hidden, popen_hidden
except ImportError:
    def run_hidden(*args, **kwargs):
        return run_hidden(*args, **kwargs)
    def popen_hidden(*args, **kwargs):
        return popen_hidden(*args, **kwargs)
import tempfile
from pathlib import Path
from typing import Tuple, Optional, Callable


# Java code for unzipping (will be written to container and executed)
JAVA_UNZIP_CODE = '''
import java.io.*;
import java.util.zip.*;

public class SimpleUnzip {
    public static void main(String[] args) {
        if (args.length != 2) {
            System.err.println("Usage: java SimpleUnzip <zip_file> <output_dir>");
            System.exit(1);
        }
        
        String zipFilePath = args[0];
        String outputDir = args[1];
        
        try {
            unzip(zipFilePath, outputDir);
            System.out.println("SUCCESS: Extracted " + zipFilePath + " to " + outputDir);
        } catch (Exception e) {
            System.err.println("ERROR: " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }
    }
    
    private static void unzip(String zipFilePath, String outputDir) throws IOException {
        File destDir = new File(outputDir);
        if (!destDir.exists()) {
            destDir.mkdirs();
        }
        
        byte[] buffer = new byte[8192];
        ZipInputStream zis = new ZipInputStream(new FileInputStream(zipFilePath));
        ZipEntry zipEntry = zis.getNextEntry();
        int count = 0;
        
        while (zipEntry != null) {
            File newFile = newFile(destDir, zipEntry);
            
            if (zipEntry.isDirectory()) {
                if (!newFile.isDirectory() && !newFile.mkdirs()) {
                    throw new IOException("Failed to create directory " + newFile);
                }
            } else {
                // Create parent directories
                File parent = newFile.getParentFile();
                if (!parent.isDirectory() && !parent.mkdirs()) {
                    throw new IOException("Failed to create directory " + parent);
                }
                
                // Write file
                FileOutputStream fos = new FileOutputStream(newFile);
                int len;
                while ((len = zis.read(buffer)) > 0) {
                    fos.write(buffer, 0, len);
                }
                fos.close();
                count++;
            }
            
            zipEntry = zis.getNextEntry();
        }
        
        zis.closeEntry();
        zis.close();
        
        System.out.println("Extracted " + count + " files");
    }
    
    private static File newFile(File destinationDir, ZipEntry zipEntry) throws IOException {
        File destFile = new File(destinationDir, zipEntry.getName());
        
        String destDirPath = destinationDir.getCanonicalPath();
        String destFilePath = destFile.getCanonicalPath();
        
        if (!destFilePath.startsWith(destDirPath + File.separator)) {
            throw new IOException("Entry is outside of the target dir: " + zipEntry.getName());
        }
        
        return destFile;
    }
}
'''


def check_java_available(container: str, log_callback: Optional[Callable] = None) -> Tuple[bool, str]:
    """
    Check if Java is available in the container
    
    Args:
        container: Container name
        log_callback: Optional logging function
    
    Returns:
        Tuple of (available: bool, java_version: str)
    """
    try:
        result = run_hidden(
            ['docker', 'exec', container, 'java', '-version'],
            capture_output=True,
            timeout=10,
            text=True
        )
        
        # Java -version outputs to stderr (not stdout)
        version_output = result.stderr.strip()
        
        if result.returncode == 0 and version_output:
            if log_callback:
                log_callback(f'✅ Java is available in container', 'success')
                # Parse version (usually first line)
                version_line = version_output.split('\n')[0] if version_output else 'unknown'
                log_callback(f'   Version: {version_line}', 'info')
            
            return True, version_line
        else:
            if log_callback:
                log_callback(f'❌ Java not found in container', 'error')
            return False, "Java not found"
    
    except subprocess.TimeoutExpired:
        if log_callback:
            log_callback(f'⏱️ Timeout checking Java', 'warning')
        return False, "Timeout"
    
    except Exception as e:
        if log_callback:
            log_callback(f'❌ Error checking Java: {e}', 'error')
        return False, str(e)


def setup_java_unzip(container: str, log_callback: Optional[Callable] = None) -> bool:
    """
    Setup Java unzip utility in container (one-time setup)
    
    Args:
        container: Container name
        log_callback: Optional logging function
    
    Returns:
        bool: True if setup successful
    """
    try:
        if log_callback:
            log_callback('📦 Setting up Java unzip utility...', 'info')
        
        # Step 1: Create temp directory in container
        mkdir_cmd = ['docker', 'exec', container, 'mkdir', '-p', '/tmp/java_utils']
        run_hidden(mkdir_cmd, capture_output=True, timeout=10)
        
        # Step 2: Write Java code to container
        # Use echo to write the Java code (multi-line)
        write_cmd = ['docker', 'exec', container, 'sh', '-c', 
                     f'cat > /tmp/java_utils/SimpleUnzip.java << \'EOFMARKER\'\n{JAVA_UNZIP_CODE}\nEOFMARKER']
        
        result = run_hidden(write_cmd, capture_output=True, timeout=10, text=True)
        
        if result.returncode != 0:
            if log_callback:
                log_callback(f'❌ Failed to write Java code: {result.stderr}', 'error')
            return False
        
        if log_callback:
            log_callback('   ✓ Java code written to container', 'success')
        
        # Step 3: Compile Java code
        if log_callback:
            log_callback('   ⚙️ Compiling Java code...', 'info')
        
        compile_cmd = ['docker', 'exec', container, 'javac', '/tmp/java_utils/SimpleUnzip.java']
        result = run_hidden(compile_cmd, capture_output=True, timeout=30, text=True)
        
        if result.returncode != 0:
            if log_callback:
                log_callback(f'❌ Java compilation failed: {result.stderr}', 'error')
            return False
        
        if log_callback:
            log_callback('   ✓ Java code compiled successfully', 'success')
        
        # Step 4: Verify .class file exists
        verify_cmd = ['docker', 'exec', container, 'test', '-f', '/tmp/java_utils/SimpleUnzip.class']
        result = run_hidden(verify_cmd, capture_output=True, timeout=10)
        
        if result.returncode != 0:
            if log_callback:
                log_callback(f'❌ Compiled .class file not found', 'error')
            return False
        
        if log_callback:
            log_callback('✅ Java unzip utility ready!', 'success')
        
        return True
    
    except subprocess.TimeoutExpired:
        if log_callback:
            log_callback(f'⏱️ Timeout during setup', 'error')
        return False
    
    except Exception as e:
        if log_callback:
            log_callback(f'❌ Setup error: {e}', 'error')
        return False


def unzip_with_java(
    container: str,
    zip_file_path: str,
    output_dir: str,
    log_callback: Optional[Callable] = None
) -> Tuple[bool, str]:
    """
    Unzip a file using Java in the container
    
    Args:
        container: Container name
        zip_file_path: Path to ZIP file in container (e.g., '/tmp/data.zip')
        output_dir: Output directory in container (e.g., '/tmp/extracted')
        log_callback: Optional logging function
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        # Check if Java unzip utility is set up
        check_cmd = ['docker', 'exec', container, 'test', '-f', '/tmp/java_utils/SimpleUnzip.class']
        result = run_hidden(check_cmd, capture_output=True, timeout=10)
        
        if result.returncode != 0:
            # Setup not done yet, do it now
            if log_callback:
                log_callback('⚙️ Java unzip utility not found, setting up...', 'info')
            
            if not setup_java_unzip(container, log_callback):
                return False, "Failed to setup Java unzip utility"
        
        # Create output directory
        mkdir_cmd = ['docker', 'exec', container, 'mkdir', '-p', output_dir]
        run_hidden(mkdir_cmd, capture_output=True, timeout=10)
        
        # Run Java unzip
        if log_callback:
            log_callback(f'📦 Extracting with Java: {zip_file_path}', 'info')
        
        unzip_cmd = [
            'docker', 'exec', container, 'java',
            '-cp', '/tmp/java_utils',
            'SimpleUnzip',
            zip_file_path,
            output_dir
        ]
        
        result = run_hidden(unzip_cmd, capture_output=True, timeout=300, text=True)
        
        if result.returncode == 0:
            # Parse success message (e.g., "Extracted 42 files")
            output = result.stdout.strip()
            
            if log_callback:
                log_callback(f'✅ Extraction successful!', 'success')
                if output:
                    # Show extracted file count
                    for line in output.split('\n'):
                        if line.strip():
                            log_callback(f'   {line}', 'info')
            
            return True, output
        else:
            error_msg = result.stderr.strip() if result.stderr else "Unknown error"
            
            if log_callback:
                log_callback(f'❌ Extraction failed: {error_msg}', 'error')
            
            return False, error_msg
    
    except subprocess.TimeoutExpired:
        msg = "Extraction timeout (>300s)"
        if log_callback:
            log_callback(f'⏱️ {msg}', 'error')
        return False, msg
    
    except Exception as e:
        msg = f"Extraction error: {e}"
        if log_callback:
            log_callback(f'❌ {msg}', 'error')
        return False, msg


def extract_and_upload_to_hdfs(
    container: str,
    zip_file_path: str,
    hdfs_target_dir: str,
    log_callback: Optional[Callable] = None
) -> Tuple[bool, str, int]:
    """
    Extract ZIP file and upload contents to HDFS
    
    Args:
        container: Container name
        zip_file_path: Path to ZIP file in container (e.g., '/tmp/data.zip')
        hdfs_target_dir: Target directory in HDFS (e.g., '/input/data')
        log_callback: Optional logging function
    
    Returns:
        Tuple of (success: bool, message: str, files_uploaded: int)
    """
    import time
    
    try:
        # Step 1: Extract to temp directory
        extract_dir = f'/tmp/extracted_{int(time.time())}'
        
        if log_callback:
            log_callback(f'📦 Step 1: Extracting ZIP file with Java...', 'info')
        
        success, msg = unzip_with_java(container, zip_file_path, extract_dir, log_callback)
        
        if not success:
            return False, f"Extraction failed: {msg}", 0
        
        # Step 2: Create HDFS directory
        if log_callback:
            log_callback(f'📁 Step 2: Creating HDFS directory...', 'info')
        
        mkdir_cmd = ['docker', 'exec', container, 'hdfs', 'dfs', '-mkdir', '-p', hdfs_target_dir]
        run_hidden(mkdir_cmd, capture_output=True, timeout=30)
        
        # Step 3: List extracted files
        if log_callback:
            log_callback(f'📋 Step 3: Listing extracted files...', 'info')
        
        ls_cmd = ['docker', 'exec', container, 'sh', '-c', f'find {extract_dir} -type f']
        result = run_hidden(ls_cmd, capture_output=True, timeout=30, text=True)
        
        if result.returncode != 0 or not result.stdout.strip():
            return False, "No files found after extraction", 0
        
        extracted_files = [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
        
        if log_callback:
            log_callback(f'   Found {len(extracted_files)} file(s)', 'info')
        
        # Step 4: Upload each file to HDFS
        if log_callback:
            log_callback(f'☁️ Step 4: Uploading to HDFS...', 'info')
        
        uploaded = 0
        for file_path in extracted_files:
            # Get relative path (for HDFS structure)
            relative_path = file_path.replace(extract_dir, '').lstrip('/')
            hdfs_file_path = f'{hdfs_target_dir}/{relative_path}'
            
            # Create parent directory in HDFS
            hdfs_parent = '/'.join(hdfs_file_path.split('/')[:-1])
            mkdir_cmd = ['docker', 'exec', container, 'hdfs', 'dfs', '-mkdir', '-p', hdfs_parent]
            run_hidden(mkdir_cmd, capture_output=True, timeout=30)
            
            # Upload file
            put_cmd = ['docker', 'exec', container, 'hdfs', 'dfs', '-put', '-f', file_path, hdfs_file_path]
            result = run_hidden(put_cmd, capture_output=True, timeout=120, text=True)
            
            if result.returncode == 0:
                uploaded += 1
                if log_callback:
                    log_callback(f'   ✓ Uploaded: {relative_path}', 'success')
            else:
                if log_callback:
                    error = result.stderr.strip() if result.stderr else "Unknown error"
                    log_callback(f'   ✗ Failed: {relative_path} - {error}', 'warning')
        
        # Step 5: Cleanup
        if log_callback:
            log_callback(f'🧹 Step 5: Cleaning up temp files...', 'info')
        
        rm_cmd = ['docker', 'exec', container, 'rm', '-rf', extract_dir]
        run_hidden(rm_cmd, capture_output=True, timeout=30)
        
        if log_callback:
            log_callback(f'✅ Upload complete: {uploaded}/{len(extracted_files)} files', 'success')
        
        return True, f"Uploaded {uploaded}/{len(extracted_files)} files", uploaded
    
    except Exception as e:
        if log_callback:
            log_callback(f'❌ Error: {e}', 'error')
        return False, str(e), 0


# Test code
if __name__ == '__main__':
    print("=" * 80)
    print("JAVA UNZIP UTILITY TEST")
    print("=" * 80)
    
    def test_log(msg, tag):
        print(f"[{tag.upper():8}] {msg}")
    
    container = 'namenode'
    
    # Test 1: Check Java availability
    print("\n1. Checking Java availability...")
    available, version = check_java_available(container, test_log)
    print(f"   Result: {'Available' if available else 'Not Available'}")
    
    if available:
        # Test 2: Setup Java unzip utility
        print("\n2. Setting up Java unzip utility...")
        success = setup_java_unzip(container, test_log)
        print(f"   Result: {'Success' if success else 'Failed'}")
        
        if success:
            print("\n✅ Java unzip utility is ready to use!")
            print("\nUsage example:")
            print("  from java_unzip_util import unzip_with_java")
            print("  success, msg = unzip_with_java(")
            print("      container='namenode',")
            print("      zip_file_path='/tmp/data.zip',")
            print("      output_dir='/tmp/extracted',")
            print("      log_callback=your_log_function")
            print("  )")
    
    print("\n" + "=" * 80)
