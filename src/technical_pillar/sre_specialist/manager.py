"""
SRE Specialist Manager for the Qwen Profiler
Handles reliability engineering, monitoring, incident response, and performance optimization
"""
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
import logging
import asyncio
from enum import Enum
import time
import statistics
from collections import deque

from ...core.config import get_config
from ...core.memory.manager import MemoryManager, MemoryEntry, MemoryType
from ...core.validation_gates.manager import ValidationGates


class IncidentSeverity(Enum):
    """Severity levels for incidents"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class MonitoringType(Enum):
    """Types of monitoring performed"""
    SYSTEM = "system"
    APPLICATION = "application"
    CUSTOM = "custom"


class SREReport:
    """Represents an SRE report"""
    def __init__(self, report_type: str, data: Dict[str, Any], timestamp: datetime):
        self.report_type = report_type
        self.data = data
        self.timestamp = timestamp
        self.id = f"sre_report_{report_type}_{timestamp.isoformat()}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "report_type": self.report_type,
            "data": self.data,
            "timestamp": self.timestamp.isoformat()
        }


class SREReliabilityMetrics:
    """Container for SRE reliability metrics"""
    def __init__(self):
        self.uptime_percentage = 99.9  # Placeholder
        self.response_time_ms = 100    # Placeholder
        self.error_rate = 0.001        # Placeholder
        self.last_incident = None
        self.incidents_count = 0
        self.timestamp = datetime.now()


class SRESpecialist:
    """Manages reliability engineering, monitoring, incident response, and performance optimization"""

    def __init__(self, memory_manager: Optional[MemoryManager] = None,
                 validation_gates: Optional[ValidationGates] = None):
        self.config = get_config()
        self.memory_manager = memory_manager or MemoryManager()
        self.validation_gates = validation_gates or ValidationGates()
        self.logger = logging.getLogger(__name__)

        # System metrics
        self.metrics = SREReliabilityMetrics()

        # Incident tracking
        self.active_incidents: Dict[str, Dict[str, Any]] = {}
        self.incident_history: List[Dict[str, Any]] = []

        # Monitoring callbacks
        self.monitoring_callbacks: Dict[str, Callable] = {}

        # Metrics history for predictive analysis
        self.metrics_history: deque = deque(maxlen=100)  # Keep last 100 metric entries

        # Initialize system
        self._init_system_monitoring()
    
    def _init_system_monitoring(self):
        """Initialize system monitoring components"""
        # Store initial metrics in memory
        self._update_metrics_memory()
        
        # Register basic monitoring components
        self.register_monitoring_callback("system_health", self._check_system_health)
        self.register_monitoring_callback("resource_usage", self._check_resource_usage)
    
    def register_monitoring_callback(self, name: str, callback: Callable) -> bool:
        """Register a monitoring callback function"""
        if name in self.monitoring_callbacks:
            self.logger.warning(f"Monitoring callback {name} already exists")
            return False
        
        self.monitoring_callbacks[name] = callback
        self.logger.info(f"Registered monitoring callback: {name}")
        return True
    
    def _check_system_health(self) -> Dict[str, Any]:
        """Check overall system health"""
        # In a real implementation, this would check actual system health
        # For now, this is a placeholder
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "checks": {
                "memory_manager": "active",
                "validation_gates": "active",
                "config_manager": "active"
            }
        }
    
    def _check_resource_usage(self) -> Dict[str, Any]:
        """Check system resource usage"""
        # In a real implementation, this would check actual resource usage
        # For now, this is a placeholder
        return {
            "cpu_usage": 10,  # Percentage
            "memory_usage": 25,  # Percentage
            "disk_usage": 60,  # Percentage
            "timestamp": datetime.now().isoformat()
        }
    
    def run_monitoring_cycle(self) -> Dict[str, Any]:
        """Run a complete monitoring cycle"""
        results = {}
        
        for name, callback in self.monitoring_callbacks.items():
            try:
                result = callback()
                results[name] = result
            except Exception as e:
                self.logger.error(f"Monitoring callback {name} failed: {e}")
                results[name] = {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
        
        # Store monitoring results in memory
        monitoring_entry = MemoryEntry(
            id=f"monitoring_cycle_{datetime.now().isoformat()}",
            content=results,
            creation_time=datetime.now(),
            memory_type=MemoryType.SHORT_TERM,
            tags=["monitoring", "cycle"],
            ttl=self.config.timeout_seconds * 3  # Keep for 3x timeout duration
        )
        self.memory_manager.store(monitoring_entry)
        
        return results
    
    def create_incident(self, title: str, description: str, severity: IncidentSeverity,
                       source: str = "system") -> str:
        """Create a new incident"""
        incident_id = f"incident_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.active_incidents)}"
        
        incident = {
            "id": incident_id,
            "title": title,
            "description": description,
            "severity": severity.value,
            "source": source,
            "created_at": datetime.now().isoformat(),
            "status": "open",
            "assignee": None,
            "resolution_time": None
        }
        
        self.active_incidents[incident_id] = incident
        self.metrics.incidents_count += 1
        
        # Store incident in memory
        incident_entry = MemoryEntry(
            id=f"incident_{incident_id}",
            content=incident,
            creation_time=datetime.now(),
            memory_type=MemoryType.LONG_TERM,
            tags=["incident", severity.value, "active"],
            priority=10 if severity == IncidentSeverity.CRITICAL else 5
        )
        self.memory_manager.store(incident_entry)
        
        self.logger.warning(f"Created incident {incident_id}: {title} (Severity: {severity.value})")
        
        # Update metrics memory
        self._update_metrics_memory()
        
        return incident_id
    
    def resolve_incident(self, incident_id: str, resolution_notes: str = "") -> bool:
        """Resolve an active incident"""
        if incident_id not in self.active_incidents:
            return False
        
        incident = self.active_incidents[incident_id]
        incident["status"] = "resolved"
        incident["resolution_time"] = datetime.now().isoformat()
        incident["resolution_notes"] = resolution_notes
        
        # Move from active to history
        self.incident_history.append(incident)
        del self.active_incidents[incident_id]
        
        # Update memory entry
        incident_entry = self.memory_manager.retrieve(f"incident_{incident_id}")
        if incident_entry:
            incident_entry.content = incident
            self.memory_manager.store(incident_entry)
        
        # Store resolution in memory as well
        resolution_entry = MemoryEntry(
            id=f"incident_resolution_{incident_id}",
            content={
                "incident_id": incident_id,
                "resolution": incident,
                "resolved_at": datetime.now().isoformat()
            },
            creation_time=datetime.now(),
            memory_type=MemoryType.LONG_TERM,
            tags=["incident", "resolution"],
            priority=7
        )
        self.memory_manager.store(resolution_entry)
        
        self.logger.info(f"Resolved incident {incident_id}")
        return True
    
    def get_active_incidents(self) -> List[Dict[str, Any]]:
        """Get all active incidents"""
        return list(self.active_incidents.values())
    
    def get_incident_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get incident history (most recent first)"""
        return self.incident_history[-limit:]
    
    def _update_metrics_memory(self):
        """Update reliability metrics in memory"""
        metrics_data = {
            "uptime_percentage": self.metrics.uptime_percentage,
            "response_time_ms": self.metrics.response_time_ms,
            "error_rate": self.metrics.error_rate,
            "last_incident": self.metrics.last_incident,
            "incidents_count": self.metrics.incidents_count,
            "timestamp": self.metrics.timestamp.isoformat()
        }

        # Add to metrics history for predictive analysis
        self.metrics_history.append(metrics_data.copy())

        # Store metrics in memory
        metrics_entry = MemoryEntry(
            id="sre_reliability_metrics",
            content=metrics_data,
            creation_time=self.metrics.timestamp,
            memory_type=MemoryType.SHORT_TERM,
            tags=["sre", "metrics", "reliability"],
            ttl=timedelta(hours=1)  # Metrics expire after 1 hour
        )
        self.memory_manager.store(metrics_entry)
    
    def update_reliability_metrics(self, uptime: Optional[float] = None,
                                  response_time: Optional[float] = None,
                                  error_rate: Optional[float] = None) -> bool:
        """Update reliability metrics"""
        updated = False

        if uptime is not None:
            self.metrics.uptime_percentage = uptime
            updated = True

        if response_time is not None:
            self.metrics.response_time_ms = response_time
            updated = True

        if error_rate is not None:
            self.metrics.error_rate = error_rate
            updated = True

        if updated:
            self.metrics.timestamp = datetime.now()
            self._update_metrics_memory()

        return updated
    
    def generate_sre_report(self, report_type: str = "reliability") -> SREReport:
        """Generate an SRE report"""
        if report_type == "reliability":
            data = {
                "metrics": {
                    "uptime_percentage": self.metrics.uptime_percentage,
                    "response_time_ms": self.metrics.response_time_ms,
                    "error_rate": self.metrics.error_rate
                },
                "incidents": {
                    "active_count": len(self.active_incidents),
                    "total_count": self.metrics.incidents_count,
                    "history_count": len(self.incident_history),
                },
                "monitoring_status": {name: "registered" for name in self.monitoring_callbacks.keys()}
            }
        elif report_type == "incident_summary":
            data = {
                "active_incidents": [
                    {k: v for k, v in incident.items() if k != 'description'} 
                    for incident in self.active_incidents.values()
                ],
                "recent_resolved": [
                    {k: v for k, v in incident.items() if k in ['id', 'title', 'severity', 'created_at', 'resolution_time']} 
                    for incident in self.incident_history[-10:]
                ]
            }
        else:
            data = {"error": f"Unknown report type: {report_type}"}
        
        report = SREReport(report_type, data, datetime.now())
        
        # Store report in memory
        report_entry = MemoryEntry(
            id=report.id,
            content=report.to_dict(),
            creation_time=report.timestamp,
            memory_type=MemoryType.SHORT_TERM,
            tags=["sre", "report", report_type],
            ttl=timedelta(hours=6)  # Reports expire after 6 hours
        )
        self.memory_manager.store(report_entry)
        
        return report
    
    def run_performance_optimization(self, target_component: str = None) -> Dict[str, Any]:
        """Run performance optimization routines"""
        optimization_results = {
            "component": target_component or "system-wide",
            "optimizations_applied": [],
            "performance_improvement": {},
            "timestamp": datetime.now().isoformat()
        }

        # Placeholder for actual optimization logic
        # In a real system, this would identify and apply performance optimizations

        # For now, just return placeholder results
        optimization_results["performance_improvement"] = {
            "response_time_reduction": 0,  # in ms
            "resource_efficiency": 0,  # percentage
            "throughput_improvement": 0  # percentage
        }

        # Store optimization results in memory
        optimization_entry = MemoryEntry(
            id=f"optimization_{target_component or 'system'}_{datetime.now().isoformat()}",
            content=optimization_results,
            creation_time=datetime.now(),
            memory_type=MemoryType.SHORT_TERM,
            tags=["sre", "optimization"],
            ttl=timedelta(hours=4)
        )
        self.memory_manager.store(optimization_entry)

        return optimization_results

    def predict_system_metrics(self, look_ahead_hours: int = 1) -> Dict[str, Any]:
        """Predict system metrics using historical data"""
        if len(self.metrics_history) < 3:
            # Not enough data to make predictions
            return {
                "predictions": {},
                "confidence": 0.0,
                "message": "Insufficient historical data for predictions"
            }

        # Calculate trends from historical data
        uptimes = [m["uptime_percentage"] for m in self.metrics_history if "uptime_percentage" in m]
        response_times = [m["response_time_ms"] for m in self.metrics_history if "response_time_ms" in m]
        error_rates = [m["error_rate"] for m in self.metrics_history if "error_rate" in m]

        predictions = {}
        confidence = 0.0

        # Predict uptime (assuming trend continues)
        if len(uptimes) >= 3:
            try:
                # Calculate average change per metric entry
                uptime_changes = [uptimes[i+1] - uptimes[i] for i in range(len(uptimes)-1)]
                avg_change = statistics.mean(uptime_changes)
                predicted_uptime = uptimes[-1] + (avg_change * look_ahead_hours)
                predicted_uptime = max(0.0, min(100.0, predicted_uptime))  # Keep between 0-100%
                predictions["predicted_uptime"] = predicted_uptime
            except:
                pass

        # Predict response time
        if len(response_times) >= 3:
            try:
                response_changes = [response_times[i+1] - response_times[i] for i in range(len(response_times)-1)]
                avg_change = statistics.mean(response_changes)
                predicted_response = response_times[-1] + (avg_change * look_ahead_hours)
                predicted_response = max(0, predicted_response)  # Response time can't be negative
                predictions["predicted_response_time"] = predicted_response
            except:
                pass

        # Predict error rate
        if len(error_rates) >= 3:
            try:
                error_changes = [error_rates[i+1] - error_rates[i] for i in range(len(error_rates)-1)]
                avg_change = statistics.mean(error_changes)
                predicted_error_rate = error_rates[-1] + (avg_change * look_ahead_hours)
                predicted_error_rate = max(0.0, min(1.0, predicted_error_rate))  # Keep between 0-1
                predictions["predicted_error_rate"] = predicted_error_rate
            except:
                pass

        # Simple confidence calculation based on data availability and stability
        if predictions:
            confidence = min(0.95, len(self.metrics_history) / 100.0 * 2)  # Max 95% confidence

        prediction_data = {
            "predictions": predictions,
            "confidence": confidence,
            "look_ahead_hours": look_ahead_hours,
            "historical_data_points": len(self.metrics_history),
            "timestamp": datetime.now().isoformat()
        }

        # Store prediction in memory
        prediction_entry = MemoryEntry(
            id=f"prediction_{datetime.now().isoformat()}",
            content=prediction_data,
            creation_time=datetime.now(),
            memory_type=MemoryType.SHORT_TERM,
            tags=["sre", "prediction", "forecasting"],
            ttl=timedelta(hours=2)  # Keep predictions for 2 hours
        )
        self.memory_manager.store(prediction_entry)

        return prediction_data

    def detect_anomalies(self) -> List[Dict[str, Any]]:
        """Detect anomalies in system metrics using statistical methods"""
        if len(self.metrics_history) < 5:
            # Not enough data to detect anomalies
            return []

        anomalies = []

        # Check for uptime anomalies
        uptimes = [m["uptime_percentage"] for m in self.metrics_history if "uptime_percentage" in m]
        if len(uptimes) >= 5:
            mean_uptime = statistics.mean(uptimes)
            stdev_uptime = statistics.stdev(uptimes) if len(uptimes) > 1 else 0
            current_uptime = uptimes[-1]

            # Identify if current uptime is more than 2 standard deviations from the mean
            if stdev_uptime > 0 and abs(current_uptime - mean_uptime) > 2 * stdev_uptime:
                anomalies.append({
                    "metric": "uptime",
                    "current_value": current_uptime,
                    "mean_value": mean_uptime,
                    "threshold": 2 * stdev_uptime,
                    "severity": "high" if abs(current_uptime - mean_uptime) > 3 * stdev_uptime else "medium",
                    "timestamp": datetime.now().isoformat()
                })

        # Check for response time anomalies
        response_times = [m["response_time_ms"] for m in self.metrics_history if "response_time_ms" in m]
        if len(response_times) >= 5:
            mean_response = statistics.mean(response_times)
            stdev_response = statistics.stdev(response_times) if len(response_times) > 1 else 0
            current_response = response_times[-1]

            if stdev_response > 0 and abs(current_response - mean_response) > 2 * stdev_response:
                anomalies.append({
                    "metric": "response_time",
                    "current_value": current_response,
                    "mean_value": mean_response,
                    "threshold": 2 * stdev_response,
                    "severity": "high" if abs(current_response - mean_response) > 3 * stdev_response else "medium",
                    "timestamp": datetime.now().isoformat()
                })

        # Check for error rate anomalies
        error_rates = [m["error_rate"] for m in self.metrics_history if "error_rate" in m]
        if len(error_rates) >= 5:
            mean_error_rate = statistics.mean(error_rates)
            stdev_error_rate = statistics.stdev(error_rates) if len(error_rates) > 1 else 0
            current_error_rate = error_rates[-1]

            if stdev_error_rate > 0 and abs(current_error_rate - mean_error_rate) > 2 * stdev_error_rate:
                anomalies.append({
                    "metric": "error_rate",
                    "current_value": current_error_rate,
                    "mean_value": mean_error_rate,
                    "threshold": 2 * stdev_error_rate,
                    "severity": "high" if abs(current_error_rate - mean_error_rate) > 3 * stdev_error_rate else "medium",
                    "timestamp": datetime.now().isoformat()
                })

        # Store anomalies in memory
        if anomalies:
            anomaly_entry = MemoryEntry(
                id=f"anomalies_{datetime.now().isoformat()}",
                content={
                    "anomalies": anomalies,
                    "timestamp": datetime.now().isoformat()
                },
                creation_time=datetime.now(),
                memory_type=MemoryType.SHORT_TERM,
                tags=["sre", "anomaly", "detection"],
                ttl=timedelta(hours=4)  # Keep anomalies for 4 hours
            )
            self.memory_manager.store(anomaly_entry)

        return anomalies

    def get_predictive_sre_dashboard(self) -> Dict[str, Any]:
        """Generate a predictive SRE dashboard with forecasts and anomaly detection"""
        # Get standard SRE dashboard
        dashboard = self.get_sre_dashboard()

        # Add predictive elements
        prediction = self.predict_system_metrics(look_ahead_hours=1)
        anomalies = self.detect_anomalies()

        predictive_dashboard = {
            **dashboard,
            "predictions": {
                "next_hour": prediction
            },
            "anomalies": {
                "count": len(anomalies),
                "items": anomalies
            },
            "health_score": self._calculate_health_score(anomalies, prediction)
        }

        return predictive_dashboard

    def _calculate_health_score(self, anomalies: List[Dict], prediction: Dict[str, Any]) -> float:
        """Calculate an overall system health score based on anomalies and predictions"""
        # Base health score is 100
        health_score = 100.0

        # Deduct points for anomalies
        for anomaly in anomalies:
            severity_deduction = {
                "low": 5,
                "medium": 15,
                "high": 30
            }
            health_score -= severity_deduction.get(anomaly.get("severity", "medium"), 15)

        # Deduct points based on confidence in predictions
        if prediction.get("confidence", 1.0) < 0.5:
            health_score -= 10  # Low confidence predictions are risky

        # Deduct points if predictions show degradation
        predictions = prediction.get("predictions", {})
        if predictions.get("predicted_error_rate", 0) > 0.05:  # More than 5%
            health_score -= 10
        if predictions.get("predicted_response_time", 0) > 1000:  # More than 1 second
            health_score -= 10

        # Ensure score is between 0 and 100
        return max(0.0, min(100.0, health_score))
    
    def get_sre_dashboard(self) -> Dict[str, Any]:
        """Generate a comprehensive SRE dashboard"""
        dashboard = {
            "reliability_metrics": {
                "uptime": f"{self.metrics.uptime_percentage}%",
                "avg_response_time": f"{self.metrics.response_time_ms}ms",
                "error_rate": f"{self.metrics.error_rate * 100}%"
            },
            "incidents": {
                "active": len(self.active_incidents),
                "today": len([i for i in self.active_incidents.values() 
                             if datetime.fromisoformat(i['created_at'].replace('Z', '+00:00')) 
                             >= datetime.now().replace(hour=0, minute=0, second=0)]),
                "total_count": self.metrics.incidents_count
            },
            "monitoring": {
                "registered_callbacks": len(self.monitoring_callbacks),
                "last_cycle": datetime.now().isoformat()
            },
            "active_incidents": [
                {k: v for k, v in incident.items() if k in ['id', 'title', 'severity', 'created_at']}
                for incident in self.active_incidents.values()
            ],
            "timestamp": datetime.now().isoformat()
        }
        
        return dashboard