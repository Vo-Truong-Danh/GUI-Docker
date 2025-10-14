#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verify AI Engine V8.3 Installation
Quick check to ensure V8.3 is properly installed and configured
"""

import sys
import os
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if file exists"""
    if Path(filepath).exists():
        size = Path(filepath).stat().st_size / 1024
        print(f"✅ {description}: {filepath} ({size:.1f} KB)")
        return True
    else:
        print(f"❌ MISSING: {description}: {filepath}")
        return False

def check_file_deleted(filepath, description):
    """Check if old file is deleted"""
    if not Path(filepath).exists():
        print(f"✅ {description}: {filepath} (deleted)")
        return True
    else:
        print(f"⚠️  OLD FILE STILL EXISTS: {description}: {filepath}")
        return False

def check_config_in_file(filepath, config_key, expected_value):
    """Check if config has expected value"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            if f"{config_key}={expected_value}" in content or f"{config_key}: {expected_value}" in content:
                print(f"✅ Config {config_key}={expected_value} found in {Path(filepath).name}")
                return True
            else:
                print(f"⚠️  Config {config_key}={expected_value} NOT found in {Path(filepath).name}")
                return False
    except Exception as e:
        print(f"❌ Error reading {filepath}: {e}")
        return False

def main():
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║           🔍 AI ENGINE V8.3 INSTALLATION VERIFICATION            ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
    """)
    
    base_dir = Path(__file__).parent
    run_spark_gui = base_dir / "run_spark_gui"
    
    print("📁 Checking required files...\n")
    
    all_ok = True
    
    # Required files
    print("1️⃣  Required Files:")
    all_ok &= check_file_exists(
        run_spark_gui / "advanced_ai_engine_v8.py",
        "AI Engine V8.3"
    )
    all_ok &= check_file_exists(
        run_spark_gui / "advanced_ai_tab_v8.py",
        "AI Tab V8.3"
    )
    all_ok &= check_file_exists(
        base_dir / "test_ai_v8_fix.py",
        "Test Script"
    )
    
    print("\n2️⃣  Old Files (should be deleted):")
    all_ok &= check_file_deleted(
        run_spark_gui / "advanced_ai_tab_old.py",
        "Old AI Tab"
    )
    all_ok &= check_file_deleted(
        run_spark_gui / "advanced_ai_tab_v2.py",
        "AI Tab V2"
    )
    all_ok &= check_file_deleted(
        run_spark_gui / "advanced_ai_engine.py",
        "Old AI Engine"
    )
    
    print("\n3️⃣  Configuration Check:")
    
    # Check V8.3 configs in advanced_ai_engine_v8.py
    engine_file = run_spark_gui / "advanced_ai_engine_v8.py"
    if engine_file.exists():
        with open(engine_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check temperature
        if "temperature: float = 0.0" in content or "temperature=0.0" in content:
            print("✅ temperature=0.0 configured")
        else:
            print("⚠️  temperature may not be 0.0")
            all_ok = False
        
        # Check system instruction
        if "system_instruction" in content and "CODE GENERATOR MACHINE" in content:
            print("✅ System instruction configured")
        else:
            print("⚠️  System instruction not found")
            all_ok = False
        
        # Check max_tokens limit
        if "max_output_tokens': min(self.config.max_tokens, 2048)" in content:
            print("✅ max_tokens limited to 2048")
        else:
            print("⚠️  max_tokens limit may not be set")
    
    # Check V8.3 configs in advanced_ai_tab_v8.py
    tab_file = run_spark_gui / "advanced_ai_tab_v8.py"
    if tab_file.exists():
        with open(tab_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check version in header
        if "V8.3" in content or "System Instruction" in content:
            print("✅ AI Tab is V8.3 edition")
        else:
            print("⚠️  AI Tab may not be V8.3")
            all_ok = False
        
        # Check default temperature
        if "temperature_var = tk.DoubleVar(value=0.0)" in content:
            print("✅ Default temperature=0.0 in UI")
        else:
            print("⚠️  Default temperature may not be 0.0 in UI")
    
    print("\n4️⃣  Documentation Files:")
    check_file_exists(base_dir / "AI_ENGINE_V8.3_SYSTEM_FIX.md", "Technical Docs")
    check_file_exists(base_dir / "APPLIED_V8.3_TO_PROGRAM.md", "Application Summary")
    check_file_exists(base_dir / "QUICK_START_V8.3.md", "Quick Start Guide")
    
    print("\n" + "="*70)
    if all_ok:
        print("""
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║                    ✅ INSTALLATION VERIFIED                       ║
║                                                                   ║
║  All files are present and configured correctly.                  ║
║  AI Engine V8.3 is ready to use!                                  ║
║                                                                   ║
║  Next steps:                                                      ║
║  1. Run: python test_ai_v8_fix.py (test AI engine)              ║
║  2. Run: python run_spark_gui/main.py (launch GUI)              ║
║  3. Open "Advanced AI" tab and test with your data               ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
        """)
    else:
        print("""
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║                  ⚠️  INSTALLATION INCOMPLETE                      ║
║                                                                   ║
║  Some files are missing or not configured correctly.              ║
║  Please check the errors above and fix them.                      ║
║                                                                   ║
║  Documentation:                                                   ║
║  - AI_ENGINE_V8.3_SYSTEM_FIX.md                                  ║
║  - APPLIED_V8.3_TO_PROGRAM.md                                    ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
        """)
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())
