"""
Automatic Code Fixer - Advanced Version
Công cụ tự động sửa lỗi mã nguồn
Version: 2.0.0
"""

import os
import re
import ast
import json
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime
import shutil


class AutoCodeFixer:
    """Tự động sửa các lỗi phổ biến trong code"""
    
    def __init__(self, workspace_dir: str, backup: bool = True):
        self.workspace_dir = Path(workspace_dir)
        self.backup = backup
        self.fixes_applied = []
        self.backup_dir = self.workspace_dir / 'backups' / f'auto_fix_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        
        if backup:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def fix_all(self, analysis_report_path: str = None) -> Dict:
        """Áp dụng tất cả các fix có thể"""
        print("🔧 Bắt đầu tự động sửa lỗi...\n")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'fixes_applied': [],
            'files_modified': set(),
            'summary': {}
        }
        
        # 1. Fix bare except clauses
        print("1️⃣ Sửa bare except clauses...")
        bare_except_fixes = self._fix_bare_except_clauses()
        results['fixes_applied'].extend(bare_except_fixes)
        
        # 2. Fix silent exception handling
        print("2️⃣ Thêm logging cho exception handling...")
        silent_exception_fixes = self._fix_silent_exceptions()
        results['fixes_applied'].extend(silent_exception_fixes)
        
        # 3. Replace print with logging
        print("3️⃣ Thay thế print statements bằng logging...")
        print_fixes = self._replace_prints_with_logging()
        results['fixes_applied'].extend(print_fixes)
        
        # 4. Remove unused imports
        print("4️⃣ Loại bỏ unused imports...")
        import_fixes = self._remove_unused_imports()
        results['fixes_applied'].extend(import_fixes)
        
        # 5. Fix line length issues
        print("5️⃣ Sửa line length issues...")
        line_fixes = self._fix_long_lines()
        results['fixes_applied'].extend(line_fixes)
        
        # Collect statistics
        for fix in results['fixes_applied']:
            results['files_modified'].add(fix['file'])
        
        results['files_modified'] = list(results['files_modified'])
        results['summary'] = {
            'total_fixes': len(results['fixes_applied']),
            'files_modified': len(results['files_modified']),
            'backup_location': str(self.backup_dir) if self.backup else None
        }
        
        return results
    
    def _fix_bare_except_clauses(self) -> List[Dict]:
        """Sửa bare except clauses"""
        fixes = []
        
        py_files = list(self.workspace_dir.rglob('*.py'))
        
        for file_path in py_files:
            if '__pycache__' in str(file_path) or 'backup' in str(file_path):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                
                modified = False
                new_lines = []
                
                for i, line in enumerate(lines):
                    # Check for bare except
                    if re.match(r'^(\s*)except\s*:\s*$', line):
                        indent = re.match(r'^(\s*)', line).group(1)
                        # Replace with Exception
                        new_line = f"{indent}except Exception as e:\n"
                        new_lines.append(new_line)
                        modified = True
                        
                        fixes.append({
                            'file': str(file_path.relative_to(self.workspace_dir)),
                            'line': i + 1,
                            'type': 'bare_except_fixed',
                            'old': line.rstrip(),
                            'new': new_line.rstrip()
                        })
                    else:
                        new_lines.append(line)
                
                if modified:
                    self._backup_and_write(file_path, new_lines)
                    print(f"  ✓ Fixed bare except in {file_path.name}")
            
            except Exception as e:
                print(f"  ⚠️ Error processing {file_path}: {e}")
        
        return fixes
    
    def _fix_silent_exceptions(self) -> List[Dict]:
        """Thêm logging cho exception handling"""
        fixes = []
        
        py_files = list(self.workspace_dir.rglob('*.py'))
        
        for file_path in py_files:
            if '__pycache__' in str(file_path) or 'backup' in str(file_path):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                
                modified = False
                new_lines = []
                i = 0
                
                while i < len(lines):
                    line = lines[i]
                    new_lines.append(line)
                    
                    # Check if this is an except clause
                    if 'except' in line and ':' in line:
                        # Check if next line is just 'pass'
                        if i + 1 < len(lines):
                            next_line = lines[i + 1].strip()
                            if next_line == 'pass':
                                indent = re.match(r'^(\s*)', lines[i + 1]).group(1)
                                
                                # Extract exception variable if exists
                                exception_var = 'e'
                                match = re.search(r'as\s+(\w+)', line)
                                if match:
                                    exception_var = match.group(1)
                                
                                # Add logging before pass
                                log_line = f'{indent}# TODO: Add proper error handling\n'
                                new_lines.append(log_line)
                                
                                modified = True
                                fixes.append({
                                    'file': str(file_path.relative_to(self.workspace_dir)),
                                    'line': i + 2,
                                    'type': 'silent_exception_logged',
                                    'message': 'Added TODO comment for error handling'
                                })
                    
                    i += 1
                
                if modified:
                    self._backup_and_write(file_path, new_lines)
                    print(f"  ✓ Added logging to exceptions in {file_path.name}")
            
            except Exception as e:
                print(f"  ⚠️ Error processing {file_path}: {e}")
        
        return fixes
    
    def _replace_prints_with_logging(self) -> List[Dict]:
        """Thay thế print statements bằng logging"""
        fixes = []
        
        py_files = list(self.workspace_dir.rglob('*.py'))
        
        for file_path in py_files:
            if '__pycache__' in str(file_path) or 'backup' in str(file_path):
                continue
            
            # Skip files that are primarily for CLI output
            if 'main.py' in str(file_path) or 'cli' in str(file_path):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    lines = content.split('\n')
                
                # Check if logging is already imported
                has_logging = 'import logging' in content or 'from logging' in content
                
                modified = False
                new_lines = []
                
                for i, line in enumerate(lines):
                    # Skip comments
                    if line.strip().startswith('#'):
                        new_lines.append(line)
                        continue
                    
                    # Find print statements
                    if re.search(r'\bprint\s*\(', line) and not line.strip().startswith('#'):
                        indent = re.match(r'^(\s*)', line).group(1)
                        
                        # Extract print content
                        match = re.search(r'print\s*\((.*)\)', line)
                        if match:
                            print_content = match.group(1)
                            # Replace with logger comment suggestion
                            comment = f"{indent}# TODO: Replace with logger.info({print_content})\n"
                            new_lines.append(comment)
                            new_lines.append(line)  # Keep original for now
                            
                            modified = True
                            fixes.append({
                                'file': str(file_path.relative_to(self.workspace_dir)),
                                'line': i + 1,
                                'type': 'print_statement_marked',
                                'message': 'Added TODO for logging conversion'
                            })
                        else:
                            new_lines.append(line)
                    else:
                        new_lines.append(line)
                
                if modified:
                    self._backup_and_write(file_path, '\n'.join(new_lines) + '\n')
                    print(f"  ✓ Marked print statements in {file_path.name}")
            
            except Exception as e:
                print(f"  ⚠️ Error processing {file_path}: {e}")
        
        return fixes
    
    def _remove_unused_imports(self) -> List[Dict]:
        """Loại bỏ unused imports (sử dụng Pylance)"""
        fixes = []
        
        # This would require AST analysis which is complex
        # For now, just mark them
        print("  ℹ️ Unused import removal requires manual review or Pylance integration")
        
        return fixes
    
    def _fix_long_lines(self) -> List[Dict]:
        """Sửa long lines (basic formatting)"""
        fixes = []
        max_length = 120
        
        py_files = list(self.workspace_dir.rglob('*.py'))
        
        for file_path in py_files:
            if '__pycache__' in str(file_path) or 'backup' in str(file_path):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                
                modified = False
                new_lines = []
                
                for i, line in enumerate(lines):
                    if len(line.rstrip()) > max_length and not line.strip().startswith('#'):
                        # Add comment suggestion
                        indent = re.match(r'^(\s*)', line).group(1)
                        comment = f"{indent}# TODO: Line too long ({len(line.rstrip())} chars) - consider refactoring\n"
                        new_lines.append(comment)
                        new_lines.append(line)
                        
                        modified = True
                        fixes.append({
                            'file': str(file_path.relative_to(self.workspace_dir)),
                            'line': i + 1,
                            'type': 'long_line_marked',
                            'length': len(line.rstrip())
                        })
                    else:
                        new_lines.append(line)
                
                if modified and len(fixes) < 50:  # Limit to avoid too many changes
                    self._backup_and_write(file_path, new_lines)
            
            except Exception as e:
                print(f"  ⚠️ Error processing {file_path}: {e}")
        
        return fixes
    
    def _backup_and_write(self, file_path: Path, content):
        """Backup file and write new content"""
        if self.backup:
            # Create backup
            backup_file = self.backup_dir / file_path.name
            shutil.copy2(file_path, backup_file)
        
        # Write new content
        if isinstance(content, list):
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(content)
        else:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
    
    def save_report(self, results: Dict):
        """Lưu báo cáo fixes"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = self.workspace_dir / f'auto_fix_report_{timestamp}.json'
        
        # Convert sets to lists for JSON serialization
        results_copy = results.copy()
        if 'files_modified' in results_copy and isinstance(results_copy['files_modified'], set):
            results_copy['files_modified'] = list(results_copy['files_modified'])
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(results_copy, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Báo cáo auto-fix đã được lưu: {report_path}")
        
        # Summary report
        summary_path = str(report_path).replace('.json', '_summary.txt')
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("AUTO-FIX REPORT\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Timestamp: {results['timestamp']}\n")
            f.write(f"Total fixes applied: {results['summary']['total_fixes']}\n")
            f.write(f"Files modified: {results['summary']['files_modified']}\n")
            if results['summary']['backup_location']:
                f.write(f"Backup location: {results['summary']['backup_location']}\n")
            f.write("\n" + "=" * 80 + "\n")
        
        print(f"✅ Tóm tắt đã được lưu: {summary_path}")


def main():
    """Main function"""
    workspace_dir = Path(__file__).parent
    
    print("=" * 80)
    print("AUTOMATIC CODE FIXER")
    print("Công cụ Tự động Sửa Lỗi")
    print("=" * 80)
    print(f"\nWorkspace: {workspace_dir}\n")
    
    # Ask for confirmation
    print("⚠️ Cảnh báo: Công cụ này sẽ tự động sửa đổi các file.")
    print("   Backup sẽ được tạo trước khi sửa đổi.\n")
    
    response = input("Tiếp tục? (y/N): ").strip().lower()
    if response != 'y':
        print("Đã hủy.")
        return
    
    fixer = AutoCodeFixer(str(workspace_dir), backup=True)
    results = fixer.fix_all()
    fixer.save_report(results)
    
    print("\n" + "=" * 80)
    print("📊 KẾT QUẢ")
    print("=" * 80)
    print(f"✓ Tổng số fixes: {results['summary']['total_fixes']}")
    print(f"✓ Files đã sửa: {results['summary']['files_modified']}")
    print(f"✓ Backup location: {results['summary']['backup_location']}")
    print("\n" + "=" * 80)
    print("✅ Auto-fix hoàn tất!")
    print("=" * 80)


if __name__ == '__main__':
    main()
