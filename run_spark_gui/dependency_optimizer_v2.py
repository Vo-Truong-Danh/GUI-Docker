"""
Dependency Optimizer - Advanced Version
Công cụ tối ưu hóa và quản lý dependencies
Version: 2.0.0
"""

import os
import re
import ast
import subprocess
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict
import json


class DependencyOptimizer:
    """Tối ưu hóa dependencies và requirements"""
    
    def __init__(self, workspace_dir: str):
        self.workspace_dir = Path(workspace_dir)
        self.requirements_file = self.workspace_dir / 'requirements.txt'
        self.imports_used = set()
        self.packages_installed = set()
        self.unused_packages = []
        self.missing_packages = []
    
    def analyze_all(self) -> Dict:
        """Phân tích toàn bộ dependencies"""
        print("🔍 Analyzing dependencies...\n")
        
        results = {
            'imports_used': [],
            'packages_in_requirements': [],
            'unused_packages': [],
            'missing_packages': [],
            'optimization_suggestions': []
        }
        
        # 1. Scan all Python files for imports
        print("1️⃣ Scanning imports in Python files...")
        self.imports_used = self._scan_imports()
        results['imports_used'] = sorted(list(self.imports_used))
        print(f"   Found {len(self.imports_used)} unique imports")
        
        # 2. Read requirements.txt
        print("\n2️⃣ Reading requirements.txt...")
        if self.requirements_file.exists():
            requirements = self._parse_requirements()
            results['packages_in_requirements'] = requirements
            print(f"   Found {len(requirements)} packages in requirements.txt")
        else:
            print("   ⚠️ requirements.txt not found")
            return results
        
        # 3. Check for unused packages
        print("\n3️⃣ Checking for unused packages...")
        unused = self._find_unused_packages(requirements)
        results['unused_packages'] = unused
        if unused:
            print(f"   ⚠️ Found {len(unused)} potentially unused packages:")
            for pkg in unused[:5]:  # Show first 5
                print(f"      - {pkg}")
        else:
            print("   ✓ No unused packages found")
        
        # 4. Check for missing packages
        print("\n4️⃣ Checking for missing packages...")
        missing = self._find_missing_packages(requirements)
        results['missing_packages'] = missing
        if missing:
            print(f"   ⚠️ Found {len(missing)} potentially missing packages:")
            for pkg in missing[:5]:
                print(f"      - {pkg}")
        else:
            print("   ✓ No missing packages detected")
        
        # 5. Generate optimization suggestions
        print("\n5️⃣ Generating optimization suggestions...")
        suggestions = self._generate_suggestions(results)
        results['optimization_suggestions'] = suggestions
        
        return results
    
    def _scan_imports(self) -> Set[str]:
        """Scan tất cả imports trong Python files"""
        imports = set()
        
        py_files = list(self.workspace_dir.rglob('*.py'))
        
        for file_path in py_files:
            if '__pycache__' in str(file_path) or 'backup' in str(file_path):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Parse AST
                try:
                    tree = ast.parse(content)
                    
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                # Get top-level module name
                                module_name = alias.name.split('.')[0]
                                imports.add(module_name)
                        
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                module_name = node.module.split('.')[0]
                                imports.add(module_name)
                
                except SyntaxError:
                    # If AST parsing fails, use regex
                    import_lines = re.findall(r'^\s*(?:from|import)\s+(\w+)', content, re.MULTILINE)
                    imports.update(import_lines)
            
            except Exception as e:
                print(f"   ⚠️ Error scanning {file_path}: {e}")
        
        return imports
    
    def _parse_requirements(self) -> List[Dict]:
        """Parse requirements.txt"""
        requirements = []
        
        with open(self.requirements_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Parse package name and version
                match = re.match(r'^([a-zA-Z0-9_-]+)([>=<!=]+.*)?$', line)
                if match:
                    package_name = match.group(1)
                    version_spec = match.group(2) or ''
                    
                    requirements.append({
                        'name': package_name,
                        'version': version_spec,
                        'line': line_num,
                        'raw': line
                    })
        
        return requirements
    
    def _find_unused_packages(self, requirements: List[Dict]) -> List[Dict]:
        """Tìm packages không được sử dụng"""
        unused = []
        
        # Map of package name to common import names
        package_import_map = {
            'pyyaml': 'yaml',
            'pillow': 'PIL',
            'python-dateutil': 'dateutil',
            'beautifulsoup4': 'bs4',
            'scikit-learn': 'sklearn',
            'opencv-python': 'cv2',
            'python-dotenv': 'dotenv',
        }
        
        for req in requirements:
            package_name = req['name'].lower()
            
            # Get expected import name
            import_name = package_import_map.get(package_name, package_name)
            
            # Check if import is used
            if import_name not in self.imports_used and package_name not in self.imports_used:
                unused.append({
                    'package': req['name'],
                    'version': req['version'],
                    'line': req['line'],
                    'reason': 'No import found in code'
                })
        
        return unused
    
    def _find_missing_packages(self, requirements: List[Dict]) -> List[Dict]:
        """Tìm packages bị thiếu trong requirements"""
        missing = []
        
        # Standard library modules (không cần trong requirements)
        stdlib_modules = {
            'os', 'sys', 're', 'json', 'datetime', 'time', 'math', 'random',
            'collections', 'itertools', 'functools', 'pathlib', 'typing',
            'logging', 'threading', 'subprocess', 'shutil', 'copy', 'pickle',
            'tempfile', 'io', 'csv', 'sqlite3', 'urllib', 'http', 'email',
            'ast', 'traceback', 'enum', 'dataclasses', 'abc', 'contextlib'
        }
        
        # Get package names from requirements
        req_packages = {req['name'].lower() for req in requirements}
        
        # Package name mappings
        import_to_package = {
            'yaml': 'pyyaml',
            'PIL': 'pillow',
            'bs4': 'beautifulsoup4',
            'sklearn': 'scikit-learn',
            'cv2': 'opencv-python',
            'dotenv': 'python-dotenv',
        }
        
        for import_name in self.imports_used:
            # Skip stdlib modules
            if import_name in stdlib_modules:
                continue
            
            # Get actual package name
            package_name = import_to_package.get(import_name, import_name)
            
            # Check if in requirements
            if package_name.lower() not in req_packages:
                missing.append({
                    'import_name': import_name,
                    'package_name': package_name,
                    'reason': 'Used in code but not in requirements.txt'
                })
        
        return missing
    
    def _generate_suggestions(self, analysis: Dict) -> List[Dict]:
        """Tạo suggestions để tối ưu hóa"""
        suggestions = []
        
        # Suggestion 1: Remove unused packages
        if analysis['unused_packages']:
            suggestions.append({
                'priority': 'MEDIUM',
                'type': 'remove_unused',
                'title': f'Remove {len(analysis["unused_packages"])} unused packages',
                'description': 'These packages are listed in requirements.txt but not imported in code',
                'packages': [pkg['package'] for pkg in analysis['unused_packages']],
                'action': 'Review and remove if truly unused'
            })
        
        # Suggestion 2: Add missing packages
        if analysis['missing_packages']:
            suggestions.append({
                'priority': 'HIGH',
                'type': 'add_missing',
                'title': f'Add {len(analysis["missing_packages"])} missing packages',
                'description': 'These packages are imported but not in requirements.txt',
                'packages': [pkg['package_name'] for pkg in analysis['missing_packages']],
                'action': 'Add to requirements.txt'
            })
        
        # Suggestion 3: Pin versions
        unpinned = [
            req for req in analysis['packages_in_requirements']
            if not req['version'] or req['version'].strip() == ''
        ]
        if unpinned:
            suggestions.append({
                'priority': 'LOW',
                'type': 'pin_versions',
                'title': f'Pin versions for {len(unpinned)} packages',
                'description': 'These packages don\'t have version specifications',
                'packages': [req['name'] for req in unpinned],
                'action': 'Add version constraints for reproducibility'
            })
        
        # Suggestion 4: Update comments
        suggestions.append({
            'priority': 'LOW',
            'type': 'improve_documentation',
            'title': 'Improve requirements.txt documentation',
            'description': 'Add comments explaining what each package is used for',
            'action': 'Add descriptive comments for better maintainability'
        })
        
        return suggestions
    
    def optimize_requirements(self, backup: bool = True) -> str:
        """Tối ưu hóa requirements.txt"""
        if not self.requirements_file.exists():
            print("❌ requirements.txt not found")
            return None
        
        analysis = self.analyze_all()
        
        # Create backup
        if backup:
            backup_path = self.requirements_file.with_suffix('.txt.backup')
            import shutil
            shutil.copy2(self.requirements_file, backup_path)
            print(f"\n✅ Backup created: {backup_path}")
        
        # Read current requirements
        with open(self.requirements_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Build new requirements
        new_lines = []
        unused_packages = {pkg['package'].lower() for pkg in analysis['unused_packages']}
        
        # Add header
        new_lines.append("# ============================================================================\n")
        new_lines.append("# Project Dependencies - Optimized\n")
        new_lines.append(f"# Generated: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        new_lines.append("# ============================================================================\n\n")
        
        # Filter out unused packages
        for line in lines:
            stripped = line.strip()
            
            # Keep comments and empty lines
            if not stripped or stripped.startswith('#'):
                new_lines.append(line)
                continue
            
            # Check if package should be kept
            package_name = re.match(r'^([a-zA-Z0-9_-]+)', stripped)
            if package_name:
                pkg = package_name.group(1).lower()
                if pkg not in unused_packages:
                    new_lines.append(line)
                else:
                    # Comment out unused package
                    new_lines.append(f"# [UNUSED] {line}")
        
        # Add missing packages section
        if analysis['missing_packages']:
            new_lines.append("\n# Missing packages (consider adding):\n")
            for pkg in analysis['missing_packages']:
                new_lines.append(f"# {pkg['package_name']}  # Used in code as '{pkg['import_name']}'\n")
        
        # Write optimized requirements
        optimized_path = self.workspace_dir / 'requirements_optimized.txt'
        with open(optimized_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        
        print(f"\n✅ Optimized requirements saved: {optimized_path}")
        print(f"   Review the file and rename to requirements.txt if satisfied")
        
        return str(optimized_path)
    
    def save_analysis_report(self, analysis: Dict):
        """Lưu báo cáo phân tích"""
        report_path = self.workspace_dir / 'dependency_analysis_report.json'
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Analysis report saved: {report_path}")
        
        # Also create text summary
        summary_path = self.workspace_dir / 'dependency_analysis_summary.txt'
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("DEPENDENCY ANALYSIS SUMMARY\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"Total imports used: {len(analysis['imports_used'])}\n")
            f.write(f"Packages in requirements: {len(analysis['packages_in_requirements'])}\n")
            f.write(f"Unused packages: {len(analysis['unused_packages'])}\n")
            f.write(f"Missing packages: {len(analysis['missing_packages'])}\n\n")
            
            if analysis['unused_packages']:
                f.write("UNUSED PACKAGES:\n")
                for pkg in analysis['unused_packages']:
                    f.write(f"  - {pkg['package']}{pkg['version']}\n")
                f.write("\n")
            
            if analysis['missing_packages']:
                f.write("MISSING PACKAGES:\n")
                for pkg in analysis['missing_packages']:
                    f.write(f"  - {pkg['package_name']} (imported as '{pkg['import_name']}')\n")
                f.write("\n")
            
            f.write("OPTIMIZATION SUGGESTIONS:\n")
            for i, sug in enumerate(analysis['optimization_suggestions'], 1):
                f.write(f"\n{i}. [{sug['priority']}] {sug['title']}\n")
                f.write(f"   {sug['description']}\n")
                f.write(f"   Action: {sug['action']}\n")
            
            f.write("\n" + "=" * 80 + "\n")
        
        print(f"✅ Summary saved: {summary_path}")


def main():
    """Main function"""
    workspace_dir = Path(__file__).parent
    
    print("=" * 80)
    print("DEPENDENCY OPTIMIZER")
    print("Công cụ Tối ưu hóa Dependencies")
    print("=" * 80)
    print(f"\nWorkspace: {workspace_dir}\n")
    
    optimizer = DependencyOptimizer(str(workspace_dir))
    analysis = optimizer.analyze_all()
    optimizer.save_analysis_report(analysis)
    
    print("\n" + "=" * 80)
    print("📊 SUMMARY")
    print("=" * 80)
    print(f"✓ Imports used: {len(analysis['imports_used'])}")
    print(f"✓ Packages in requirements: {len(analysis['packages_in_requirements'])}")
    print(f"⚠️ Unused packages: {len(analysis['unused_packages'])}")
    print(f"⚠️ Missing packages: {len(analysis['missing_packages'])}")
    print(f"💡 Suggestions: {len(analysis['optimization_suggestions'])}")
    
    # Ask to optimize
    if analysis['unused_packages'] or analysis['missing_packages']:
        print("\n" + "=" * 80)
        response = input("\nOptimize requirements.txt? (y/N): ").strip().lower()
        if response == 'y':
            optimizer.optimize_requirements(backup=True)
    
    print("\n" + "=" * 80)
    print("✅ Analysis complete!")
    print("=" * 80)


if __name__ == '__main__':
    main()
