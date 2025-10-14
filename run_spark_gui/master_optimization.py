"""
Master System Optimization Script
Script tổng hợp tối ưu hóa hệ thống
Version: 1.0.0
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime
import json


class MasterOptimizer:
    """Tổng hợp tất cả công cụ tối ưu hóa"""
    
    def __init__(self):
        self.workspace_dir = Path(__file__).parent
        self.python_cmd = sys.executable
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'steps_completed': [],
            'errors': []
        }
    
    def run_full_optimization(self):
        """Chạy full optimization pipeline"""
        print("=" * 80)
        print("MASTER SYSTEM OPTIMIZATION")
        print("Tối ưu hóa Toàn diện Hệ thống")
        print("=" * 80)
        print(f"\nWorkspace: {self.workspace_dir}")
        print(f"Python: {self.python_cmd}\n")
        
        steps = [
            ("🔍 System Analysis", "comprehensive_system_analysis.py"),
            ("🔧 Auto Code Fixer", "auto_code_fixer.py"),
            ("📦 Dependency Optimizer", "dependency_optimizer_v2.py"),
        ]
        
        for step_name, script_name in steps:
            print("\n" + "=" * 80)
            print(f"{step_name}")
            print("=" * 80)
            
            success = self._run_script(script_name)
            
            if success:
                self.results['steps_completed'].append(step_name)
                print(f"\n✅ {step_name} completed successfully")
            else:
                self.results['errors'].append({
                    'step': step_name,
                    'message': 'Script execution failed'
                })
                print(f"\n❌ {step_name} failed")
                
                # Ask to continue
                response = input("\nContinue with next step? (Y/n): ").strip().lower()
                if response == 'n':
                    break
        
        # Save results
        self._save_results()
        
        # Show summary
        self._show_summary()
    
    def _run_script(self, script_name: str) -> bool:
        """Chạy một script"""
        script_path = self.workspace_dir / script_name
        
        if not script_path.exists():
            print(f"⚠️ Script not found: {script_name}")
            return False
        
        try:
            # Run script
            result = subprocess.run(
                [self.python_cmd, str(script_path)],
                cwd=str(self.workspace_dir),
                capture_output=False,
                text=True
            )
            
            return result.returncode == 0
        
        except Exception as e:
            print(f"❌ Error running script: {e}")
            return False
    
    def _save_results(self):
        """Lưu kết quả"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_path = self.workspace_dir / f'optimization_results_{timestamp}.json'
        
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Results saved: {results_path}")
    
    def _show_summary(self):
        """Hiển thị tóm tắt"""
        print("\n" + "=" * 80)
        print("📊 OPTIMIZATION SUMMARY")
        print("=" * 80)
        
        print(f"\n✅ Steps completed: {len(self.results['steps_completed'])}")
        for step in self.results['steps_completed']:
            print(f"   ✓ {step}")
        
        if self.results['errors']:
            print(f"\n❌ Errors: {len(self.results['errors'])}")
            for error in self.results['errors']:
                print(f"   ✗ {error['step']}: {error['message']}")
        
        print("\n" + "=" * 80)
        print("NEXT STEPS")
        print("=" * 80)
        print("""
1. Review generated reports:
   - system_analysis_report_*.json
   - auto_fix_report_*.json
   - dependency_analysis_report.json

2. Apply recommended fixes:
   - Review auto-fix changes in backups/
   - Update requirements.txt if needed
   - Address critical security issues

3. Test the system:
   - Run test suite
   - Verify all features work correctly
   - Check for any regressions

4. Monitor system health:
   - Use realtime_monitoring_dashboard.py
   - Set up alerts for critical thresholds
   - Review error logs regularly

5. Additional improvements:
   - Consider implementing suggested features
   - Update documentation
   - Set up automated testing
        """)
        
        print("=" * 80)
        print("✅ OPTIMIZATION COMPLETE!")
        print("=" * 80)


def show_menu():
    """Hiển thị menu"""
    print("\n" + "=" * 80)
    print("SYSTEM OPTIMIZATION MENU")
    print("=" * 80)
    print("""
Choose an option:

1. 🚀 Run Full Optimization (All steps)
2. 🔍 System Analysis Only
3. 🔧 Auto Code Fixer Only
4. 📦 Dependency Optimizer Only
5. 📊 Launch Monitoring Dashboard
6. 📋 View Previous Reports
7. ❌ Exit

    """)


def run_individual_tool(tool_name: str):
    """Chạy công cụ riêng lẻ"""
    workspace_dir = Path(__file__).parent
    python_cmd = sys.executable
    
    tools = {
        'analysis': 'comprehensive_system_analysis.py',
        'fixer': 'auto_code_fixer.py',
        'dependency': 'dependency_optimizer_v2.py',
        'dashboard': 'realtime_monitoring_dashboard.py'
    }
    
    script_name = tools.get(tool_name)
    if not script_name:
        print(f"❌ Unknown tool: {tool_name}")
        return
    
    script_path = workspace_dir / script_name
    
    if not script_path.exists():
        print(f"❌ Script not found: {script_name}")
        return
    
    print(f"\n🚀 Running {script_name}...\n")
    
    try:
        subprocess.run(
            [python_cmd, str(script_path)],
            cwd=str(workspace_dir)
        )
    except Exception as e:
        print(f"❌ Error: {e}")


def view_reports():
    """Xem các reports"""
    workspace_dir = Path(__file__).parent
    
    print("\n" + "=" * 80)
    print("AVAILABLE REPORTS")
    print("=" * 80 + "\n")
    
    report_patterns = [
        'system_analysis_report_*.json',
        'auto_fix_report_*.json',
        'dependency_analysis_report.json',
        'monitoring_report_*.json'
    ]
    
    for pattern in report_patterns:
        files = list(workspace_dir.glob(pattern))
        if files:
            print(f"\n{pattern}:")
            for file in sorted(files, reverse=True)[:5]:  # Show latest 5
                size = file.stat().st_size / 1024  # KB
                mtime = datetime.fromtimestamp(file.stat().st_mtime)
                print(f"  • {file.name}")
                print(f"    Size: {size:.1f} KB | Modified: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\n" + "=" * 80)


def main():
    """Main function"""
    print("=" * 80)
    print("🚀 SYSTEM OPTIMIZATION SUITE")
    print("Bộ công cụ Tối ưu hóa Hệ thống")
    print("=" * 80)
    
    while True:
        show_menu()
        
        choice = input("Enter your choice (1-7): ").strip()
        
        if choice == '1':
            optimizer = MasterOptimizer()
            optimizer.run_full_optimization()
            input("\nPress Enter to continue...")
        
        elif choice == '2':
            run_individual_tool('analysis')
            input("\nPress Enter to continue...")
        
        elif choice == '3':
            run_individual_tool('fixer')
            input("\nPress Enter to continue...")
        
        elif choice == '4':
            run_individual_tool('dependency')
            input("\nPress Enter to continue...")
        
        elif choice == '5':
            run_individual_tool('dashboard')
            input("\nPress Enter to continue...")
        
        elif choice == '6':
            view_reports()
            input("\nPress Enter to continue...")
        
        elif choice == '7':
            print("\n👋 Goodbye!")
            break
        
        else:
            print("\n❌ Invalid choice. Please try again.")


if __name__ == '__main__':
    main()
