"""
Security Auditor Module
Comprehensive security analysis and vulnerability detection
Version: 1.0.0
"""
import re
import os
import hashlib
from typing import Dict, List, Set, Tuple
from pathlib import Path
from datetime import datetime


class SecurityAuditor:
    """Security auditing and vulnerability detection"""
    
    def __init__(self, logger=None):
        self.logger = logger
        self.vulnerabilities = []
        self.security_score = 100
        
        # Security patterns to detect
        self.patterns = {
            'sql_injection': [
                r'execute\s*\(\s*["\'].*?\%s.*?["\']',
                r'cursor\.execute\s*\(\s*f["\']',
                r'\.format\s*\(.*?sql',
            ],
            'command_injection': [
                r'os\.system\s*\(',
                r'subprocess\.call\s*\(.*?shell\s*=\s*True',
                r'eval\s*\(',
                r'exec\s*\(',
            ],
            'path_traversal': [
                r'open\s*\(\s*.*?\+.*?\)',
                r'\.\./',
                r'\.\.\\\\',
            ],
            'hardcoded_secrets': [
                r'password\s*=\s*["\'][^"\']+["\']',
                r'api[_-]?key\s*=\s*["\'][^"\']+["\']',
                r'secret\s*=\s*["\'][^"\']+["\']',
                r'token\s*=\s*["\'][^"\']+["\']',
            ],
            'weak_crypto': [
                r'hashlib\.md5',
                r'hashlib\.sha1',
                r'random\.random\(',
            ],
            'unsafe_deserialization': [
                r'pickle\.loads',
                r'yaml\.load\s*\(',
                r'json\.loads\s*\(.*?request',
            ]
        }
    
    def scan_file(self, file_path: str) -> Dict:
        """Scan a single file for vulnerabilities"""
        vulnerabilities = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
                
                for vuln_type, patterns in self.patterns.items():
                    for pattern in patterns:
                        for line_num, line in enumerate(lines, 1):
                            if re.search(pattern, line, re.IGNORECASE):
                                vulnerabilities.append({
                                    'file': file_path,
                                    'line': line_num,
                                    'type': vuln_type,
                                    'code': line.strip(),
                                    'severity': self._get_severity(vuln_type)
                                })
            
            return {
                'file': file_path,
                'vulnerabilities': vulnerabilities,
                'count': len(vulnerabilities)
            }
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to scan {file_path}: {e}")
            return {'file': file_path, 'error': str(e)}
    
    def scan_directory(self, directory: str, extensions: List[str] = None) -> Dict:
        """Scan entire directory for vulnerabilities"""
        if extensions is None:
            extensions = ['.py']
        
        all_vulnerabilities = []
        scanned_files = 0
        errors = []
        
        try:
            for root, dirs, files in os.walk(directory):
                # Skip common non-source directories
                dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'venv', 'env']]
                
                for file in files:
                    if any(file.endswith(ext) for ext in extensions):
                        file_path = os.path.join(root, file)
                        result = self.scan_file(file_path)
                        
                        if 'error' in result:
                            errors.append(result)
                        else:
                            scanned_files += 1
                            all_vulnerabilities.extend(result['vulnerabilities'])
            
            # Calculate security score
            critical_count = sum(1 for v in all_vulnerabilities if v['severity'] == 'CRITICAL')
            high_count = sum(1 for v in all_vulnerabilities if v['severity'] == 'HIGH')
            medium_count = sum(1 for v in all_vulnerabilities if v['severity'] == 'MEDIUM')
            
            score = 100 - (critical_count * 20) - (high_count * 10) - (medium_count * 5)
            score = max(0, score)
            
            return {
                'timestamp': datetime.now().isoformat(),
                'directory': directory,
                'files_scanned': scanned_files,
                'total_vulnerabilities': len(all_vulnerabilities),
                'vulnerabilities': all_vulnerabilities,
                'by_severity': {
                    'CRITICAL': critical_count,
                    'HIGH': high_count,
                    'MEDIUM': medium_count,
                    'LOW': len(all_vulnerabilities) - critical_count - high_count - medium_count
                },
                'security_score': score,
                'errors': errors
            }
        except Exception as e:
            if self.logger:
                self.logger.error(f"Directory scan failed: {e}")
            return {'error': str(e)}
    
    def _get_severity(self, vuln_type: str) -> str:
        """Get severity level for vulnerability type"""
        severity_map = {
            'sql_injection': 'CRITICAL',
            'command_injection': 'CRITICAL',
            'unsafe_deserialization': 'CRITICAL',
            'path_traversal': 'HIGH',
            'hardcoded_secrets': 'HIGH',
            'weak_crypto': 'MEDIUM',
        }
        return severity_map.get(vuln_type, 'LOW')
    
    def check_file_permissions(self, directory: str) -> Dict:
        """Check for insecure file permissions"""
        issues = []
        
        try:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        stats = os.stat(file_path)
                        mode = oct(stats.st_mode)[-3:]
                        
                        # Check if file is world-writable
                        if mode[-1] in ['2', '3', '6', '7']:
                            issues.append({
                                'file': file_path,
                                'issue': 'World-writable permissions',
                                'mode': mode,
                                'severity': 'HIGH'
                            })
                    except:
                        pass
            
            return {
                'issues': issues,
                'count': len(issues)
            }
        except Exception as e:
            if self.logger:
                self.logger.error(f"Permission check failed: {e}")
            return {'error': str(e)}
    
    def generate_security_report(self, directory: str) -> Dict:
        """Generate comprehensive security report"""
        code_scan = self.scan_directory(directory)
        permission_check = self.check_file_permissions(directory)
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'directory': directory,
            'code_vulnerabilities': code_scan,
            'permission_issues': permission_check,
            'overall_score': code_scan.get('security_score', 0)
        }
        
        # Generate recommendations
        recommendations = []
        
        if code_scan.get('by_severity', {}).get('CRITICAL', 0) > 0:
            recommendations.append('URGENT: Critical vulnerabilities found - immediate action required')
        
        if code_scan.get('by_severity', {}).get('HIGH', 0) > 0:
            recommendations.append('High priority vulnerabilities detected - review and fix soon')
        
        if permission_check.get('count', 0) > 0:
            recommendations.append('Insecure file permissions detected - restrict access')
        
        if code_scan.get('security_score', 0) < 70:
            recommendations.append('Overall security score is low - comprehensive security review needed')
        
        report['recommendations'] = recommendations
        
        if self.logger:
            self.logger.info(f"Security audit completed - Score: {report['overall_score']}")
        
        return report
    
    def get_vulnerability_summary(self, report: Dict) -> str:
        """Get human-readable summary of vulnerabilities"""
        code_vulns = report.get('code_vulnerabilities', {})
        
        summary = []
        summary.append("=" * 70)
        summary.append("SECURITY AUDIT REPORT")
        summary.append("=" * 70)
        summary.append(f"Timestamp: {report.get('timestamp', 'N/A')}")
        summary.append(f"Directory: {report.get('directory', 'N/A')}")
        summary.append(f"Security Score: {report.get('overall_score', 0)}/100")
        summary.append("")
        
        summary.append("Code Vulnerabilities:")
        summary.append(f"  Total: {code_vulns.get('total_vulnerabilities', 0)}")
        by_severity = code_vulns.get('by_severity', {})
        summary.append(f"  Critical: {by_severity.get('CRITICAL', 0)}")
        summary.append(f"  High: {by_severity.get('HIGH', 0)}")
        summary.append(f"  Medium: {by_severity.get('MEDIUM', 0)}")
        summary.append(f"  Low: {by_severity.get('LOW', 0)}")
        summary.append("")
        
        perm_issues = report.get('permission_issues', {})
        summary.append(f"Permission Issues: {perm_issues.get('count', 0)}")
        summary.append("")
        
        recommendations = report.get('recommendations', [])
        if recommendations:
            summary.append("Recommendations:")
            for rec in recommendations:
                summary.append(f"  - {rec}")
        
        summary.append("=" * 70)
        
        return "\n".join(summary)


# Global instance
_security_auditor = None


def get_security_auditor(logger=None) -> SecurityAuditor:
    """Get or create global security auditor"""
    global _security_auditor
    if _security_auditor is None:
        _security_auditor = SecurityAuditor(logger)
    return _security_auditor
