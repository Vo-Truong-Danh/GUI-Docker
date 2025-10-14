"""
Advanced Code Quality Checker
Analyzes code for quality issues, complexity, and best practices
Version: 1.0.0
"""
import os
import re
import ast
from typing import Dict, List, Tuple
from pathlib import Path
from collections import defaultdict


class CodeQualityChecker:
    """Advanced code quality analysis"""
    
    def __init__(self, logger=None):
        self.logger = logger
        self.issues = []
        
        # Quality thresholds
        self.max_line_length = 120
        self.max_function_lines = 50
        self.max_complexity = 10
        self.max_parameters = 5
    
    def analyze_file(self, file_path: str) -> Dict:
        """Analyze a single Python file"""
        issues = []
        metrics = {
            'lines': 0,
            'code_lines': 0,
            'comment_lines': 0,
            'blank_lines': 0,
            'functions': 0,
            'classes': 0,
            'imports': 0
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
                
                metrics['lines'] = len(lines)
                
                # Line-by-line analysis
                for line_num, line in enumerate(lines, 1):
                    stripped = line.strip()
                    
                    # Count line types
                    if not stripped:
                        metrics['blank_lines'] += 1
                    elif stripped.startswith('#'):
                        metrics['comment_lines'] += 1
                    else:
                        metrics['code_lines'] += 1
                    
                    # Check line length
                    if len(line) > self.max_line_length:
                        issues.append({
                            'line': line_num,
                            'type': 'line_length',
                            'severity': 'low',
                            'message': f'Line exceeds {self.max_line_length} characters ({len(line)} chars)'
                        })
                    
                    # Check for common issues
                    if 'TODO' in stripped or 'FIXME' in stripped:
                        issues.append({
                            'line': line_num,
                            'type': 'todo',
                            'severity': 'info',
                            'message': 'TODO/FIXME comment found'
                        })
                    
                    if 'print(' in stripped and not stripped.startswith('#'):
                        issues.append({
                            'line': line_num,
                            'type': 'debug_code',
                            'severity': 'low',
                            'message': 'Print statement (consider using logging)'
                        })
                
                # AST analysis
                try:
                    tree = ast.parse(content)
                    
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            metrics['functions'] += 1
                            
                            # Check function complexity
                            complexity = self._calculate_complexity(node)
                            if complexity > self.max_complexity:
                                issues.append({
                                    'line': node.lineno,
                                    'type': 'high_complexity',
                                    'severity': 'medium',
                                    'message': f'Function {node.name} has high complexity ({complexity})'
                                })
                            
                            # Check parameter count
                            param_count = len(node.args.args)
                            if param_count > self.max_parameters:
                                issues.append({
                                    'line': node.lineno,
                                    'type': 'too_many_params',
                                    'severity': 'medium',
                                    'message': f'Function {node.name} has too many parameters ({param_count})'
                                })
                            
                            # Check function length
                            func_lines = node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 0
                            if func_lines > self.max_function_lines:
                                issues.append({
                                    'line': node.lineno,
                                    'type': 'long_function',
                                    'severity': 'medium',
                                    'message': f'Function {node.name} is too long ({func_lines} lines)'
                                })
                        
                        elif isinstance(node, ast.ClassDef):
                            metrics['classes'] += 1
                        
                        elif isinstance(node, (ast.Import, ast.ImportFrom)):
                            metrics['imports'] += 1
                
                except SyntaxError as e:
                    issues.append({
                        'line': e.lineno if hasattr(e, 'lineno') else 0,
                        'type': 'syntax_error',
                        'severity': 'critical',
                        'message': f'Syntax error: {str(e)}'
                    })
            
            return {
                'file': file_path,
                'metrics': metrics,
                'issues': issues,
                'quality_score': self._calculate_quality_score(metrics, issues)
            }
        
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to analyze {file_path}: {e}")
            return {'file': file_path, 'error': str(e)}
    
    def analyze_directory(self, directory: str) -> Dict:
        """Analyze entire directory"""
        all_issues = []
        all_metrics = defaultdict(int)
        files_analyzed = 0
        errors = []
        
        try:
            for root, dirs, files in os.walk(directory):
                # Skip common non-source directories
                dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'venv', 'env', 'logs']]
                
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        result = self.analyze_file(file_path)
                        
                        if 'error' in result:
                            errors.append(result)
                        else:
                            files_analyzed += 1
                            all_issues.extend(result['issues'])
                            
                            for key, value in result['metrics'].items():
                                all_metrics[key] += value
            
            # Calculate overall quality score
            total_issues = len(all_issues)
            critical_issues = sum(1 for i in all_issues if i['severity'] == 'critical')
            high_issues = sum(1 for i in all_issues if i['severity'] == 'high')
            medium_issues = sum(1 for i in all_issues if i['severity'] == 'medium')
            
            overall_score = 100 - (critical_issues * 20) - (high_issues * 10) - (medium_issues * 5) - (total_issues * 0.5)
            overall_score = max(0, min(100, overall_score))
            
            return {
                'directory': directory,
                'files_analyzed': files_analyzed,
                'total_metrics': dict(all_metrics),
                'total_issues': total_issues,
                'issues_by_severity': {
                    'critical': critical_issues,
                    'high': high_issues,
                    'medium': medium_issues,
                    'low': sum(1 for i in all_issues if i['severity'] == 'low'),
                    'info': sum(1 for i in all_issues if i['severity'] == 'info')
                },
                'issues': all_issues,
                'quality_score': overall_score,
                'errors': errors
            }
        
        except Exception as e:
            if self.logger:
                self.logger.error(f"Directory analysis failed: {e}")
            return {'error': str(e)}
    
    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity of a function"""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            # Count decision points
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity
    
    def _calculate_quality_score(self, metrics: Dict, issues: List) -> float:
        """Calculate quality score for a file"""
        score = 100.0
        
        # Deduct points for issues
        for issue in issues:
            if issue['severity'] == 'critical':
                score -= 20
            elif issue['severity'] == 'high':
                score -= 10
            elif issue['severity'] == 'medium':
                score -= 5
            elif issue['severity'] == 'low':
                score -= 2
        
        # Bonus for good practices
        if metrics.get('comment_lines', 0) > 0:
            comment_ratio = metrics['comment_lines'] / max(metrics.get('code_lines', 1), 1)
            if 0.1 <= comment_ratio <= 0.3:  # 10-30% comments is good
                score += 5
        
        return max(0, min(100, score))
    
    def get_report_summary(self, report: Dict) -> str:
        """Generate human-readable summary"""
        lines = []
        lines.append("=" * 80)
        lines.append("CODE QUALITY REPORT")
        lines.append("=" * 80)
        lines.append(f"Directory: {report.get('directory', 'N/A')}")
        lines.append(f"Files analyzed: {report.get('files_analyzed', 0)}")
        lines.append(f"Quality Score: {report.get('quality_score', 0):.1f}/100")
        lines.append("")
        
        metrics = report.get('total_metrics', {})
        lines.append("Code Metrics:")
        lines.append(f"  Total lines: {metrics.get('lines', 0)}")
        lines.append(f"  Code lines: {metrics.get('code_lines', 0)}")
        lines.append(f"  Comment lines: {metrics.get('comment_lines', 0)}")
        lines.append(f"  Functions: {metrics.get('functions', 0)}")
        lines.append(f"  Classes: {metrics.get('classes', 0)}")
        lines.append("")
        
        issues = report.get('issues_by_severity', {})
        lines.append(f"Issues (Total: {report.get('total_issues', 0)}):")
        lines.append(f"  🔴 Critical: {issues.get('critical', 0)}")
        lines.append(f"  🟠 High: {issues.get('high', 0)}")
        lines.append(f"  🟡 Medium: {issues.get('medium', 0)}")
        lines.append(f"  🟢 Low: {issues.get('low', 0)}")
        lines.append(f"  ℹ️  Info: {issues.get('info', 0)}")
        lines.append("=" * 80)
        
        return "\n".join(lines)


# Global instance
_code_quality_checker = None


def get_code_quality_checker(logger=None) -> CodeQualityChecker:
    """Get or create global code quality checker"""
    global _code_quality_checker
    if _code_quality_checker is None:
        _code_quality_checker = CodeQualityChecker(logger)
    return _code_quality_checker
