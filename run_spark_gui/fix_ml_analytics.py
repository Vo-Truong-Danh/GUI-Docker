# -*- coding: utf-8 -*-
"""
Fix ml_analytics_tab.py - Replace run_analysis method with ASCII-only version
"""

import re

file_path = r'd:\BaiTapSinhVien\TH BigData\GUI-Docker\run_spark_gui\ml_analytics_tab.py'

# Read the file
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the run_analysis method
# We'll look for the method definition and replace everything up to the next def

pattern = r'(    def run_analysis\(self\):.*?)(    def \w+\(self)'
replacement = r'''\1    def _execute_analysis(self, input_path, output_dir, script_path):
        """Execute the ML analysis"""
        try:
\2'''

# This approach is complex. Instead, let's use a simpler approach:
# Find the run_analysis method start and replace the entire method body

start_marker = '    def run_analysis(self):'
end_marker = '    def _execute_analysis(self, input_path, output_dir, script_path):'

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx != -1 and end_idx != -1:
    # Extract the part before, the new method, and the part after
    before = content[:start_idx]
    after = content[end_idx:]
    
    # Create new method (ASCII-only)
    new_method = '''    def run_analysis(self):
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

'''
    
    # Reconstruct the file
    new_content = before + new_method + after
    
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("[OK] File updated successfully!")
    print(f"[OK] Method replacement completed")
    
else:
    print("[ERROR] Could not find method markers")
    print(f"start_idx: {start_idx}, end_idx: {end_idx}")
