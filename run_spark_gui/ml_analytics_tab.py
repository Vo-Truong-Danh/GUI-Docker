"""
ML Analytics Tab - Big Data Analysis with Machine Learning
Tích hợp Machine Learning nâng cao từ code7.py vào GUI
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import json
import subprocess
import threading
import sys
from pathlib import Path
from datetime import datetime
import traceback

# Import HTML Dashboard Helper
try:
    from html_dashboard_helper import HTMLDashboardHelper
    HTML_DASHBOARD_AVAILABLE = True
except ImportError:
    HTML_DASHBOARD_AVAILABLE = False
    HTMLDashboardHelper = None

class MLAnalyticsTab:
    """
    Tab để chạy phân tích Big Data với Machine Learning
    - K-Means Clustering cho Customer Segmentation
    - Linear Regression & Random Forest cho Revenue Prediction
    - Bisecting K-Means cho Product Clustering
    - Visualization nâng cao
    """
    
    def __init__(self, parent_frame, config, status_callback=None, log_callback=None):
        self.parent = parent_frame
        self.config = config
        self.update_status = status_callback or (lambda x: None)
        self.append_log = log_callback or (lambda x: None)
        
        self.is_running = False
        self.process = None
        self.output_dir = "/tmp/"
        
        self.setup_ui()
    
    def setup_ui(self):
        """Tạo UI cho tab ML Analytics"""
        
        # Main container
        main_container = ttk.Frame(self.parent)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Header
        header_frame = ttk.LabelFrame(main_container, text="🤖 ML Analytics Configuration", padding=10)
        header_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Input file selection
        input_frame = ttk.Frame(header_frame)
        input_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(input_frame, text="📁 Input File (CSV):", font=('Segoe UI', 9)).pack(side=tk.LEFT, padx=5)
        self.input_path_var = tk.StringVar(value="hdfs://namenode:8020/input/online_retail_II.csv")
        ttk.Entry(input_frame, textvariable=self.input_path_var, width=50).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(input_frame, text="Browse", command=self.browse_input).pack(side=tk.LEFT, padx=2)
        
        # Output directory
        output_frame = ttk.Frame(header_frame)
        output_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(output_frame, text="📂 Output Directory:", font=('Segoe UI', 9)).pack(side=tk.LEFT, padx=5)
        self.output_path_var = tk.StringVar(value="/tmp/")
        ttk.Entry(output_frame, textvariable=self.output_path_var, width=50).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(output_frame, text="Browse", command=self.browse_output).pack(side=tk.LEFT, padx=2)
        
        # ML Analysis Script Selection (NEW FEATURE!)
        script_frame = ttk.Frame(header_frame)
        script_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(script_frame, text="🐍 ML Script (.py):", font=('Segoe UI', 9)).pack(side=tk.LEFT, padx=5)
        self.script_path_var = tk.StringVar(value="code7.py")
        ttk.Entry(script_frame, textvariable=self.script_path_var, width=50).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(script_frame, text="Browse", command=self.browse_script).pack(side=tk.LEFT, padx=2)
        
        # Info label
        info_label = ttk.Label(header_frame, text="💡 Tip: Select a Python ML script to use instead of default code7.py", 
                              font=('Segoe UI', 8), foreground='#0066CC')
        info_label.pack(anchor=tk.W, padx=5, pady=2)
        
        # Analysis Options
        options_frame = ttk.LabelFrame(main_container, text="⚙️ Analysis Options", padding=10)
        options_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Checkboxes for analysis types
        self.clustering_var = tk.BooleanVar(value=True)
        self.regression_var = tk.BooleanVar(value=True)
        self.visualization_var = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(options_frame, text="✓ Customer Segmentation (K-Means)", 
                       variable=self.clustering_var).pack(anchor=tk.W, pady=3)
        ttk.Checkbutton(options_frame, text="✓ Revenue Prediction (Linear Regression + Random Forest)", 
                       variable=self.regression_var).pack(anchor=tk.W, pady=3)
        ttk.Checkbutton(options_frame, text="✓ Advanced Visualization (6 charts)", 
                       variable=self.visualization_var).pack(anchor=tk.W, pady=3)
        
        # Control buttons
        button_frame = ttk.Frame(main_container)
        button_frame.pack(fill=tk.X, padx=5, pady=10)
        
        self.run_button = ttk.Button(button_frame, text="▶️ Run Analysis", 
                                      command=self.run_analysis, width=20)
        self.run_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="⏹️ Stop", 
                                       command=self.stop_analysis, width=20, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="📂 Open Output Folder", 
                  command=self.open_output_folder, width=20).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="📊 Open HTML Dashboard", 
                  command=self.open_html_dashboard, width=20).pack(side=tk.LEFT, padx=5)
        
        # Progress section
        progress_frame = ttk.LabelFrame(main_container, text="📊 Progress", padding=10)
        progress_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                           maximum=100, mode='determinate', length=400)
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        self.progress_label = ttk.Label(progress_frame, text="Ready", font=('Segoe UI', 9))
        self.progress_label.pack(anchor=tk.W)
        
        # Output console
        console_frame = ttk.LabelFrame(main_container, text="📝 Console Output", padding=5)
        console_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.console = scrolledtext.ScrolledText(console_frame, height=15, width=80,
                                                 bg='#1E1E1E', fg='#00FF00', 
                                                 font=('Consolas', 9), wrap=tk.WORD)
        self.console.pack(fill=tk.BOTH, expand=True)
        
        # Configure console tags
        self.console.tag_config('info', foreground='#00FF00')
        self.console.tag_config('warning', foreground='#FFD700')
        self.console.tag_config('error', foreground='#FF6B6B')
        self.console.tag_config('success', foreground='#00FF00')
        
        # Results section
        results_frame = ttk.LabelFrame(main_container, text="📈 Results", padding=10)
        results_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.results_text = tk.Text(results_frame, height=8, width=80, 
                                    bg='#F6F8FA', fg='#24292F',
                                    font=('Segoe UI', 9), state=tk.DISABLED)
        results_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        self.results_text.config(yscrollcommand=results_scrollbar.set)
        
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.log_message("info", "✅ ML Analytics Tab initialized")
        self.log_message("info", "Ready to run analysis on Big Data files")
    
    def log_message(self, tag, message):
        """Add message to console with tag"""
        self.console.config(state=tk.NORMAL)
        self.console.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n", tag)
        self.console.see(tk.END)
        self.console.config(state=tk.DISABLED)
        self.console.update()
    
    def browse_input(self):
        """Browse for input CSV file"""
        file = filedialog.askopenfilename(
            title="Select Input CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file:
            self.input_path_var.set(file)
    
    def browse_output(self):
        """Browse for output directory"""
        folder = filedialog.askdirectory(title="Select Output Directory")
        if folder:
            self.output_path_var.set(folder)
    
    def browse_script(self):
        """Browse for ML analysis Python script"""
        file = filedialog.askopenfilename(
            title="Select ML Analysis Script",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")]
        )
        if file:
            self.script_path_var.set(file)
            self.log_message("info", f"📄 Selected ML script: {Path(file).name}")
    
    def open_output_folder(self):
        """Open output folder in explorer"""
        output_dir = self.output_path_var.get()
        if os.path.exists(output_dir):
            if sys.platform == 'win32':
                os.startfile(output_dir)
            elif sys.platform == 'darwin':
                subprocess.Popen(['open', output_dir])
            else:
                subprocess.Popen(['xdg-open', output_dir])
        else:
            messagebox.showerror("Error", f"Output directory not found: {output_dir}")
    
    def open_html_dashboard(self):
        """Open ML Analytics HTML Dashboard"""
        if not HTML_DASHBOARD_AVAILABLE:
            messagebox.showerror("Error", 
                "HTML Dashboard helper not available.\nPlease ensure html_dashboard_helper.py is in the same directory.")
            return
        
        # FIRST: Extract from Docker
        self.log_message("info", "[INFO] Extracting results from Docker container...")
        
        try:
            from docker_results_extractor import copy_docker_results_to_tmp
            
            container = self.config.get('container', 'spark-master')
            self.log_message("info", f"[INFO] Container: {container}")
            
            success, json_file, png_file = copy_docker_results_to_tmp(container, verbose=False)
            
            if success:
                self.log_message("success", "[OK] Results extracted from Docker!")
            else:
                self.log_message("warning", "[WARNING] No results in container yet")
                self.log_message("info", "[INFO] Run Spark Runner tab first to generate analysis")
        
        except Exception as e:
            self.log_message("error", f"[ERROR] Extraction failed: {e}")
        
        # THEN: Open dashboard
        try:
            # Find dashboard HTML file - prefer index2_1.html (new) over ml_analytics_dashboard.html (old)
            current_dir = Path(__file__).parent.parent
            
            # Try new dashboard first
            dashboard_path = current_dir / 'index2_1.html'
            if not dashboard_path.exists():
                # Fallback to old dashboard
                dashboard_path = current_dir / 'ml_analytics_dashboard.html'
            
            if not dashboard_path.exists():
                messagebox.showerror("Error", 
                    f"Dashboard file not found:\n{dashboard_path}\n\n"
                    "Please run ML Analysis first to generate the dashboard.")
                return
            
            # Initialize helper
            helper = HTMLDashboardHelper(str(dashboard_path))
            
            # Open dashboard (will auto-load data with retry logic)
            self.log_message("info", "[INFO] Opening HTML Dashboard...")
            
            if helper.open_dashboard(new_window=True):
                self.log_message("success", "[OK] Dashboard opened in browser")
            else:
                messagebox.showerror("Error", "Failed to open dashboard")
        
        except Exception as e:
            self.log_message("error", f"Error opening dashboard: {e}")
            messagebox.showerror("Error", f"Error opening dashboard:\n{e}")
    
    def run_analysis(self):
        """Open ML Analytics Dashboard - Extract from Docker first"""
        output_dir = self.output_path_var.get() or "/tmp/"
        
        self.log_message("info", "[INFO] Sao chep ket qua tu Docker container...")
        
        try:
            # Import extractor
            from docker_results_extractor import copy_docker_results_to_tmp
            
            # Get container name tu config
            container = self.config.get('container', 'spark-master')
            
            self.log_message("info", f"[INFO] Container: {container}")
            
            # Extract files tu container
            success, json_file, png_file = copy_docker_results_to_tmp(container, verbose=False)
            
            if success:
                self.log_message("success", "[OK] Ket qua da sao chep thanh cong!")
                if json_file:
                    self.log_message("success", f"[OK] JSON: {json_file}")
                if png_file:
                    self.log_message("success", f"[OK] PNG: {png_file}")
            else:
                self.log_message("warning", "[WARNING] Khong tim thay ket qua trong container")
                self.log_message("info", "[INFO] Hay chay analysis tu Spark Runner tab truoc")
        
        except ImportError:
            self.log_message("error", "[ERROR] Khong tim thay docker_results_extractor")
            return
        except Exception as e:
            self.log_message("error", f"[ERROR] Loi: {e}")
        
        # Open dashboard
        self.log_message("info", "[INFO] Mo ML Analytics Dashboard...")
        
        try:
            from html_dashboard_helper import HTMLDashboardHelper
            helper = HTMLDashboardHelper()
            helper.open_dashboard()
            self.log_message("success", "[OK] Dashboard mo thanh cong!")
        except Exception as e:
            self.log_message("error", f"[ERROR] Loi: {e}")
            messagebox.showerror("Error", f"Cannot open Dashboard: {str(e)}")

    def _execute_analysis(self, input_path, output_dir, script_path):
        """Execute the ML analysis"""
        try:
            self.log_message("info", "🚀 Starting ML Analysis...")
            self.update_status("Running ML Analysis...")
            
            self.progress_var.set(10)
            self.progress_label.config(text="10% - Initializing Spark Session")
            
            self.log_message("info", f"Input: {input_path}")
            self.log_message("info", f"Output: {output_dir}")
            
            # Check if custom script exists and use it
            if script_path and os.path.exists(script_path):
                self.log_message("info", f"📄 Using custom script: {script_path}")
                with open(script_path, 'r', encoding='utf-8') as f:
                    analysis_script = f.read()
                # Add input/output params if not already in script
                if "INPUT_FILE" not in analysis_script:
                    analysis_script = analysis_script.replace(
                        "spark = SparkSession.builder",
                        f'INPUT_FILE = r"{input_path}"\nOUTPUT_DIR = r"{output_dir}"\n\nspark = SparkSession.builder'
                    )
            else:
                # Use default generated script
                self.log_message("info", "📄 Using default analysis script")
                analysis_script = self._create_analysis_script(input_path, output_dir)
            
            self.progress_var.set(20)
            self.progress_label.config(text="20% - Loading data...")
            
            # Execute the script
            self._execute_spark_job(analysis_script, output_dir)
            
            self.progress_var.set(100)
            self.progress_label.config(text="100% - Analysis Complete!")
            self.log_message("success", "✅ Analysis completed successfully!")
            self.update_status("ML Analysis completed")
            
            # Update results
            self._update_results(output_dir)
            
            messagebox.showinfo("Success", "ML Analysis completed!\n\nResults saved to:\n" + output_dir)
            
        except Exception as e:
            self.log_message("error", f"❌ Error: {str(e)}")
            self.log_message("error", traceback.format_exc())
            self.update_status("Analysis failed")
            messagebox.showerror("Error", f"Analysis failed:\n{str(e)}")
        
        finally:
            self.is_running = False
            self.run_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
    
    def _create_analysis_script(self, input_path, output_dir):
        """Create a Python script with the ML analysis code"""
        
        script = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ML Analytics Script - Generated automatically
Based on code7.py
"""

import sys
import json
from datetime import datetime

try:
    from pyspark.sql import SparkSession
    from pyspark.sql.functions import col, sum as _sum, count, avg, month, year, when, datediff, max as _max, min as _min
    from pyspark.ml.clustering import KMeans, BisectingKMeans
    from pyspark.ml.regression import LinearRegression, RandomForestRegressor
    from pyspark.ml.feature import VectorAssembler, StandardScaler
    from pyspark.ml.evaluation import RegressionEvaluator
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import seaborn as sns
    import pandas as pd
    import numpy as np
    import warnings
    warnings.filterwarnings('ignore')
    
    print("✅ All required libraries imported successfully")
    
except ImportError as e:
    print(f"❌ Import Error: {{e}}")
    print("Cần cài đặt: pip install pyspark pandas matplotlib seaborn numpy scikit-learn")
    sys.exit(1)

# Configuration
INPUT_FILE = r"{input_path}"
OUTPUT_DIR = r"{output_dir}"

print("=" * 80)
print("🤖 ML BIG DATA ANALYTICS - AUTOMATED EXECUTION")
print("=" * 80)
print(f"📂 Input: {{INPUT_FILE}}")
print(f"📂 Output: {{OUTPUT_DIR}}")

# Initialize Spark
print("\\n[1/4] Initializing Spark Session...")
spark = SparkSession.builder \\
    .appName("MLAnalytics_AutoExec") \\
    .config("spark.sql.adaptive.enabled", "true") \\
    .getOrCreate()

try:
    # Load data
    print("[2/4] Loading data...")
    df = spark.read.csv(INPUT_FILE, header=True, inferSchema=True)
    print(f"✅ Loaded {{df.count():,}} records")
    
    # Basic analysis
    print("[3/4] Running analysis...")
    
    # Clean data
    df_clean = df.dropna().filter(col("Quantity") > 0).filter(col("Price") > 0)
    df_clean = df_clean.withColumn("Revenue", col("Quantity") * col("Price"))
    df_clean.cache()
    
    total_records = df_clean.count()
    total_revenue = df_clean.agg(_sum("Revenue")).collect()[0][0]
    
    print(f"✅ Processed {{total_records:,}} clean records")
    print(f"✅ Total Revenue: ${{total_revenue:,.2f}}")
    
    print("[4/4] Creating visualizations...")
    
    # Basic statistics
    top_countries = df_clean.groupBy("Country") \\
        .agg(_sum("Revenue").alias("Total_Revenue")) \\
        .orderBy(col("Total_Revenue").desc()) \\
        .limit(10).toPandas()
    
    top_products = df_clean.groupBy("Description") \\
        .agg(_sum("Revenue").alias("Total_Revenue")) \\
        .orderBy(col("Total_Revenue").desc()) \\
        .limit(10).toPandas()
    
    # Create basic visualization
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Top countries
    axes[0].barh(top_countries['Country'].head(5), 
                 top_countries['Total_Revenue'].head(5),
                 color='#3498db', edgecolor='black')
    axes[0].set_xlabel('Revenue ($)', fontweight='bold')
    axes[0].set_title('Top 5 Countries by Revenue', fontweight='bold')
    axes[0].invert_yaxis()
    axes[0].grid(axis='x', alpha=0.3)
    
    # Top products
    prod_names = [name[:25] + '...' if len(name) > 25 else name 
                  for name in top_products['Description'].head(5)]
    axes[1].barh(prod_names, top_products['Total_Revenue'].head(5),
                 color='#2ecc71', edgecolor='black')
    axes[1].set_xlabel('Revenue ($)', fontweight='bold')
    axes[1].set_title('Top 5 Products by Revenue', fontweight='bold')
    axes[1].invert_yaxis()
    axes[1].grid(axis='x', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR + '/ml_analysis_results.png', dpi=300, bbox_inches='tight')
    print(f"✅ Chart saved: {{OUTPUT_DIR}}/ml_analysis_results.png")
    plt.close()
    
    # Save results summary
    results = {{
        'timestamp': datetime.now().isoformat(),
        'total_records': int(total_records),
        'total_revenue': float(total_revenue),
        'num_countries': int(df_clean.select('Country').distinct().count()),
        'num_products': int(df_clean.select('Description').distinct().count()),
        'top_countries': top_countries[['Country', 'Total_Revenue']].head(5).to_dict('records'),
        'top_products': top_products[['Description', 'Total_Revenue']].head(5).to_dict('records')
    }}
    
    with open(OUTPUT_DIR + '/ml_analysis_summary.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"✅ Summary saved: {{OUTPUT_DIR}}/ml_analysis_summary.json")
    
    print("\\n" + "=" * 80)
    print("✅ ANALYSIS COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    
    spark.stop()
    
except Exception as e:
    print(f"❌ Error: {{e}}")
    import traceback
    traceback.print_exc()
    spark.stop()
    sys.exit(1)
'''
        return script
    
    def _execute_spark_job(self, script_content, output_dir):
        """Execute Spark job asynchronously - optimized for long-running tasks"""
        import tempfile
        import subprocess
        import shutil
        import time
        
        # Write script to temporary file
        temp_dir = tempfile.gettempdir()
        script_path = os.path.join(temp_dir, 'temp_ml_analysis.py')
        
        try:
            # Ensure directories exist
            os.makedirs(temp_dir, exist_ok=True)
            os.makedirs(output_dir, exist_ok=True)
            
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            self.log_message("info", f"✍️ Script created: {script_path}")
            self.log_message("info", "⏳ Running analysis in background (this may take 10-30 minutes)...")
            
            # Execute using Python with extended timeout (30 minutes for large datasets)
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            
            self.progress_var.set(30)
            self.progress_label.config(text="30% - Processing data (background task)...")
            
            self.log_message("info", "🚀 Executing PySpark job...")
            
            # Run with extended timeout (1800 seconds = 30 minutes)
            result = subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=1800,  # 30 minute timeout for large data processing
                env=env
            )
            
            # Log major milestones only (reduce noise)
            if result.stdout:
                for line in result.stdout.split('\n'):
                    # Log only important lines to reduce clutter
                    if any(keyword in line for keyword in ['✅', '❌', 'tính', 'thành công', 'hoàn', '[', 'ERROR', 'error']):
                        if line.strip():
                            self.log_message("info", line)
            
            if result.returncode != 0:
                self.log_message("error", f"❌ Script execution failed with code {result.returncode}")
                if result.stderr:
                    self.log_message("error", result.stderr[:500])  # Limit error message length
                # Still try to load partial results
                self.log_message("warning", "⚠️ Attempting to load partial results...")
            else:
                self.log_message("success", "✅ Data processing complete")
            
            self.progress_var.set(70)
            self.progress_label.config(text="70% - Finding analysis results...")
            
            # Check for output files in /tmp (primary location for PySpark)
            json_file = os.path.join(output_dir, 'ml_analysis_summary.json')
            png_file = os.path.join(output_dir, 'ml_analysis_results.png')
            
            # Try multiple locations for files
            locations_to_check = [
                output_dir,
                '/tmp/',
                tempfile.gettempdir(),
                os.path.expanduser('~')
            ]
            
            found_json = False
            found_png = False
            
            for loc in locations_to_check:
                if not found_json:
                    alt_json = os.path.join(loc, 'ml_analysis_summary.json')
                    if os.path.exists(alt_json) and not found_json:
                        try:
                            if alt_json != json_file:
                                shutil.copy(alt_json, json_file)
                                self.log_message("info", f"✅ Results found at: {alt_json}")
                            found_json = True
                        except:
                            pass
                
                if not found_png:
                    alt_png = os.path.join(loc, 'ml_analysis_results.png')
                    if os.path.exists(alt_png) and not found_png:
                        try:
                            if alt_png != png_file:
                                shutil.copy(alt_png, png_file)
                                self.log_message("info", f"✅ Chart found at: {alt_png}")
                            found_png = True
                        except:
                            pass
            
            if found_json:
                self.log_message("success", f"✅ Analysis data ready: {json_file}")
            else:
                self.log_message("warning", "⚠️ Analysis data file not found - may still be processing")
            
            if found_png:
                self.log_message("success", f"✅ Visualization ready: {png_file}")
            else:
                self.log_message("info", "ℹ️ Chart will be generated automatically")
            
            self.progress_var.set(90)
            self.progress_label.config(text="90% - Finalizing...")
            
            # Give system a moment to finish file writes
            time.sleep(1)
            
        except subprocess.TimeoutExpired:
            self.log_message("warning", "⏱️ Analysis is taking longer than expected (>30 minutes)")
            self.log_message("info", "ℹ️ The script is still running in background - results will be available when complete")
            self.log_message("info", "ℹ️ You can check /tmp/ml_analysis_summary.json manually later")
            # Don't raise - let user check results manually
        except Exception as e:
            self.log_message("error", f"❌ Error during execution: {str(e)[:200]}")
            raise

    
    def _update_results(self, output_dir):
        """Update results display - simplified for performance"""
        import tempfile
        try:
            # Check multiple locations for results file
            locations = [
                os.path.join(output_dir, 'ml_analysis_summary.json'),
                '/tmp/ml_analysis_summary.json',
                os.path.join(tempfile.gettempdir(), 'ml_analysis_summary.json')
            ]
            
            result_file = None
            for loc in locations:
                if os.path.exists(loc):
                    result_file = loc
                    break
            
            if not result_file:
                self.log_message("info", "ℹ️ Results not yet available - analysis may still be running")
                self.log_message("info", "ℹ️ Results will appear in /tmp/ml_analysis_summary.json when complete")
                return
            
            # Load and display results
            with open(result_file, 'r', encoding='utf-8') as f:
                results = json.load(f)
            
            results_text = f"""
📊 PHÂN TÍCH HOÀN THÀNH
{'=' * 60}

📅 Thời gian: {results.get('timestamp', 'N/A')}
📈 Tổng bản ghi: {results.get('total_records', 0):,}
💰 Tổng doanh thu: ${results.get('total_revenue', 0):,.2f}
🌍 Số nước: {results.get('num_countries', 0)}
📦 Số sản phẩm: {results.get('num_products', 0)}

🏆 TOP 5 QUỐC GIA:
"""
            
            for idx, country in enumerate(results.get('top_countries', []), 1):
                results_text += f"  {idx}. {country.get('Country', 'N/A')}: ${country.get('Total_Revenue', 0):,.2f}\n"
            
            results_text += "\n📦 TOP 5 SẢN PHẨM:\n"
            for idx, product in enumerate(results.get('top_products', []), 1):
                prod_name = product.get('Description', 'N/A')[:45]
                results_text += f"  {idx}. {prod_name}: ${product.get('Total_Revenue', 0):,.2f}\n"
            
            # Update results display
            self.results_text.config(state=tk.NORMAL)
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, results_text)
            self.results_text.config(state=tk.DISABLED)
            
            self.log_message("success", f"✅ Kết quả tải thành công: {result_file}")
                
        except json.JSONDecodeError:
            self.log_message("warning", "⚠️ Định dạng JSON không hợp lệ - file còn đang ghi")
        except Exception as e:
            self.log_message("info", f"ℹ️ Không thể tải kết quả: {str(e)[:100]}")

    
    def stop_analysis(self):
        """Stop the running analysis"""
        if self.process:
            self.process.terminate()
        self.is_running = False
        self.log_message("warning", "⏹️ Analysis stopped by user")
        self.update_status("Analysis stopped")
        self.run_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)


# Export
__all__ = ['MLAnalyticsTab']
