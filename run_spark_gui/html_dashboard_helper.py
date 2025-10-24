"""
HTML Dashboard Helper - Open and manage ML Analytics Dashboard from Tkinter GUI
"""

import os
import sys
import json
import webbrowser
import threading
from pathlib import Path
from datetime import datetime
import subprocess
import platform

class HTMLDashboardHelper:
    """Helper class to integrate HTML dashboard with Tkinter GUI"""
    
    def __init__(self, dashboard_path=None):
        """
        Initialize dashboard helper
        
        Args:
            dashboard_path (str): Path to ml_analytics_dashboard.html
        """
        if dashboard_path is None:
            # Auto-detect dashboard path
            script_dir = Path(__file__).parent.parent
            dashboard_path = script_dir / 'ml_analytics_dashboard.html'
        
        self.dashboard_path = Path(dashboard_path)
        self.data_path = Path('/tmp/ml_analysis_summary.json')
        self.chart_path = Path('/tmp/ml_analysis_results.png')
        
        if not self.dashboard_path.exists():
            raise FileNotFoundError(f"Dashboard not found: {self.dashboard_path}")
    
    def open_dashboard(self, new_window=True):
        """
        Open ML Analytics Dashboard in default web browser
        
        Args:
            new_window (bool): Open in new browser window if True
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Convert path to file:// URL
            dashboard_url = self.dashboard_path.as_uri()
            
            # Open in browser (in background thread to not block GUI)
            thread = threading.Thread(
                target=self._open_url,
                args=(dashboard_url, new_window),
                daemon=True
            )
            thread.start()
            
            return True
        except Exception as e:
            print(f"❌ Error opening dashboard: {e}")
            return False
    
    def _open_url(self, url, new_window):
        """Open URL in web browser"""
        try:
            webbrowser.open(url, new=1 if new_window else 0)
        except Exception as e:
            print(f"❌ Failed to open browser: {e}")
    
    def check_data_availability(self):
        """
        Check if latest analysis data is available
        
        Returns:
            dict: Status information
        """
        status = {
            'data_exists': self.data_path.exists(),
            'chart_exists': self.chart_path.exists(),
            'data_path': str(self.data_path),
            'chart_path': str(self.chart_path)
        }
        
        if status['data_exists']:
            try:
                with open(self.data_path, 'r') as f:
                    data = json.load(f)
                status['timestamp'] = data.get('timestamp', 'Unknown')
                status['records'] = data.get('total_records', 0)
                status['revenue'] = data.get('total_revenue', 0)
            except Exception as e:
                status['data_error'] = str(e)
        
        if status['chart_exists']:
            status['chart_mtime'] = datetime.fromtimestamp(
                self.chart_path.stat().st_mtime
            ).isoformat()
        
        return status
    
    def get_data_summary(self):
        """
        Get summary of current analysis data
        
        Returns:
            dict: Analysis summary or None if no data
        """
        try:
            if not self.data_path.exists():
                return None
            
            with open(self.data_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error reading data: {e}")
            return None
    
    def generate_report(self, output_file=None):
        """
        Generate a text report from analysis data
        
        Args:
            output_file (str): Optional file path to save report
        
        Returns:
            str: Report text
        """
        data = self.get_data_summary()
        if not data:
            return "❌ No analysis data available"
        
        report = f"""
{'='*80}
ML ANALYTICS REPORT
{'='*80}

Generated: {data.get('timestamp', 'Unknown')}

KEY METRICS
{'-'*80}
Total Records:     {data.get('total_records', 0):>20,}
Total Revenue:     ${data.get('total_revenue', 0):>19,.2f}
Countries:         {data.get('num_countries', 0):>20}
Products:          {data.get('num_products', 0):>20}

TOP 5 COUNTRIES
{'-'*80}
"""
        
        for idx, country in enumerate(data.get('top_countries', [])[:5], 1):
            name = country.get('Country', 'Unknown')
            revenue = country.get('Total_Revenue', 0)
            report += f"{idx}. {name:<30} ${revenue:>15,.2f}\n"
        
        report += f"\nTOP 5 PRODUCTS\n{'-'*80}\n"
        
        for idx, product in enumerate(data.get('top_products', [])[:5], 1):
            desc = product.get('Description', 'Unknown')[:40]
            revenue = product.get('Total_Revenue', 0)
            report += f"{idx}. {desc:<40} ${revenue:>15,.2f}\n"
        
        report += f"\n{'='*80}\n"
        
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(report)
                print(f"✅ Report saved to: {output_file}")
            except Exception as e:
                print(f"⚠️ Could not save report: {e}")
        
        return report
    
    def export_to_html_string(self):
        """
        Export dashboard HTML as string (for embedding)
        
        Returns:
            str: HTML content
        """
        try:
            with open(self.dashboard_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"❌ Error reading dashboard HTML: {e}")
            return None
    
    def refresh_data(self, force=False):
        """
        Refresh/reload analysis data
        
        Args:
            force (bool): Force reload even if data is fresh
        
        Returns:
            bool: True if data loaded successfully
        """
        try:
            data = self.get_data_summary()
            if data is None:
                return False
            
            print(f"✅ Data refreshed: {data.get('timestamp', 'Unknown')}")
            return True
        except Exception as e:
            print(f"❌ Error refreshing data: {e}")
            return False
    
    def validate_setup(self):
        """
        Validate dashboard setup and dependencies
        
        Returns:
            dict: Validation results
        """
        results = {
            'dashboard_exists': self.dashboard_path.exists(),
            'dashboard_path': str(self.dashboard_path),
            'dashboard_readable': self.dashboard_path.exists() and os.access(self.dashboard_path, os.R_OK),
            'python_version': f"{sys.version_info.major}.{sys.version_info.minor}",
            'os': platform.system(),
        }
        
        # Check for required Python modules
        required_modules = ['webbrowser', 'json', 'threading', 'pathlib']
        results['required_modules'] = {}
        
        for module in required_modules:
            try:
                __import__(module)
                results['required_modules'][module] = True
            except ImportError:
                results['required_modules'][module] = False
        
        results['all_valid'] = (
            results['dashboard_exists'] and 
            results['dashboard_readable'] and
            all(results['required_modules'].values())
        )
        
        return results
    
    @staticmethod
    def create_quick_link(dashboard_path, output_dir='/tmp'):
        """
        Create a quick link file (shortcut) to dashboard
        
        Args:
            dashboard_path (str): Path to dashboard HTML
            output_dir (str): Directory to save shortcut
        
        Returns:
            str: Path to created shortcut or None
        """
        try:
            output_path = Path(output_dir) / 'open_dashboard.bat'
            
            if platform.system() == 'Windows':
                # Windows batch file
                batch_content = f'@echo off\nstart "" "{dashboard_path}"\n'
                with open(output_path, 'w') as f:
                    f.write(batch_content)
            else:
                # Linux/Mac shell script
                output_path = Path(output_dir) / 'open_dashboard.sh'
                shell_content = f'#!/bin/bash\nopen "{dashboard_path}"\n'
                with open(output_path, 'w') as f:
                    f.write(shell_content)
                os.chmod(output_path, 0o755)
            
            print(f"✅ Quick link created: {output_path}")
            return str(output_path)
        except Exception as e:
            print(f"❌ Error creating quick link: {e}")
            return None


# Example usage for Tkinter integration
if __name__ == '__main__':
    # Find dashboard
    dashboard_helper = HTMLDashboardHelper()
    
    # Check setup
    validation = dashboard_helper.validate_setup()
    print("🔍 Validation Results:")
    print(f"  Dashboard exists: {validation['dashboard_exists']}")
    print(f"  Dashboard readable: {validation['dashboard_readable']}")
    print(f"  All requirements met: {validation['all_valid']}")
    
    # Check data availability
    status = dashboard_helper.check_data_availability()
    print("\n📊 Data Availability:")
    print(f"  Data file exists: {status['data_exists']}")
    print(f"  Chart file exists: {status['chart_exists']}")
    
    if status['data_exists']:
        print(f"  Last update: {status.get('timestamp', 'Unknown')}")
        print(f"  Records: {status.get('records', 0):,}")
        print(f"  Revenue: ${status.get('revenue', 0):,.2f}")
    
    # Generate report
    print("\n📝 Report:")
    print(dashboard_helper.generate_report())
    
    # Open dashboard (uncomment to use)
    # dashboard_helper.open_dashboard()
