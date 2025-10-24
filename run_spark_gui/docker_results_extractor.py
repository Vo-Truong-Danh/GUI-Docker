"""
Docker Results Extractor
Copy analysis results từ Docker container sang host machine /tmp/
"""

import subprocess
import os
import shutil
from pathlib import Path

def extract_results_from_docker(container_name, output_dir="/tmp/"):
    """
    Extract ML analysis results từ Docker container
    
    Args:
        container_name: Tên Docker container (ví dụ: 'spark-master')
        output_dir: Thư mục đích trên host (default: /tmp/)
    
    Returns:
        dict: {'json': path_to_json, 'png': path_to_png, 'success': bool}
    """
    
    results = {
        'json': None,
        'png': None,
        'success': False,
        'messages': []
    }
    
    # Đảm bảo output directory tồn tại
    os.makedirs(output_dir, exist_ok=True)
    results['messages'].append(f"✅ Output directory: {output_dir}")
    
    # Files cần copy từ container
    # Bao gồm: 1 JSON file + 6 PNG files từ code7.py
    files_to_extract = [
        '/tmp/ml_analysis_summary.json',
        '/tmp/ml_analysis_results.png',          # Legacy (old single image)
        '/tmp/ml_result_1_customer_clustering.png',
        '/tmp/ml_result_2_regression_analysis.png',
        '/tmp/ml_result_3_product_clustering.png',
        '/tmp/ml_result_4_comprehensive_dashboard.png',
        '/tmp/ml_result_5_advanced_analytics.png',
        '/tmp/ml_result_6_trends_comparison.png'
    ]
    
    png_files = []  # List tất cả PNG files đã copy
    
    for container_file in files_to_extract:
        filename = os.path.basename(container_file)
        host_file = os.path.join(output_dir, filename)
        
        try:
            # Copy từ container sang host
            cmd = f'docker cp {container_name}:{container_file} "{host_file}"'
            
            print(f"📥 Copying {container_file} from container...")
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                if os.path.exists(host_file):
                    file_size = os.path.getsize(host_file)
                    results['messages'].append(f"✅ Copied {filename} ({file_size:,} bytes)")
                    
                    if 'json' in filename:
                        results['json'] = host_file
                    elif 'png' in filename:
                        png_files.append(host_file)
                        if 'ml_analysis_results.png' in filename:
                            results['png'] = host_file  # Legacy fallback
                else:
                    results['messages'].append(f"⚠️ File copied but not found: {host_file}")
            else:
                # File không tồn tại - bỏ qua (có thể là file không cần thiết)
                pass
        
        except subprocess.TimeoutExpired:
            results['messages'].append(f"⏱️ Timeout copying {filename}")
        except Exception as e:
            results['messages'].append(f"❌ Error copying {filename}: {e}")
    
    # Xác định thành công (có JSON + ít nhất 1 PNG)
    results['success'] = (results['json'] is not None and len(png_files) > 0)
    
    # Log số lượng PNG files đã copy
    results['messages'].append(f"📊 Total PNG files copied: {len(png_files)}")
    if len(png_files) > 0:
        results['messages'].append(f"   Files: {', '.join([os.path.basename(f) for f in png_files])}")
    
    return results


def get_container_tmp_files(container_name):
    """
    List tất cả files trong /tmp/ của container
    
    Returns:
        list: Danh sách files trong container /tmp/
    """
    try:
        cmd = f'docker exec {container_name} ls -la /tmp/'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            return result.stdout
        else:
            return f"Error: {result.stderr}"
    except Exception as e:
        return f"Exception: {e}"


def copy_docker_results_to_tmp(container_name, verbose=True):
    """
    Main function - Copy results từ Docker container
    
    Args:
        container_name: Tên container (ví dụ: 'spark-master')
        verbose: Print debug messages
    
    Returns:
        tuple: (success: bool, json_path: str, png_path: str)
    """
    
    if verbose:
        print("\n" + "=" * 70)
        print(f"🐳 Extracting results từ container: {container_name}")
        print("=" * 70)
    
    # Extract files
    result = extract_results_from_docker(container_name)
    
    # Print messages
    for msg in result['messages']:
        if verbose:
            print(msg)
    
    # Return results
    return (
        result['success'],
        result['json'],
        result['png']
    )


# Example usage
if __name__ == '__main__':
    import sys
    
    container = 'spark-master'  # Default container name
    
    if len(sys.argv) > 1:
        container = sys.argv[1]
    
    # Extract files
    success, json_file, png_file = copy_docker_results_to_tmp(container, verbose=True)
    
    print("\n" + "=" * 70)
    print("📊 Results:")
    print(f"  JSON: {json_file if json_file else 'NOT FOUND'}")
    print(f"  PNG:  {png_file if png_file else 'NOT FOUND'}")
    print(f"  Status: {'✅ Success' if success else '❌ Failed'}")
    print("=" * 70 + "\n")
