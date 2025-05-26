"""
Performance monitoring and optimization utilities for Project Runner App.
"""

import time
import threading
import psutil
import gc
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from collections import deque
from config.settings import PERFORMANCE_CONFIG


@dataclass
class PerformanceMetrics:
    """Container for performance metrics."""
    timestamp: float
    memory_usage: int  # bytes
    cpu_percent: float
    thread_count: int
    process_count: int
    ui_update_queue_size: int
    database_cache_size: int


class PerformanceMonitor:
    """
    Monitor application performance and provide optimization recommendations.
    """
    
    def __init__(self, max_history=1000):
        self.max_history = max_history
        self._metrics_history = deque(maxlen=max_history)
        self._monitoring = False
        self._monitor_thread = None
        self._callbacks = []
        self._thresholds = {
            'memory_mb': 500,      # Alert if memory > 500MB
            'cpu_percent': 80,     # Alert if CPU > 80%
            'thread_count': 50,    # Alert if threads > 50
            'ui_queue_size': 100   # Alert if UI queue > 100
        }
        
    def start_monitoring(self, interval=5.0):
        """Start performance monitoring."""
        if self._monitoring:
            return
            
        self._monitoring = True
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval,),
            daemon=True
        )
        self._monitor_thread.start()
        
    def stop_monitoring(self):
        """Stop performance monitoring."""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=1.0)
            
    def _monitor_loop(self, interval):
        """Main monitoring loop."""
        while self._monitoring:
            try:
                metrics = self._collect_metrics()
                self._metrics_history.append(metrics)
                
                # Check thresholds and trigger callbacks
                self._check_thresholds(metrics)
                
                time.sleep(interval)
                
            except Exception as e:
                print(f"Performance monitoring error: {e}")
                time.sleep(interval)
                
    def _collect_metrics(self) -> PerformanceMetrics:
        """Collect current performance metrics."""
        try:
            process = psutil.Process()
            
            # Memory usage
            memory_info = process.memory_info()
            memory_usage = memory_info.rss
            
            # CPU usage
            cpu_percent = process.cpu_percent()
            
            # Thread count
            thread_count = process.num_threads()
            
            # Process count (children)
            try:
                children = process.children(recursive=True)
                process_count = len(children)
            except psutil.NoSuchProcess:
                process_count = 0
                
            return PerformanceMetrics(
                timestamp=time.time(),
                memory_usage=memory_usage,
                cpu_percent=cpu_percent,
                thread_count=thread_count,
                process_count=process_count,
                ui_update_queue_size=0,  # Will be updated by UI components
                database_cache_size=0    # Will be updated by database
            )
            
        except Exception as e:
            print(f"Error collecting metrics: {e}")
            return PerformanceMetrics(
                timestamp=time.time(),
                memory_usage=0,
                cpu_percent=0,
                thread_count=0,
                process_count=0,
                ui_update_queue_size=0,
                database_cache_size=0
            )
            
    def _check_thresholds(self, metrics: PerformanceMetrics):
        """Check if metrics exceed thresholds."""
        alerts = []
        
        memory_mb = metrics.memory_usage / (1024 * 1024)
        if memory_mb > self._thresholds['memory_mb']:
            alerts.append(f"High memory usage: {memory_mb:.1f}MB")
            
        if metrics.cpu_percent > self._thresholds['cpu_percent']:
            alerts.append(f"High CPU usage: {metrics.cpu_percent:.1f}%")
            
        if metrics.thread_count > self._thresholds['thread_count']:
            alerts.append(f"High thread count: {metrics.thread_count}")
            
        if metrics.ui_update_queue_size > self._thresholds['ui_queue_size']:
            alerts.append(f"Large UI queue: {metrics.ui_update_queue_size}")
            
        if alerts:
            for callback in self._callbacks:
                try:
                    callback(alerts, metrics)
                except Exception as e:
                    print(f"Performance callback error: {e}")
                    
    def add_alert_callback(self, callback):
        """Add callback for performance alerts."""
        self._callbacks.append(callback)
        
    def get_current_metrics(self) -> Optional[PerformanceMetrics]:
        """Get the most recent metrics."""
        return self._metrics_history[-1] if self._metrics_history else None
        
    def get_metrics_history(self, count: int = None) -> List[PerformanceMetrics]:
        """Get metrics history."""
        if count is None:
            return list(self._metrics_history)
        return list(self._metrics_history)[-count:]
        
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary statistics."""
        if not self._metrics_history:
            return {}
            
        recent_metrics = list(self._metrics_history)[-10:]  # Last 10 measurements
        
        memory_values = [m.memory_usage / (1024 * 1024) for m in recent_metrics]
        cpu_values = [m.cpu_percent for m in recent_metrics]
        thread_values = [m.thread_count for m in recent_metrics]
        
        return {
            'memory_mb': {
                'current': memory_values[-1] if memory_values else 0,
                'average': sum(memory_values) / len(memory_values) if memory_values else 0,
                'max': max(memory_values) if memory_values else 0
            },
            'cpu_percent': {
                'current': cpu_values[-1] if cpu_values else 0,
                'average': sum(cpu_values) / len(cpu_values) if cpu_values else 0,
                'max': max(cpu_values) if cpu_values else 0
            },
            'threads': {
                'current': thread_values[-1] if thread_values else 0,
                'average': sum(thread_values) / len(thread_values) if thread_values else 0,
                'max': max(thread_values) if thread_values else 0
            },
            'uptime_seconds': time.time() - recent_metrics[0].timestamp if recent_metrics else 0
        }
        
    def suggest_optimizations(self) -> List[str]:
        """Suggest performance optimizations based on metrics."""
        suggestions = []
        summary = self.get_performance_summary()
        
        if not summary:
            return suggestions
            
        # Memory optimization suggestions
        if summary['memory_mb']['current'] > 300:
            suggestions.append("Consider reducing output buffer size or clearing old project data")
            
        if summary['memory_mb']['max'] > 500:
            suggestions.append("High memory usage detected - enable aggressive garbage collection")
            
        # CPU optimization suggestions
        if summary['cpu_percent']['average'] > 50:
            suggestions.append("High CPU usage - consider reducing UI update frequency")
            
        # Thread optimization suggestions
        if summary['threads']['current'] > 30:
            suggestions.append("Many threads active - consider limiting concurrent processes")
            
        return suggestions
        
    def force_cleanup(self):
        """Force memory cleanup and garbage collection."""
        try:
            # Force garbage collection
            gc.collect()
            
            # Additional cleanup can be added here
            print("Forced memory cleanup completed")
            
        except Exception as e:
            print(f"Error during forced cleanup: {e}")


# Global performance monitor instance
_performance_monitor = None


def get_performance_monitor() -> PerformanceMonitor:
    """Get the global performance monitor instance."""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor


def start_performance_monitoring():
    """Start global performance monitoring."""
    monitor = get_performance_monitor()
    monitor.start_monitoring()
    
    # Add default alert callback
    def default_alert_callback(alerts, metrics):
        for alert in alerts:
            print(f"Performance Alert: {alert}")
            
    monitor.add_alert_callback(default_alert_callback)


def get_performance_stats() -> Dict[str, Any]:
    """Get current performance statistics."""
    monitor = get_performance_monitor()
    return monitor.get_performance_summary()


def suggest_optimizations() -> List[str]:
    """Get performance optimization suggestions."""
    monitor = get_performance_monitor()
    return monitor.suggest_optimizations() 