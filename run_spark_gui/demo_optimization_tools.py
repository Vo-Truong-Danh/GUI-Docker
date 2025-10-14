"""
Demo Script - System Optimization Tools
Script demo các tính năng tối ưu hóa
Version: 1.0.0
"""

import sys
from pathlib import Path


def print_banner():
    """Print banner"""
    print("\n" + "=" * 80)
    print(" " * 20 + "🚀 SYSTEM OPTIMIZATION TOOLS DEMO 🚀")
    print("=" * 80 + "\n")


def demo_error_handler():
    """Demo error handler v3"""
    print("=" * 80)
    print("1️⃣ DEMO: Enhanced Error Handler v3.0")
    print("=" * 80 + "\n")
    
    try:
        from enhanced_error_handler_v3 import (
            get_error_handler, ErrorSeverity, ErrorCategory, ErrorContext
        )
        
        handler = get_error_handler()
        
        print("✓ Error handler imported successfully\n")
        
        # Demo 1: Basic error handling
        print("Demo 1: Basic Error Handling")
        print("-" * 40)
        
        @handler.decorator(severity=ErrorSeverity.MEDIUM)
        def demo_function_1():
            raise ValueError("This is a demo error")
        
        demo_function_1()
        print("✓ Error handled with decorator\n")
        
        # Demo 2: Error with context
        print("Demo 2: Error with Context")
        print("-" * 40)
        
        context = ErrorContext(
            operation="Demo operation",
            details={'demo': True, 'version': '1.0'}
        )
        
        try:
            raise FileNotFoundError("Demo file not found")
        except Exception as e:
            handler.handle_error(
                e,
                context=context,
                severity=ErrorSeverity.HIGH,
                category=ErrorCategory.FILE_IO
            )
        
        print("✓ Error handled with context\n")
        
        # Demo 3: Safe execute
        print("Demo 3: Safe Execute")
        print("-" * 40)
        
        def risky_function():
            raise RuntimeError("Risky operation failed")
        
        result = handler.safe_execute(
            risky_function,
            default="fallback_value"
        )
        
        print(f"✓ Safe execute returned: {result}\n")
        
        # Demo 4: Statistics
        print("Demo 4: Error Statistics")
        print("-" * 40)
        stats = handler.get_statistics()
        print(f"Total errors: {stats['total_errors']}")
        print(f"By severity: {stats['by_severity']}")
        print("\n✓ Demo completed successfully!\n")
        
    except ImportError as e:
        print(f"❌ Failed to import error handler: {e}")
        print("   Make sure enhanced_error_handler_v3.py exists\n")


def demo_monitoring_dashboard():
    """Demo monitoring dashboard"""
    print("=" * 80)
    print("2️⃣ DEMO: Real-time Monitoring Dashboard")
    print("=" * 80 + "\n")
    
    try:
        from realtime_monitoring_dashboard import RealTimeMonitoringDashboard
        
        print("✓ Dashboard imported successfully")
        print("\nℹ️ Dashboard features:")
        print("  • Real-time CPU, Memory, Disk monitoring")
        print("  • Process monitoring with filtering")
        print("  • Configurable alert thresholds")
        print("  • Statistics and export capabilities")
        
        print("\n📝 To launch dashboard:")
        print("  $ python realtime_monitoring_dashboard.py")
        
        response = input("\n❓ Launch dashboard now? (y/N): ").strip().lower()
        
        if response == 'y':
            print("\n🚀 Launching dashboard...\n")
            dashboard = RealTimeMonitoringDashboard()
            dashboard.run()
        else:
            print("✓ Demo skipped (user choice)\n")
        
    except ImportError as e:
        print(f"❌ Failed to import dashboard: {e}")
        print("   Make sure realtime_monitoring_dashboard.py exists\n")


def demo_analysis_tool():
    """Demo analysis tool"""
    print("=" * 80)
    print("3️⃣ DEMO: Comprehensive System Analysis")
    print("=" * 80 + "\n")
    
    script_path = Path(__file__).parent / 'comprehensive_system_analysis.py'
    
    if not script_path.exists():
        print("❌ Analysis script not found")
        print(f"   Expected: {script_path}\n")
        return
    
    print("✓ Analysis script found")
    print("\nℹ️ Analysis features:")
    print("  • Scans all Python files")
    print("  • Detects logic errors, security issues")
    print("  • Performance analysis")
    print("  • Generates detailed reports")
    
    print("\n📝 To run analysis:")
    print("  $ python comprehensive_system_analysis.py")
    
    print("\n📊 Example output:")
    print("  • Total issues: 809")
    print("  • Critical: 2 | High: 16 | Medium: 15 | Low: 776")
    print("  • Reports: JSON + TXT summary")
    
    response = input("\n❓ Run analysis now? (y/N): ").strip().lower()
    
    if response == 'y':
        print("\n🔍 Running analysis...")
        print("   This may take a minute...\n")
        
        import subprocess
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(script_path.parent)
        )
        
        if result.returncode == 0:
            print("\n✓ Analysis completed successfully!")
            print("   Check generated reports\n")
        else:
            print("\n⚠️ Analysis completed with warnings\n")
    else:
        print("✓ Demo skipped (user choice)\n")


def demo_auto_fixer():
    """Demo auto fixer"""
    print("=" * 80)
    print("4️⃣ DEMO: Auto Code Fixer")
    print("=" * 80 + "\n")
    
    print("⚠️ WARNING: This tool modifies code files!")
    print("   Backups are created automatically\n")
    
    print("✓ Auto-fixer features:")
    print("  • Fix bare except clauses")
    print("  • Add logging to silent exceptions")
    print("  • Mark print statements")
    print("  • Automatic backup before changes")
    
    print("\n📝 To run auto-fixer:")
    print("  $ python auto_code_fixer.py")
    
    print("\n💡 Recommended workflow:")
    print("  1. Run analysis first")
    print("  2. Review issues")
    print("  3. Run auto-fixer")
    print("  4. Review changes in backups/")
    print("  5. Test thoroughly")
    
    print("\n✓ Demo information shown (not executed for safety)\n")


def demo_dependency_optimizer():
    """Demo dependency optimizer"""
    print("=" * 80)
    print("5️⃣ DEMO: Dependency Optimizer")
    print("=" * 80 + "\n")
    
    print("✓ Dependency optimizer features:")
    print("  • Scan all Python imports")
    print("  • Compare with requirements.txt")
    print("  • Find unused packages")
    print("  • Find missing packages")
    print("  • Generate optimized requirements")
    
    print("\n📝 To run optimizer:")
    print("  $ python dependency_optimizer_v2.py")
    
    print("\n📊 Example results:")
    print("  • Imports used: 80")
    print("  • Packages in requirements: 3")
    print("  • Unused packages: 1")
    print("  • Missing packages: 55 (mostly internal)")
    
    print("\n✓ Demo information shown\n")


def demo_master_suite():
    """Demo master suite"""
    print("=" * 80)
    print("6️⃣ DEMO: Master Optimization Suite")
    print("=" * 80 + "\n")
    
    print("✓ Master suite features:")
    print("  • Menu-driven interface")
    print("  • Run all tools from one place")
    print("  • View previous reports")
    print("  • Launch dashboard")
    
    print("\n📝 To launch suite:")
    print("  $ python master_optimization.py")
    
    print("\n📋 Menu options:")
    print("  1. Run Full Optimization")
    print("  2. System Analysis Only")
    print("  3. Auto Code Fixer Only")
    print("  4. Dependency Optimizer Only")
    print("  5. Launch Monitoring Dashboard")
    print("  6. View Previous Reports")
    print("  7. Exit")
    
    response = input("\n❓ Launch master suite now? (y/N): ").strip().lower()
    
    if response == 'y':
        script_path = Path(__file__).parent / 'master_optimization.py'
        if script_path.exists():
            print("\n🚀 Launching master suite...\n")
            import subprocess
            subprocess.run([sys.executable, str(script_path)])
        else:
            print("❌ master_optimization.py not found\n")
    else:
        print("✓ Demo skipped (user choice)\n")


def show_documentation():
    """Show documentation"""
    print("=" * 80)
    print("7️⃣ DOCUMENTATION")
    print("=" * 80 + "\n")
    
    docs = [
        ("OPTIMIZATION_REPORT.md", "Comprehensive optimization report"),
        ("QUICK_START_OPTIMIZATION_TOOLS.md", "Quick start guide"),
        ("OPTIMIZATION_SUMMARY_FINAL.txt", "Final summary (this document)")
    ]
    
    print("📚 Available Documentation:\n")
    
    for doc_name, description in docs:
        doc_path = Path(__file__).parent.parent / doc_name
        exists = "✓" if doc_path.exists() else "❌"
        print(f"  {exists} {doc_name}")
        print(f"     {description}")
        print()
    
    print("📝 Generated Reports:\n")
    
    report_dir = Path(__file__).parent
    reports = list(report_dir.glob("*report*.json"))
    reports.extend(list(report_dir.glob("*report*.txt")))
    reports.extend(list(report_dir.glob("*analysis*.json")))
    
    if reports:
        for report in sorted(reports)[-5:]:  # Show last 5
            print(f"  • {report.name}")
    else:
        print("  (No reports found - run analysis first)")
    
    print()


def main():
    """Main function"""
    print_banner()
    
    demos = [
        ("Enhanced Error Handler v3.0", demo_error_handler),
        ("Real-time Monitoring Dashboard", demo_monitoring_dashboard),
        ("Comprehensive System Analysis", demo_analysis_tool),
        ("Auto Code Fixer", demo_auto_fixer),
        ("Dependency Optimizer", demo_dependency_optimizer),
        ("Master Optimization Suite", demo_master_suite),
        ("Documentation", show_documentation)
    ]
    
    print("Available demos:\n")
    for i, (name, _) in enumerate(demos, 1):
        print(f"  {i}. {name}")
    print(f"  {len(demos) + 1}. Run All Demos")
    print(f"  0. Exit")
    
    while True:
        try:
            print("\n" + "-" * 80)
            choice = input("\nChoose demo (0-8): ").strip()
            
            if choice == '0':
                print("\n👋 Goodbye!\n")
                break
            
            choice_num = int(choice)
            
            if choice_num == len(demos) + 1:
                # Run all demos
                for name, demo_func in demos:
                    print()
                    demo_func()
                    input("Press Enter to continue...")
            elif 1 <= choice_num <= len(demos):
                print()
                demos[choice_num - 1][1]()
                input("\nPress Enter to continue...")
            else:
                print("❌ Invalid choice")
        
        except ValueError:
            print("❌ Please enter a number")
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!\n")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}\n")
        import traceback
        traceback.print_exc()
