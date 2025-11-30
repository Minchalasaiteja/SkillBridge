"""
Observability Module: Logging, Tracing, and Metrics
Provides comprehensive monitoring and debugging capabilities
"""

import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum
from pythonjsonlogger import jsonlogger
from config import settings

# Setup structured logging
class LogLevel(str, Enum):
    """Log level enumeration"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class StructuredLogger:
    """Structured JSON logger for better observability"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(settings.log_level)
        
        # JSON handler
        json_handler = logging.StreamHandler()
        formatter = jsonlogger.JsonFormatter()
        json_handler.setFormatter(formatter)
        
        if not self.logger.handlers:
            self.logger.addHandler(json_handler)
    
    def log_event(self, level: LogLevel, message: str, **context):
        """Log structured event"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level.value,
            "message": message,
            **context
        }
        
        if level == LogLevel.DEBUG:
            self.logger.debug(json.dumps(log_data))
        elif level == LogLevel.INFO:
            self.logger.info(json.dumps(log_data))
        elif level == LogLevel.WARNING:
            self.logger.warning(json.dumps(log_data))
        elif level == LogLevel.ERROR:
            self.logger.error(json.dumps(log_data))
        elif level == LogLevel.CRITICAL:
            self.logger.critical(json.dumps(log_data))
    
    def info(self, message: str, **context):
        """Log info message"""
        self.log_event(LogLevel.INFO, message, **context)
    
    def debug(self, message: str, **context):
        """Log debug message"""
        self.log_event(LogLevel.DEBUG, message, **context)
    
    def warning(self, message: str, **context):
        """Log warning message"""
        self.log_event(LogLevel.WARNING, message, **context)
    
    def error(self, message: str, **context):
        """Log error message"""
        self.log_event(LogLevel.ERROR, message, **context)
    
    def critical(self, message: str, **context):
        """Log critical message"""
        self.log_event(LogLevel.CRITICAL, message, **context)


class ExecutionTracer:
    """Execution tracing for agents and operations"""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = StructuredLogger(f"tracer.{name}")
        self.traces = []
        self.start_time = None
    
    def start_trace(self, operation: str, **metadata):
        """Start tracing operation"""
        self.start_time = datetime.utcnow()
        trace_entry = {
            "operation": operation,
            "start_time": self.start_time.isoformat(),
            "metadata": metadata
        }
        self.traces.append(trace_entry)
        self.logger.info(f"Trace started: {operation}", operation=operation, **metadata)
    
    def end_trace(self, status: str = "success", result: Optional[Dict] = None):
        """End tracing operation"""
        if self.traces and self.start_time:
            end_time = datetime.utcnow()
            duration = (end_time - self.start_time).total_seconds()
            
            self.traces[-1].update({
                "end_time": end_time.isoformat(),
                "duration_seconds": duration,
                "status": status,
                "result": result
            })
            
            self.logger.info(
                f"Trace ended: {self.traces[-1]['operation']}",
                status=status,
                duration=duration,
                operation=self.traces[-1]['operation']
            )
    
    def get_traces(self) -> list:
        """Get all traces"""
        return self.traces


class MetricsCollector:
    """Collect metrics on agent performance"""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = StructuredLogger(f"metrics.{name}")
        self.metrics = {
            "execution_count": 0,
            "success_count": 0,
            "failure_count": 0,
            "total_duration": 0,
            "avg_duration": 0,
            "errors": []
        }
    
    def record_execution(self, duration: float, success: bool, error: Optional[str] = None):
        """Record execution metric"""
        self.metrics["execution_count"] += 1
        self.metrics["total_duration"] += duration
        self.metrics["avg_duration"] = self.metrics["total_duration"] / self.metrics["execution_count"]
        
        if success:
            self.metrics["success_count"] += 1
        else:
            self.metrics["failure_count"] += 1
            if error:
                self.metrics["errors"].append({
                    "timestamp": datetime.utcnow().isoformat(),
                    "error": error
                })
        
        self.logger.info(
            f"Execution recorded for {self.name}",
            component=self.name,
            duration=duration,
            success=success,
            execution_count=self.metrics["execution_count"]
        )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get metrics summary"""
        return self.metrics.copy()
    
    def reset(self):
        """Reset metrics"""
        self.metrics = {
            "execution_count": 0,
            "success_count": 0,
            "failure_count": 0,
            "total_duration": 0,
            "avg_duration": 0,
            "errors": []
        }


class ObservabilityManager:
    """Centralized observability management"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ObservabilityManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.loggers = {}
        self.tracers = {}
        self.metrics = {}
    
    def get_logger(self, name: str) -> StructuredLogger:
        """Get or create logger"""
        if name not in self.loggers:
            self.loggers[name] = StructuredLogger(name)
        return self.loggers[name]
    
    def get_tracer(self, name: str) -> ExecutionTracer:
        """Get or create tracer"""
        if name not in self.tracers:
            self.tracers[name] = ExecutionTracer(name)
        return self.tracers[name]
    
    def get_metrics(self, name: str) -> MetricsCollector:
        """Get or create metrics collector"""
        if name not in self.metrics:
            self.metrics[name] = MetricsCollector(name)
        return self.metrics[name]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get observability summary"""
        return {
            "loggers": list(self.loggers.keys()),
            "tracers": {name: tracer.get_traces() for name, tracer in self.tracers.items()},
            "metrics": {name: metrics.get_metrics() for name, metrics in self.metrics.items()}
        }


# Global observability manager
observability = ObservabilityManager()


def get_logger(name: str) -> StructuredLogger:
    """Get logger instance"""
    return observability.get_logger(name)


def get_tracer(name: str) -> ExecutionTracer:
    """Get tracer instance"""
    return observability.get_tracer(name)


def get_metrics(name: str) -> MetricsCollector:
    """Get metrics collector"""
    return observability.get_metrics(name)


def get_observability_summary() -> Dict[str, Any]:
    """Get observability summary"""
    return observability.get_summary()
