"""
System Integration Module - Tích hợp tất cả các cải tiến mới
Version: 1.0.0

Tính năng:
- Tích hợp docker_health_monitor
- Tích hợp enhanced_error_handler
- Tích hợp resource_optimizer
- Cung cấp API thống nhất
- Auto-initialization
- Health monitoring dashboard
"""

import threading
import time
from typing import Dict, Any, Optional, Callable
from datetime import datetime
import json


class SystemIntegration:
    """Tích hợp tất cả các module cải tiến"""
    
    def __init__(self):
        self._initialized = False
        self._lock = threading.RLock()
        
        # Module instances
        self.docker_monitor = None
        self.error_analyzer = None
        self.resource_optimizer = None
        
        # Integration status
        self.status = {
            'docker_monitor': False,
            'error_analyzer': False,
            'resource_optimizer': False,
            'last_update': None
        }
        
    def initialize(self, enable_monitoring: bool = True, 
                  enable_auto_cleanup: bool = True) -> Dict[str, Any]:
        """
        Khởi tạo tất cả các module
        
        Args:
            enable_monitoring: Bật auto-monitoring
            enable_auto_cleanup: Bật auto-cleanup
            
        Returns:
            dict: Kết quả khởi tạo
        """
        with self._lock:
            if self._initialized:
                return {'status': 'already_initialized', 'modules': self.status}
                
            results = {
                'timestamp': datetime.now().isoformat(),
                'modules': {},
                'errors': []
            }
            
            # Initialize Docker Health Monitor
            try:
                from docker_health_monitor import get_health_monitor
                self.docker_monitor = get_health_monitor()
                
                if enable_monitoring:
                    self.docker_monitor.start_monitoring()
                    
                self.status['docker_monitor'] = True
                results['modules']['docker_monitor'] = 'initialized'
                print("✅ Docker Health Monitor initialized")
            except Exception as e:
                results['errors'].append(f"Docker Monitor: {e}")
                print(f"⚠️ Failed to initialize Docker Monitor: {e}")
                
            # Initialize Enhanced Error Analyzer
            try:
                from enhanced_error_handler import get_error_analyzer
                self.error_analyzer = get_error_analyzer()
                self.status['error_analyzer'] = True
                results['modules']['error_analyzer'] = 'initialized'
                print("✅ Enhanced Error Analyzer initialized")
            except Exception as e:
                results['errors'].append(f"Error Analyzer: {e}")
                print(f"⚠️ Failed to initialize Error Analyzer: {e}")
                
            # Initialize Resource Optimizer
            try:
                from resource_optimizer import get_resource_optimizer
                self.resource_optimizer = get_resource_optimizer()
                
                if enable_auto_cleanup:
                    self.resource_optimizer.start_auto_cleanup()
                    
                self.status['resource_optimizer'] = True
                results['modules']['resource_optimizer'] = 'initialized'
                print("✅ Resource Optimizer initialized")
            except Exception as e:
                results['errors'].append(f"Resource Optimizer: {e}")
                print(f"⚠️ Failed to initialize Resource Optimizer: {e}")
                
            self._initialized = True
            self.status['last_update'] = datetime.now().isoformat()
            
            return results
            
    def shutdown(self):
        """Tắt tất cả các module"""
        with self._lock:
            print("🛑 Shutting down system integration...")
            
            # Stop Docker Monitor
            if self.docker_monitor:
                try:
                    self.docker_monitor.stop_monitoring()
                    print("  ✅ Docker Monitor stopped")
                except Exception as e:
                    print(f"  ⚠️ Error stopping Docker Monitor: {e}")
                    
            # Stop Resource Optimizer
            if self.resource_optimizer:
                try:
                    self.resource_optimizer.stop_auto_cleanup()
                    print("  ✅ Resource Optimizer stopped")
                except Exception as e:
                    print(f"  ⚠️ Error stopping Resource Optimizer: {e}")
                    
            self._initialized = False
            print("✅ System integration shutdown complete")
            
    def get_system_status(self) -> Dict[str, Any]:
        """Lấy trạng thái tổng quan của hệ thống"""
        status = {
            'timestamp': datetime.now().isoformat(),
            'initialized': self._initialized,
            'modules': self.status.copy()
        }
        
        # Docker Health
        if self.docker_monitor:
            try:
                status['docker_health'] = self.docker_monitor.get_health_summary()
            except Exception as e:
                status['docker_health'] = {'error': str(e)}
                
        # Resource Status
        if self.resource_optimizer:
            try:
                status['resources'] = self.resource_optimizer.get_system_resources()
                status['cleanup_stats'] = self.resource_optimizer.get_statistics()
            except Exception as e:
                status['resources'] = {'error': str(e)}
                
        # Error Analysis
        if self.error_analyzer:
            try:
                status['error_trends'] = self.error_analyzer.get_error_trends()
            except Exception as e:
                status['error_trends'] = {'error': str(e)}
                
        return status
        
    def handle_error(self, error: Exception, context: str = "") -> Dict[str, Any]:
        """
        Xử lý lỗi với enhanced error analyzer
        
        Args:
            error: Exception cần xử lý
            context: Context của lỗi
            
        Returns:
            dict: Phân tích lỗi với suggestions
        """
        if self.error_analyzer:
            return self.error_analyzer.analyze_error(error, context)
        else:
            return {
                'error': 'Error analyzer not initialized',
                'error_type': type(error).__name__,
                'error_message': str(error)
            }
            
    def trigger_cleanup(self, force: bool = True) -> Dict[str, Any]:
        """
        Kích hoạt cleanup ngay lập tức
        
        Args:
            force: Bắt buộc cleanup
            
        Returns:
            dict: Báo cáo cleanup
        """
        if self.resource_optimizer:
            return self.resource_optimizer.perform_cleanup(force=force)
        else:
            return {'error': 'Resource optimizer not initialized'}
            
    def get_recommendations(self) -> Dict[str, Any]:
        """Lấy tất cả recommendations từ các module"""
        recommendations = {
            'timestamp': datetime.now().isoformat(),
            'docker': [],
            'resources': [],
            'errors': []
        }
        
        # Docker recommendations
        if self.docker_monitor:
            try:
                health_report = self.docker_monitor.perform_health_check()
                recommendations['docker'] = health_report.get('recommendations', [])
            except Exception as e:
                recommendations['docker'] = [f"Error: {e}"]
                
        # Resource recommendations
        if self.resource_optimizer:
            try:
                recommendations['resources'] = self.resource_optimizer.get_recommendations()
            except Exception as e:
                recommendations['resources'] = [f"Error: {e}"]
                
        # Error recommendations
        if self.error_analyzer:
            try:
                trends = self.error_analyzer.get_error_trends()
                if trends.get('total_errors', 0) > 0:
                    recommendations['errors'] = [
                        f"Total errors: {trends['total_errors']}",
                        f"Trend: {trends.get('trends', 'unknown')}"
                    ]
            except Exception as e:
                recommendations['errors'] = [f"Error: {e}"]
                
        return recommendations
        
    def export_comprehensive_report(self, filepath: str = 'system_report.json') -> bool:
        """Export báo cáo toàn diện"""
        try:
            report = {
                'generated_at': datetime.now().isoformat(),
                'system_status': self.get_system_status(),
                'recommendations': self.get_recommendations()
            }
            
            # Add detailed reports from each module
            if self.docker_monitor:
                try:
                    report['docker_health_history'] = self.docker_monitor.get_health_history(20)
                except (AttributeError, TypeError, ValueError) as e:
                    print(f"⚠️ Cannot get Docker health history: {e}")
                    report['docker_health_history'] = None
                    
            if self.resource_optimizer:
                try:
                    report['resource_statistics'] = self.resource_optimizer.get_statistics()
                except (AttributeError, TypeError, ValueError) as e:
                    print(f"⚠️ Cannot get resource statistics: {e}")
                    report['resource_statistics'] = None
                    
            if self.error_analyzer:
                try:
                    report['error_analysis'] = self.error_analyzer.get_error_trends()
                except (AttributeError, TypeError, ValueError) as e:
                    print(f"⚠️ Cannot get error analysis: {e}")
                    report['error_analysis'] = None
                    
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, default=str)
                
            print(f"✅ Comprehensive report exported to: {filepath}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to export report: {e}")
            return False


# Global integration instance
_global_integration: Optional[SystemIntegration] = None


def get_system_integration() -> SystemIntegration:
    """Lấy hoặc tạo instance global"""
    global _global_integration
    if _global_integration is None:
        _global_integration = SystemIntegration()
    return _global_integration


# Convenience functions
def initialize_enhanced_system(enable_monitoring: bool = True,
                              enable_auto_cleanup: bool = True) -> Dict[str, Any]:
    """Khởi tạo hệ thống cải tiến"""
    integration = get_system_integration()
    return integration.initialize(enable_monitoring, enable_auto_cleanup)


def shutdown_enhanced_system():
    """Tắt hệ thống cải tiến"""
    integration = get_system_integration()
    integration.shutdown()


def get_system_dashboard() -> Dict[str, Any]:
    """Lấy dashboard tổng quan"""
    integration = get_system_integration()
    return integration.get_system_status()


def handle_error_enhanced(error: Exception, context: str = "") -> Dict[str, Any]:
    """Xử lý lỗi với enhanced analyzer"""
    integration = get_system_integration()
    return integration.handle_error(error, context)


def cleanup_system_now(force: bool = True) -> Dict[str, Any]:
    """Cleanup hệ thống ngay"""
    integration = get_system_integration()
    return integration.trigger_cleanup(force)


def get_all_recommendations() -> Dict[str, Any]:
    """Lấy tất cả recommendations"""
    integration = get_system_integration()
    return integration.get_recommendations()


# Example usage
if __name__ == '__main__':
    print("=" * 70)
    print("SYSTEM INTEGRATION - INITIALIZATION")
    print("=" * 70)
    
    # Initialize
    init_result = initialize_enhanced_system(
        enable_monitoring=True,
        enable_auto_cleanup=True
    )
    print(json.dumps(init_result, indent=2))
    
    # Wait a bit for monitoring to collect data
    print("\n⏳ Waiting for initial data collection...")
    time.sleep(5)
    
    # Get dashboard
    print("\n" + "=" * 70)
    print("SYSTEM DASHBOARD")
    print("=" * 70)
    dashboard = get_system_dashboard()
    print(json.dumps(dashboard, indent=2, default=str))
    
    # Get recommendations
    print("\n" + "=" * 70)
    print("SYSTEM RECOMMENDATIONS")
    print("=" * 70)
    recommendations = get_all_recommendations()
    for category, recs in recommendations.items():
        if recs and category != 'timestamp':
            print(f"\n{category.upper()}:")
            for rec in recs:
                print(f"  • {rec}")
                
    # Test error handling
    print("\n" + "=" * 70)
    print("ERROR HANDLING TEST")
    print("=" * 70)
    test_error = ConnectionError("Cannot connect to Docker daemon")
    analysis = handle_error_enhanced(test_error, "Docker operation")
    print(f"Error Type: {analysis['error_type']}")
    print(f"Category: {analysis['category']}")
    print(f"Severity: {analysis['severity']}")
    print("Solutions:")
    for i, solution in enumerate(analysis.get('solutions', []), 1):
        print(f"  {i}. {solution}")
        
    # Trigger cleanup
    print("\n" + "=" * 70)
    print("SYSTEM CLEANUP")
    print("=" * 70)
    cleanup_report = cleanup_system_now(force=True)
    print(json.dumps(cleanup_report, indent=2, default=str))
    
    # Export comprehensive report
    print("\n" + "=" * 70)
    print("EXPORTING REPORT")
    print("=" * 70)
    integration = get_system_integration()
    integration.export_comprehensive_report('comprehensive_system_report.json')
    
    # Shutdown
    print("\n" + "=" * 70)
    print("SHUTDOWN")
    print("=" * 70)
    shutdown_enhanced_system()
