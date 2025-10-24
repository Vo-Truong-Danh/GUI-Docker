#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ML Analytics Tab - QUICK START EXAMPLE
Ví dụ nhanh cách sử dụng tab ML Analytics từ code
"""

# ============================================================
# EXAMPLE 1: Sử dụng MLAnalyticsTab trong Python code
# ============================================================

def example_1_basic_usage():
    """Ví dụ cơ bản: Tạo tab và chạy phân tích"""
    
    import tkinter as tk
    from tkinter import ttk
    from run_spark_gui.ml_analytics_tab import MLAnalyticsTab
    
    # Tạo window chính
    root = tk.Tk()
    root.title("ML Analytics Example")
    root.geometry("1200x800")
    
    # Tạo frame cho tab
    frame = ttk.Frame(root)
    frame.pack(fill=tk.BOTH, expand=True)
    
    # Tạo config đơn giản
    config = {
        'hdfs_host': 'hdfs://namenode:8020',
        'hdfs_default_path': '/user/spark/data',
        'compose_file': '/tmp/'
    }
    
    # Callback functions
    def on_status_update(message):
        print(f"Status: {message}")
    
    def on_log_append(message):
        print(f"Log: {message}")
    
    # Tạo tab ML Analytics
    ml_tab = MLAnalyticsTab(
        parent_frame=frame,
        config=config,
        status_callback=on_status_update,
        log_callback=on_log_append
    )
    
    root.mainloop()


# ============================================================
# EXAMPLE 2: Chạy phân tích programmatically
# ============================================================

def example_2_programmatic_analysis():
    """Ví dụ: Chạy phân tích theo chương trình"""
    
    from run_spark_gui.ml_analytics_tab import MLAnalyticsTab
    import tkinter as tk
    from tkinter import ttk
    
    root = tk.Tk()
    frame = ttk.Frame(root)
    frame.pack(fill=tk.BOTH, expand=True)
    
    config = {'hdfs_host': 'hdfs://namenode:8020'}
    
    ml_tab = MLAnalyticsTab(
        parent_frame=frame,
        config=config
    )
    
    # Đặt đường dẫn input/output
    ml_tab.input_path_var.set("hdfs://namenode:8020/input/online_retail_II.csv")
    ml_tab.output_path_var.set("/tmp/ml_results/")
    
    # Chọn loại phân tích
    ml_tab.clustering_var.set(True)      # K-Means
    ml_tab.regression_var.set(True)      # Linear Regression
    ml_tab.visualization_var.set(True)   # Charts
    
    # Chạy phân tích
    ml_tab.run_analysis()
    
    root.mainloop()


# ============================================================
# EXAMPLE 3: Batch Processing - Chạy nhiều file
# ============================================================

def example_3_batch_processing():
    """Ví dụ: Xử lý batch - phân tích nhiều file"""
    
    import os
    import time
    from run_spark_gui.ml_analytics_tab import MLAnalyticsTab
    import tkinter as tk
    from tkinter import ttk
    
    # Danh sách file cần phân tích
    input_files = [
        "hdfs://namenode:8020/input/retail_2024_Q1.csv",
        "hdfs://namenode:8020/input/retail_2024_Q2.csv",
        "hdfs://namenode:8020/input/retail_2024_Q3.csv",
    ]
    
    output_base = "/tmp/ml_batch_results/"
    
    root = tk.Tk()
    frame = ttk.Frame(root)
    frame.pack(fill=tk.BOTH, expand=True)
    
    config = {'hdfs_host': 'hdfs://namenode:8020'}
    ml_tab = MLAnalyticsTab(parent_frame=frame, config=config)
    
    # Xử lý từng file
    for idx, input_file in enumerate(input_files, 1):
        print(f"\n📊 Processing {idx}/{len(input_files)}: {input_file}")
        
        # Tạo output folder cho file này
        output_dir = os.path.join(output_base, f"result_{idx}/")
        os.makedirs(output_dir, exist_ok=True)
        
        # Đặt đường dẫn
        ml_tab.input_path_var.set(input_file)
        ml_tab.output_path_var.set(output_dir)
        
        # Chạy phân tích
        ml_tab.run_analysis()
        
        # Chờ hoàn thành
        while ml_tab.is_running:
            root.update()
            time.sleep(1)
        
        print(f"✅ Complete: {output_dir}")
    
    print(f"\n✅ Batch processing complete! Results in {output_base}")
    root.destroy()


# ============================================================
# EXAMPLE 4: Custom Configuration & Advanced Options
# ============================================================

def example_4_advanced_config():
    """Ví dụ: Cấu hình nâng cao"""
    
    from run_spark_gui.ml_analytics_tab import MLAnalyticsTab
    import tkinter as tk
    from tkinter import ttk
    
    root = tk.Tk()
    frame = ttk.Frame(root)
    frame.pack(fill=tk.BOTH, expand=True)
    
    # Cấu hình chi tiết
    config = {
        'hdfs_host': 'hdfs://namenode:8020',
        'hdfs_default_path': '/user/spark/data',
        'hdfs_container': 'namenode',
        'compose_file': '/opt/docker-compose.yml',
        
        # Spark config
        'spark_master': 'spark://spark-master:7077',
        'spark_executor_memory': '4G',
        'spark_executor_cores': '4',
        
        # ML config
        'kmeans_k': 3,
        'bisecting_kmeans_k': 4,
        'random_forest_trees': 20,
        'max_iterations': 100,
        
        # Output config
        'output_dpi': 300,
        'output_format': 'png',
        'include_statistics': True,
    }
    
    def on_status(msg):
        print(f"[STATUS] {msg}")
    
    def on_log(msg):
        print(f"[LOG] {msg}")
    
    ml_tab = MLAnalyticsTab(
        parent_frame=frame,
        config=config,
        status_callback=on_status,
        log_callback=on_log
    )
    
    # Thiết lập thêm
    ml_tab.input_path_var.set("hdfs://namenode:8020/data/online_retail.csv")
    ml_tab.output_path_var.set("/mnt/nfs/ml_results/")
    
    # Chạy
    ml_tab.run_analysis()
    
    root.mainloop()


# ============================================================
# EXAMPLE 5: Integration với Spark Runner Tab
# ============================================================

def example_5_spark_integration():
    """Ví dụ: Tích hợp với Spark Runner"""
    
    from run_spark_gui.ml_analytics_tab import MLAnalyticsTab
    from run_spark_gui.spark_runner_tab_v4_clean import SparkRunnerTabV4
    import tkinter as tk
    from tkinter import ttk
    
    root = tk.Tk()
    root.title("Spark + ML Analytics Integration")
    root.geometry("1200x800")
    
    # Tạo notebook
    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True)
    
    # Tab 1: Spark Runner
    spark_frame = ttk.Frame(notebook)
    notebook.add(spark_frame, text="Spark Runner")
    
    # Tab 2: ML Analytics
    ml_frame = ttk.Frame(notebook)
    notebook.add(ml_frame, text="ML Analytics")
    
    config = {
        'hdfs_host': 'hdfs://namenode:8020',
        'master': 'spark://spark-master:7077'
    }
    
    # Tạo ML Analytics tab
    ml_tab = MLAnalyticsTab(
        parent_frame=ml_frame,
        config=config
    )
    
    # Kết nối với Spark Runner nếu cần
    # ml_tab.spark_runner = spark_runner_instance
    
    root.mainloop()


# ============================================================
# EXAMPLE 6: Output & Results Processing
# ============================================================

def example_6_results_processing():
    """Ví dụ: Xử lý kết quả phân tích"""
    
    import json
    import os
    from PIL import Image
    
    results_dir = "/tmp/ml_results/"
    
    # Đọc summary JSON
    summary_file = os.path.join(results_dir, "ml_analysis_summary.json")
    
    with open(summary_file, 'r') as f:
        results = json.load(f)
    
    # Xử lý results
    print(f"📊 Analysis Timestamp: {results['timestamp']}")
    print(f"📈 Total Records: {results['total_records']:,}")
    print(f"💰 Total Revenue: ${results['total_revenue']:,.2f}")
    print(f"🌍 Countries: {results['num_countries']}")
    print(f"📦 Products: {results['num_products']}")
    
    # Top countries
    print("\n🏆 Top 5 Countries:")
    for idx, country in enumerate(results['top_countries'][:5], 1):
        print(f"  {idx}. {country['Country']}: ${country['Total_Revenue']:,.2f}")
    
    # Top products
    print("\n📦 Top 5 Products:")
    for idx, product in enumerate(results['top_products'][:5], 1):
        print(f"  {idx}. {product['Description']}: ${product['Total_Revenue']:,.2f}")
    
    # Mở chart
    chart_file = os.path.join(results_dir, "ml_analysis_results.png")
    if os.path.exists(chart_file):
        img = Image.open(chart_file)
        print(f"\n🖼️ Chart size: {img.size}, DPI: {img.info.get('dpi', 'N/A')}")
        # img.show()  # Uncomment to display


# ============================================================
# EXAMPLE 7: Error Handling & Recovery
# ============================================================

def example_7_error_handling():
    """Ví dụ: Xử lý lỗi"""
    
    from run_spark_gui.ml_analytics_tab import MLAnalyticsTab
    import tkinter as tk
    from tkinter import ttk
    import threading
    
    root = tk.Tk()
    frame = ttk.Frame(root)
    frame.pack(fill=tk.BOTH, expand=True)
    
    config = {'hdfs_host': 'hdfs://namenode:8020'}
    
    ml_tab = MLAnalyticsTab(
        parent_frame=frame,
        config=config
    )
    
    def run_with_error_handling():
        try:
            # Kiểm tra input
            input_file = ml_tab.input_path_var.get()
            output_dir = ml_tab.output_path_var.get()
            
            if not input_file:
                ml_tab.log_message("error", "❌ Input file not specified")
                return
            
            if not output_dir:
                ml_tab.log_message("error", "❌ Output directory not specified")
                return
            
            # Chạy phân tích
            ml_tab.run_analysis()
            
        except Exception as e:
            ml_tab.log_message("error", f"❌ Error: {str(e)}")
            import traceback
            ml_tab.log_message("error", traceback.format_exc())
    
    # Chạy trong background thread
    thread = threading.Thread(target=run_with_error_handling, daemon=True)
    thread.start()
    
    root.mainloop()


# ============================================================
# EXAMPLE 8: Performance & Optimization
# ============================================================

def example_8_performance():
    """Ví dụ: Tối ưu hiệu suất"""
    
    from run_spark_gui.ml_analytics_tab import MLAnalyticsTab
    import tkinter as tk
    from tkinter import ttk
    import time
    
    root = tk.Tk()
    frame = ttk.Frame(root)
    frame.pack(fill=tk.BOTH, expand=True)
    
    # Cấu hình tối ưu
    config = {
        'hdfs_host': 'hdfs://namenode:8020',
        'spark_executor_memory': '8G',      # Tăng memory
        'spark_executor_cores': '8',         # Tăng cores
        'shuffle_partitions': 200,           # Tối ưu partitions
    }
    
    ml_tab = MLAnalyticsTab(parent_frame=frame, config=config)
    
    # Đo thời gian
    ml_tab.input_path_var.set("hdfs://namenode:8020/big_data.csv")
    ml_tab.output_path_var.set("/ssd/fast_output/")
    
    start_time = time.time()
    ml_tab.run_analysis()
    
    # Chờ xong
    while ml_tab.is_running:
        root.update()
        time.sleep(1)
    
    elapsed = time.time() - start_time
    print(f"⏱️ Analysis completed in {elapsed:.2f} seconds")
    
    root.destroy()


# ============================================================
# EXAMPLE 9: CLI Usage
# ============================================================

if __name__ == "__main__":
    """
    Chạy ví dụ từ command line:
    
    python ml_analytics_examples.py --example 1
    python ml_analytics_examples.py --example 2
    python ml_analytics_examples.py --example 3
    ...
    """
    
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--example":
        example_num = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        
        examples = {
            1: example_1_basic_usage,
            2: example_2_programmatic_analysis,
            3: example_3_batch_processing,
            4: example_4_advanced_config,
            5: example_5_spark_integration,
            6: example_6_results_processing,
            7: example_7_error_handling,
            8: example_8_performance,
        }
        
        if example_num in examples:
            print(f"🚀 Running Example {example_num}...\n")
            examples[example_num]()
        else:
            print(f"❌ Example {example_num} not found")
    else:
        print("""
📚 ML Analytics Tab - EXAMPLES

Usage:
    python ml_analytics_examples.py --example <number>

Available Examples:
    1. Basic Usage - Tạo tab cơ bản
    2. Programmatic - Chạy từ code
    3. Batch Processing - Xử lý nhiều file
    4. Advanced Config - Cấu hình nâng cao
    5. Spark Integration - Tích hợp Spark
    6. Results Processing - Xử lý kết quả
    7. Error Handling - Xử lý lỗi
    8. Performance - Tối ưu hiệu suất

Examples:
    python ml_analytics_examples.py --example 1
    python ml_analytics_examples.py --example 3
        """)
