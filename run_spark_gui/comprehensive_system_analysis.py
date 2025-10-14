"""
Comprehensive System Analysis and Optimization Tool
Phân tích toàn diện và tối ưu hóa hệ thống
Version: 1.0.0
"""

import os
import sys
import json
import ast
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Set
from collections import defaultdict


class ComprehensiveSystemAnalyzer:
    """Công cụ phân tích và tối ưu hệ thống toàn diện"""
    
    def __init__(self, workspace_dir: str):
        self.workspace_dir = Path(workspace_dir)
        self.issues = []
        self.security_issues = []
        self.performance_issues = []
        self.code_smells = []
        self.unused_resources = []
        
    def analyze_all(self) -> Dict:
        """Phân tích toàn bộ hệ thống"""
        print("🔍 Bắt đầu phân tích toàn diện hệ thống...")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'workspace': str(self.workspace_dir),
            'summary': {},
            'detailed_issues': {},
            'recommendations': []
        }
        
        # 1. Phân tích lỗi logic
        print("\n📋 1. Phân tích lỗi logic và code quality...")
        logic_issues = self._analyze_logic_errors()
        results['detailed_issues']['logic_errors'] = logic_issues
        
        # 2. Phân tích bảo mật
        print("\n🔒 2. Phân tích bảo mật...")
        security_issues = self._analyze_security()
        results['detailed_issues']['security_issues'] = security_issues
        
        # 3. Phân tích error handling
        print("\n⚠️ 3. Phân tích error handling...")
        error_handling_issues = self._analyze_error_handling()
        results['detailed_issues']['error_handling'] = error_handling_issues
        
        # 4. Phân tích tài nguyên thừa
        print("\n🗑️ 4. Phân tích tài nguyên thừa...")
        unused_resources = self._analyze_unused_resources()
        results['detailed_issues']['unused_resources'] = unused_resources
        
        # 5. Phân tích performance
        print("\n⚡ 5. Phân tích performance...")
        performance_issues = self._analyze_performance()
        results['detailed_issues']['performance_issues'] = performance_issues
        
        # 6. Tạo khuyến nghị
        print("\n💡 6. Tạo khuyến nghị...")
        recommendations = self._generate_recommendations(results['detailed_issues'])
        results['recommendations'] = recommendations
        
        # Tạo summary
        results['summary'] = self._create_summary(results['detailed_issues'])
        
        return results
    
    def _analyze_logic_errors(self) -> Dict:
        """Phân tích lỗi logic"""
        issues = {
            'critical': [],
            'high': [],
            'medium': [],
            'low': []
        }
        
        py_files = list(self.workspace_dir.rglob('*.py'))
        
        for file_path in py_files:
            if '__pycache__' in str(file_path):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                    # Check for bare except clauses
                    for i, line in enumerate(lines, 1):
                        # Bare except
                        if re.search(r'except\s*:', line) and not line.strip().startswith('#'):
                            issues['high'].append({
                                'file': str(file_path.relative_to(self.workspace_dir)),
                                'line': i,
                                'type': 'bare_except',
                                'message': 'Bare except clause catches all exceptions',
                                'suggestion': 'Use specific exception types or Exception'
                            })
                        
                        # Pass in except block
                        if 'except' in line and i < len(lines):
                            next_line = lines[i].strip() if i < len(lines) else ''
                            if next_line == 'pass':
                                issues['medium'].append({
                                    'file': str(file_path.relative_to(self.workspace_dir)),
                                    'line': i + 1,
                                    'type': 'silent_exception',
                                    'message': 'Exception silently ignored with pass',
                                    'suggestion': 'Add logging or proper error handling'
                                })
                        
                        # Print statements
                        if re.search(r'\bprint\s*\(', line) and not line.strip().startswith('#'):
                            issues['low'].append({
                                'file': str(file_path.relative_to(self.workspace_dir)),
                                'line': i,
                                'type': 'print_statement',
                                'message': 'Print statement found (should use logging)',
                                'suggestion': 'Replace with logging.info/debug'
                            })
                        
                        # TODO/FIXME comments
                        if re.search(r'(TODO|FIXME|HACK|XXX)', line):
                            issues['low'].append({
                                'file': str(file_path.relative_to(self.workspace_dir)),
                                'line': i,
                                'type': 'todo_comment',
                                'message': 'TODO/FIXME comment found',
                                'suggestion': 'Address or create issue tracker item'
                            })
                    
                    # AST analysis
                    try:
                        tree = ast.parse(content)
                        
                        for node in ast.walk(tree):
                            # Unused imports
                            if isinstance(node, ast.Import):
                                for alias in node.names:
                                    imported_name = alias.asname or alias.name
                                    if not self._is_name_used(tree, imported_name):
                                        issues['low'].append({
                                            'file': str(file_path.relative_to(self.workspace_dir)),
                                            'line': node.lineno,
                                            'type': 'unused_import',
                                            'message': f'Unused import: {alias.name}',
                                            'suggestion': 'Remove unused import'
                                        })
                            
                            # Functions with too many parameters
                            if isinstance(node, ast.FunctionDef):
                                if len(node.args.args) > 7:
                                    issues['medium'].append({
                                        'file': str(file_path.relative_to(self.workspace_dir)),
                                        'line': node.lineno,
                                        'type': 'too_many_parameters',
                                        'message': f'Function {node.name} has {len(node.args.args)} parameters',
                                        'suggestion': 'Consider using config object or dataclass'
                                    })
                    
                    except SyntaxError as e:
                        issues['critical'].append({
                            'file': str(file_path.relative_to(self.workspace_dir)),
                            'line': e.lineno if hasattr(e, 'lineno') else 0,
                            'type': 'syntax_error',
                            'message': f'Syntax error: {str(e)}',
                            'suggestion': 'Fix syntax error'
                        })
            
            except Exception as e:
                print(f"⚠️ Error analyzing {file_path}: {e}")
        
        return issues
    
    def _analyze_security(self) -> Dict:
        """Phân tích bảo mật"""
        issues = {
            'critical': [],
            'high': [],
            'medium': [],
            'low': []
        }
        
        py_files = list(self.workspace_dir.rglob('*.py'))
        
        dangerous_patterns = [
            (r'eval\s*\(', 'eval() usage', 'critical', 'Avoid eval(), use safer alternatives'),
            (r'exec\s*\(', 'exec() usage', 'critical', 'Avoid exec(), use safer alternatives'),
            (r'__import__\s*\(', 'Dynamic import', 'high', 'Validate module names before import'),
            (r'subprocess\.call.*shell\s*=\s*True', 'Shell injection risk', 'critical', 'Use shell=False'),
            (r'os\.system\s*\(', 'Command injection risk', 'high', 'Use subprocess with list args'),
            (r'pickle\.loads?\s*\(', 'Pickle deserialization', 'high', 'Validate data source'),
            (r'yaml\.load\s*\((?!.*Loader)', 'Unsafe YAML loading', 'high', 'Use yaml.safe_load()'),
            (r'password\s*=\s*["\'].*["\']', 'Hardcoded password', 'critical', 'Use environment variables'),
            (r'api_key\s*=\s*["\'].*["\']', 'Hardcoded API key', 'critical', 'Use environment variables'),
            (r'secret\s*=\s*["\'].*["\']', 'Hardcoded secret', 'critical', 'Use environment variables'),
        ]
        
        for file_path in py_files:
            if '__pycache__' in str(file_path):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    
                    for i, line in enumerate(lines, 1):
                        if line.strip().startswith('#'):
                            continue
                            
                        for pattern, desc, severity, suggestion in dangerous_patterns:
                            if re.search(pattern, line):
                                issues[severity].append({
                                    'file': str(file_path.relative_to(self.workspace_dir)),
                                    'line': i,
                                    'type': 'security_risk',
                                    'message': f'{desc}: {line.strip()[:50]}...',
                                    'suggestion': suggestion
                                })
            
            except Exception as e:
                print(f"⚠️ Error analyzing {file_path}: {e}")
        
        return issues
    
    def _analyze_error_handling(self) -> Dict:
        """Phân tích error handling"""
        issues = {
            'improvements_needed': [],
            'missing_logging': [],
            'poor_practices': []
        }
        
        py_files = list(self.workspace_dir.rglob('*.py'))
        
        for file_path in py_files:
            if '__pycache__' in str(file_path):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    # Check for try-except blocks without logging
                    try_blocks = re.finditer(r'try:.*?except.*?:', content, re.DOTALL)
                    for match in try_blocks:
                        block = match.group()
                        if 'logger' not in block and 'logging' not in block and 'print' not in block:
                            issues['missing_logging'].append({
                                'file': str(file_path.relative_to(self.workspace_dir)),
                                'type': 'no_error_logging',
                                'message': 'Try-except block without logging',
                                'suggestion': 'Add logging to track errors'
                            })
                    
                    # Check for generic exception messages
                    if 'except Exception' in content:
                        issues['improvements_needed'].append({
                            'file': str(file_path.relative_to(self.workspace_dir)),
                            'type': 'generic_exception',
                            'message': 'Generic Exception catching',
                            'suggestion': 'Use specific exception types when possible'
                        })
            
            except Exception as e:
                print(f"⚠️ Error analyzing {file_path}: {e}")
        
        return issues
    
    def _analyze_unused_resources(self) -> Dict:
        """Phân tích tài nguyên thừa"""
        issues = {
            'unused_files': [],
            'duplicate_files': [],
            'large_files': [],
            'unused_dependencies': []
        }
        
        # Check for backup/temp files
        patterns = ['*.bak', '*.tmp', '*.old', '*~', '*.swp']
        for pattern in patterns:
            for file_path in self.workspace_dir.rglob(pattern):
                issues['unused_files'].append({
                    'file': str(file_path.relative_to(self.workspace_dir)),
                    'size': file_path.stat().st_size,
                    'suggestion': 'Consider removing backup/temp files'
                })
        
        # Check for large log files
        for log_file in self.workspace_dir.rglob('*.log'):
            size = log_file.stat().st_size
            if size > 10 * 1024 * 1024:  # > 10MB
                issues['large_files'].append({
                    'file': str(log_file.relative_to(self.workspace_dir)),
                    'size': size,
                    'size_mb': round(size / (1024 * 1024), 2),
                    'suggestion': 'Archive or clean old logs'
                })
        
        # Check for duplicate Python files
        file_hashes = defaultdict(list)
        for py_file in self.workspace_dir.rglob('*.py'):
            if '__pycache__' in str(py_file):
                continue
            try:
                with open(py_file, 'rb') as f:
                    content = f.read()
                    file_hash = hash(content)
                    file_hashes[file_hash].append(py_file)
            except:
                pass
        
        for file_hash, files in file_hashes.items():
            if len(files) > 1:
                issues['duplicate_files'].append({
                    'files': [str(f.relative_to(self.workspace_dir)) for f in files],
                    'suggestion': 'Review and remove duplicate files'
                })
        
        # Analyze requirements.txt
        req_file = self.workspace_dir / 'requirements.txt'
        if req_file.exists():
            try:
                with open(req_file, 'r') as f:
                    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                
                # Check for commented dependencies
                with open(req_file, 'r') as f:
                    lines = f.readlines()
                    commented = [line.strip() for line in lines if line.strip().startswith('#') and '=' in line]
                    
                if commented:
                    issues['unused_dependencies'].append({
                        'type': 'commented_dependencies',
                        'count': len(commented),
                        'suggestion': 'Remove commented dependencies or uncomment if needed'
                    })
            except:
                pass
        
        return issues
    
    def _analyze_performance(self) -> Dict:
        """Phân tích performance"""
        issues = {
            'optimization_opportunities': [],
            'memory_concerns': [],
            'io_concerns': []
        }
        
        py_files = list(self.workspace_dir.rglob('*.py'))
        
        performance_patterns = [
            (r'for .* in .*\.keys\(\):', 'Unnecessary .keys()', 'Iterate dict directly'),
            (r'len\(.*\)\s*==\s*0', 'Inefficient emptiness check', 'Use "not collection"'),
            (r'\+\s*=.*\[', 'List concatenation in loop', 'Use list.append() or list comprehension'),
            (r'\.append\(.*\n.*\.append\(', 'Multiple appends', 'Consider bulk operations'),
        ]
        
        for file_path in py_files:
            if '__pycache__' in str(file_path):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                    for i, line in enumerate(lines, 1):
                        for pattern, desc, suggestion in performance_patterns:
                            if re.search(pattern, line):
                                issues['optimization_opportunities'].append({
                                    'file': str(file_path.relative_to(self.workspace_dir)),
                                    'line': i,
                                    'issue': desc,
                                    'suggestion': suggestion
                                })
                    
                    # Check for file operations without context manager
                    if re.search(r'open\s*\([^)]+\)(?!\s*as\s)', content):
                        issues['io_concerns'].append({
                            'file': str(file_path.relative_to(self.workspace_dir)),
                            'issue': 'File opened without context manager',
                            'suggestion': 'Use "with open() as f:" to ensure proper resource cleanup'
                        })
            
            except Exception as e:
                print(f"⚠️ Error analyzing {file_path}: {e}")
        
        return issues
    
    def _is_name_used(self, tree: ast.AST, name: str) -> bool:
        """Check if a name is used in the AST"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id == name:
                return True
            if isinstance(node, ast.Attribute) and node.attr == name:
                return True
        return False
    
    def _generate_recommendations(self, issues: Dict) -> List[Dict]:
        """Tạo khuyến nghị dựa trên issues"""
        recommendations = []
        
        # Logic errors recommendations
        logic_issues = issues.get('logic_errors', {})
        critical_count = len(logic_issues.get('critical', []))
        high_count = len(logic_issues.get('high', []))
        
        if critical_count > 0:
            recommendations.append({
                'priority': 'CRITICAL',
                'category': 'Code Quality',
                'title': f'Sửa {critical_count} lỗi nghiêm trọng',
                'description': 'Các lỗi syntax và logic nghiêm trọng cần được khắc phục ngay lập tức',
                'action': 'Review và sửa từng lỗi critical'
            })
        
        if high_count > 5:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Error Handling',
                'title': 'Cải thiện error handling',
                'description': f'Phát hiện {high_count} bare except clauses',
                'action': 'Thay thế bare except bằng specific exception types'
            })
        
        # Security recommendations
        security_issues = issues.get('security_issues', {})
        security_critical = len(security_issues.get('critical', []))
        
        if security_critical > 0:
            recommendations.append({
                'priority': 'CRITICAL',
                'category': 'Security',
                'title': f'Khắc phục {security_critical} vấn đề bảo mật nghiêm trọng',
                'description': 'Phát hiện hardcoded credentials hoặc unsafe functions',
                'action': 'Di chuyển credentials sang environment variables, tránh eval/exec'
            })
        
        # Performance recommendations
        perf_issues = issues.get('performance_issues', {})
        if perf_issues.get('optimization_opportunities'):
            recommendations.append({
                'priority': 'MEDIUM',
                'category': 'Performance',
                'title': 'Tối ưu hóa performance',
                'description': f'Phát hiện {len(perf_issues["optimization_opportunities"])} cơ hội tối ưu',
                'action': 'Refactor code theo best practices'
            })
        
        # Resource cleanup recommendations
        unused = issues.get('unused_resources', {})
        if unused.get('unused_files') or unused.get('large_files'):
            total_size = sum(f.get('size', 0) for f in unused.get('large_files', []))
            recommendations.append({
                'priority': 'LOW',
                'category': 'Resource Management',
                'title': 'Dọn dẹp tài nguyên thừa',
                'description': f'Có thể giải phóng {total_size / (1024*1024):.1f} MB',
                'action': 'Archive logs cũ, xóa backup files không cần thiết'
            })
        
        return recommendations
    
    def _create_summary(self, issues: Dict) -> Dict:
        """Tạo summary từ issues"""
        summary = {
            'total_issues': 0,
            'by_severity': {
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0
            },
            'by_category': {}
        }
        
        for category, category_issues in issues.items():
            if isinstance(category_issues, dict):
                for severity in ['critical', 'high', 'medium', 'low']:
                    if severity in category_issues:
                        count = len(category_issues[severity])
                        summary['by_severity'][severity] += count
                        summary['total_issues'] += count
                        
                        if category not in summary['by_category']:
                            summary['by_category'][category] = 0
                        summary['by_category'][category] += count
        
        return summary
    
    def save_report(self, results: Dict, output_path: str = None):
        """Lưu báo cáo ra file"""
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = self.workspace_dir / f'system_analysis_report_{timestamp}.json'
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Báo cáo đã được lưu: {output_path}")
        
        # Also create a human-readable summary
        summary_path = str(output_path).replace('.json', '_summary.txt')
        self._save_summary_text(results, summary_path)
        print(f"✅ Tóm tắt đã được lưu: {summary_path}")
    
    def _save_summary_text(self, results: Dict, output_path: str):
        """Lưu báo cáo tóm tắt dạng text"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("BÁO CÁO PHÂN TÍCH HỆ THỐNG TOÀN DIỆN\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"Thời gian: {results['timestamp']}\n")
            f.write(f"Workspace: {results['workspace']}\n\n")
            
            # Summary
            summary = results['summary']
            f.write("TỔNG QUAN\n")
            f.write("-" * 80 + "\n")
            f.write(f"Tổng số vấn đề: {summary['total_issues']}\n\n")
            
            f.write("Phân loại theo mức độ nghiêm trọng:\n")
            for severity, count in summary['by_severity'].items():
                icon = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}.get(severity, '⚪')
                f.write(f"  {icon} {severity.upper()}: {count}\n")
            
            f.write("\nPhân loại theo danh mục:\n")
            for category, count in summary['by_category'].items():
                f.write(f"  • {category}: {count}\n")
            
            # Recommendations
            f.write("\n\nKHUYẾN NGHỊ\n")
            f.write("-" * 80 + "\n")
            for i, rec in enumerate(results['recommendations'], 1):
                f.write(f"\n{i}. [{rec['priority']}] {rec['title']}\n")
                f.write(f"   Danh mục: {rec['category']}\n")
                f.write(f"   Mô tả: {rec['description']}\n")
                f.write(f"   Hành động: {rec['action']}\n")
            
            f.write("\n" + "=" * 80 + "\n")


def main():
    """Main function"""
    workspace_dir = Path(__file__).parent
    
    print("=" * 80)
    print("COMPREHENSIVE SYSTEM ANALYSIS")
    print("Phân tích Toàn diện Hệ thống")
    print("=" * 80)
    print(f"\nWorkspace: {workspace_dir}\n")
    
    analyzer = ComprehensiveSystemAnalyzer(str(workspace_dir))
    results = analyzer.analyze_all()
    analyzer.save_report(results)
    
    print("\n" + "=" * 80)
    print("📊 TỔNG KẾT")
    print("=" * 80)
    summary = results['summary']
    print(f"✓ Tổng số vấn đề phát hiện: {summary['total_issues']}")
    print(f"  🔴 Critical: {summary['by_severity']['critical']}")
    print(f"  🟠 High: {summary['by_severity']['high']}")
    print(f"  🟡 Medium: {summary['by_severity']['medium']}")
    print(f"  🟢 Low: {summary['by_severity']['low']}")
    
    print(f"\n✓ Số khuyến nghị: {len(results['recommendations'])}")
    
    print("\n" + "=" * 80)
    print("✅ Phân tích hoàn tất!")
    print("=" * 80)


if __name__ == '__main__':
    main()
