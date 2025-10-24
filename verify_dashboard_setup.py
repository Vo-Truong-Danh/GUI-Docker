#!/usr/bin/env python
"""
HTML Dashboard Setup Verification Script
Kiểm tra xem các tệp tin và phụ thuộc đã được thiết lập đúng cách chưa
"""

import os
import sys
from pathlib import Path
import json

def check_file_exists(file_path, description=""):
    """Check if file exists and report status"""
    exists = os.path.exists(file_path)
    status = "✅" if exists else "❌"
    desc = f" ({description})" if description else ""
    print(f"{status} {file_path}{desc}")
    return exists

def check_file_content(file_path, search_string, description=""):
    """Check if file contains specific content"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            found = search_string in content
            status = "✅" if found else "❌"
            desc = f" - {description}" if description else ""
            print(f"  {status} Contains: {search_string[:50]}{desc}")
            return found
    except Exception as e:
        print(f"  ❌ Error reading file: {e}")
        return False

def verify_python_module(module_name):
    """Verify if Python module can be imported"""
    try:
        __import__(module_name)
        print(f"✅ Python module '{module_name}' available")
        return True
    except ImportError:
        print(f"❌ Python module '{module_name}' NOT available")
        return False

def main():
    print("=" * 80)
    print("🔍 HTML Dashboard Setup Verification")
    print("=" * 80)
    print()
    
    # Get workspace root
    workspace_root = Path(__file__).parent
    run_spark_gui = workspace_root / "run_spark_gui"
    
    print(f"📂 Workspace Root: {workspace_root}")
    print(f"📂 Run Spark GUI Dir: {run_spark_gui}")
    print()
    
    # Check critical files
    print("📋 File Checks:")
    print("-" * 80)
    
    critical_files = [
        (workspace_root / "ml_analytics_dashboard.html", "HTML Dashboard"),
        (workspace_root / "ml_analytics_bridge.js", "JavaScript Bridge"),
        (workspace_root / "HTML_DASHBOARD_INTEGRATION_GUIDE.md", "Integration Guide"),
        (workspace_root / "HTML_DASHBOARD_COMPLETE_GUIDE.md", "Complete Guide"),
        (run_spark_gui / "html_dashboard_helper.py", "Python Helper"),
        (run_spark_gui / "ml_analytics_tab.py", "ML Analytics Tab"),
        (run_spark_gui / "main.py", "Main Application"),
        (run_spark_gui / "code7.py", "ML Analysis Code"),
    ]
    
    files_ok = True
    for file_path, description in critical_files:
        if not check_file_exists(str(file_path), description):
            files_ok = False
    
    print()
    
    # Check HTML Dashboard content
    print("📊 Dashboard Content Checks:")
    print("-" * 80)
    
    dashboard_path = workspace_root / "ml_analytics_dashboard.html"
    if dashboard_path.exists():
        checks = [
            ("Bootstrap", "Dashboard CSS framework"),
            ("Chart.js", "JavaScript charting library"),
            ("topCountriesTable", "Countries table element"),
            ("topProductsTable", "Products table element"),
            ("totalRecords", "Total records metric"),
            ("totalRevenue", "Total revenue metric"),
            ("auto-refresh", "Auto-refresh feature"),
        ]
        
        for search, desc in checks:
            check_file_content(str(dashboard_path), search, desc)
    
    print()
    
    # Check Python helper content
    print("🐍 Python Helper Content Checks:")
    print("-" * 80)
    
    helper_path = run_spark_gui / "html_dashboard_helper.py"
    if helper_path.exists():
        checks = [
            ("class HTMLDashboardHelper", "Main class definition"),
            ("open_dashboard", "Open dashboard method"),
            ("check_data_availability", "Data check method"),
            ("get_data_summary", "Data summary method"),
            ("generate_report", "Report generation method"),
        ]
        
        for search, desc in checks:
            check_file_content(str(helper_path), search, desc)
    
    print()
    
    # Check ML Analytics Tab integration
    print("🎨 ML Analytics Tab Integration Checks:")
    print("-" * 80)
    
    tab_path = run_spark_gui / "ml_analytics_tab.py"
    if tab_path.exists():
        checks = [
            ("HTMLDashboardHelper", "Dashboard helper import"),
            ("open_html_dashboard", "Dashboard open method"),
            ("Open HTML Dashboard", "Dashboard button in UI"),
        ]
        
        for search, desc in checks:
            check_file_content(str(tab_path), search, desc)
    
    print()
    
    # Check Python modules
    print("📦 Python Module Checks:")
    print("-" * 80)
    
    modules = [
        "tkinter",
        "json",
        "os",
        "sys",
        "pathlib",
        "webbrowser",
        "threading",
    ]
    
    modules_ok = True
    for module in modules:
        if not verify_python_module(module):
            modules_ok = False
    
    print()
    
    # Check data output directories
    print("📂 Data Output Directory Checks:")
    print("-" * 80)
    
    tmp_dir = Path("/tmp")
    print(f"📂 Temp directory: {tmp_dir}")
    print(f"  Exists: {'✅' if tmp_dir.exists() else '❌'}")
    print(f"  Writable: {'✅' if os.access(tmp_dir, os.W_OK) else '❌'}")
    
    # Check for existing analysis data
    data_file = tmp_dir / "ml_analysis_summary.json"
    chart_file = tmp_dir / "ml_analysis_results.png"
    
    if data_file.exists():
        print(f"✅ Analysis data exists: {data_file}")
        try:
            with open(data_file, 'r') as f:
                data = json.load(f)
                print(f"   Records: {data.get('total_records', 0):,}")
                print(f"   Revenue: ${data.get('total_revenue', 0):,.2f}")
                print(f"   Updated: {data.get('timestamp', 'Unknown')}")
        except Exception as e:
            print(f"⚠️ Error reading data: {e}")
    else:
        print(f"⚠️ No analysis data found: {data_file}")
    
    if chart_file.exists():
        print(f"✅ Chart image exists: {chart_file}")
    else:
        print(f"⚠️ No chart image found: {chart_file}")
    
    print()
    
    # Summary
    print("=" * 80)
    print("📊 Verification Summary:")
    print("=" * 80)
    
    summary = {
        "Files": files_ok,
        "Modules": modules_ok,
        "Dashboard": dashboard_path.exists(),
        "Helper": helper_path.exists(),
        "Integration": tab_path.exists(),
    }
    
    all_ok = all(summary.values())
    
    for check, status in summary.items():
        emoji = "✅" if status else "❌"
        print(f"{emoji} {check}: {'OK' if status else 'MISSING'}")
    
    print()
    
    if all_ok:
        print("🎉 ✅ All checks passed! Dashboard is ready to use.")
        print()
        print("Next steps:")
        print("1. Run ML Analysis in Tkinter GUI")
        print("2. Click 'Open HTML Dashboard' button")
        print("3. View results in your default browser")
        return 0
    else:
        print("⚠️ Some checks failed. Please review the output above.")
        print()
        print("Common issues:")
        print("• Missing files - Verify files are in correct locations")
        print("• Python modules - Install required packages")
        print("• No analysis data - Run ML Analysis first")
        return 1

if __name__ == "__main__":
    sys.exit(main())
