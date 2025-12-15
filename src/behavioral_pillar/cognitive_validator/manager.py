"""
Cognitive Validator Manager for the Qwen Profiler
Handles behavioral consistency monitoring, methodology adherence, and cognitive pattern validation
"""
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import logging
from enum import Enum

from ...core.config import get_config
from ...core.memory.manager import MemoryManager, MemoryEntry, MemoryType
from ...core.validation_gates.manager import ValidationGates, ValidationResult, GateStatus
from ..behavioral_architect.manager import BehavioralArchitect, BehavioralPattern


class CognitivePatternType(Enum):
    """Types of cognitive patterns to validate"""
    REASONING_FLOW = "reasoning_flow"
    RESPONSE_CONSISTENCY = "response_consistency"
    METHODOLOGY_ADHERENCE = "methodology_adherence"
    ASSUMPTION_VERIFICATION = "assumption_verification"
    CONTEXT_PRESERVATION = "context_preservation"


class CognitiveDriftType(Enum):
    """Types of cognitive drift to detect"""
    REASONING_DEVIATION = "reasoning_deviation"
    RESPONSE_INCONSISTENCY = "response_inconsistency"
    METHODOLOGY_VIOLATION = "methodology_violation"
    ASSUMPTION_BIAS = "assumption_bias"
    CONTEXT_COLLAPSE = "context_collapse"


class CognitiveValidator:
    """Manages behavioral consistency monitoring, methodology adherence, and cognitive pattern validation"""
    
    def __init__(self, memory_manager: Optional[MemoryManager] = None, 
                 validation_gates: Optional[ValidationGates] = None,
                 behavioral_architect: Optional[BehavioralArchitect] = None):
        self.config = get_config()
        self.memory_manager = memory_manager or MemoryManager()
        self.validation_gates = validation_gates or ValidationGates()
        self.behavioral_architect = behavioral_architect or BehavioralArchitect()
        self.logger = logging.getLogger(__name__)
        
        # Track cognitive patterns and drifts
        self.tracked_patterns: Dict[str, Dict[str, Any]] = {}
        self.detected_drifts: List[Dict[str, Any]] = []
        self.drift_history: List[Dict[str, Any]] = []
        
        # Initialize tracking system
        self._init_tracking_system()
    
    def _init_tracking_system(self):
        """Initialize the cognitive pattern tracking system"""
        # Initialize with common pattern templates
        self.tracked_patterns = {
            "default_reasoning_flow": {
                "type": CognitivePatternType.REASONING_FLOW.value,
                "definition": {
                    "required_steps": ["perceive", "analyze", "reason", "conclude"],
                    "validation_points": ["fact_check", "logic_validation", "consistency_check"]
                },
                "last_seen": datetime.now().isoformat(),
                "compliance_count": 0,
                "non_compliance_count": 0
            },
            "default_response_consistency": {
                "type": CognitivePatternType.RESPONSE_CONSISTENCY.value,
                "definition": {
                    "elements_to_track": ["tone", "format", "content_style"],
                    "consistency_threshold": 0.8
                },
                "last_seen": datetime.now().isoformat(),
                "compliance_count": 0,
                "non_compliance_count": 0
            }
        }
    
    def validate_behavioral_consistency(self, target_behavior: Dict[str, Any]) -> ValidationResult:
        """Validate behavioral consistency against established patterns"""
        # This is a simplified validation - in a real system, this would be more comprehensive
        issues = []
        
        # Check for consistency in responses
        responses = target_behavior.get("responses", [])
        if len(responses) > 1:
            # Compare first response with others for consistency
            first_response = responses[0]
            for i, response in enumerate(responses[1:], 1):
                if not self._compare_responses(first_response, response):
                    issues.append(f"Inconsistency detected between response 0 and response {i}")
        
        # Check for reasoning consistency
        reasoning_steps = target_behavior.get("reasoning_steps", [])
        if len(reasoning_steps) > 0:
            if not self._validate_reasoning_flow(reasoning_steps):
                issues.append("Reasoning flow deviates from expected pattern")
        
        # Determine status based on issues found
        if issues:
            status = GateStatus.FAIL
            message = f"Behavioral consistency validation failed with {len(issues)} issue(s)"
        else:
            status = GateStatus.PASS
            message = "Behavioral consistency validation passed"
        
        result = ValidationResult(
            gate=self.validation_gates._rules.get("behavior_consistency_check").gate
            if self.validation_gates._rules.get("behavior_consistency_check")
            else self.validation_gates._validate_behavioral_consistency.__code__.co_name,
            status=status,
            message=message,
            timestamp=datetime.now(),
            metadata={"validation_type": "behavioral_consistency", "issues_count": len(issues)},
            errors=issues
        )
        
        # Store validation result in memory
        self._store_validation_result(result, target_behavior)
        
        return result
    
    def _compare_responses(self, response1: Dict[str, Any], response2: Dict[str, Any]) -> bool:
        """Compare two responses for consistency"""
        # Simplified comparison - in a real system, this would use more sophisticated NLP
        keys_to_compare = ["tone", "format", "content_style"]
        
        for key in keys_to_compare:
            val1 = response1.get(key)
            val2 = response2.get(key)
            
            if val1 != val2:
                return False
        
        return True
    
    def _validate_reasoning_flow(self, reasoning_steps: List[Dict[str, Any]]) -> bool:
        """Validate that reasoning follows expected flow"""
        # Expected steps in a reasoning flow
        expected_steps = ["perceive", "analyze", "reason", "conclude"]
        
        # Check if all required steps are present
        step_types = [step.get("type") for step in reasoning_steps]
        
        for expected_step in expected_steps:
            if expected_step not in step_types:
                return False
        
        return True
    
    def validate_methodology_adherence(self, target_process: Dict[str, Any]) -> ValidationResult:
        """Validate adherence to established methodologies"""
        issues = []

        # Check if required methodology steps were performed
        required_steps = target_process.get("required_methodology", {}).get("steps", [])
        performed_steps = target_process.get("performed_steps", [])

        # Only check for missing steps if both required and performed steps are defined
        if required_steps and performed_steps:
            missing_steps = [step for step in required_steps if step not in performed_steps]
            if missing_steps:
                issues.extend([f"Missing required methodology step: {step}" for step in missing_steps])
        # If no required steps or no performed steps, consider it as passing during system initialization

        # Check if required validation gates were passed
        required_gates = target_process.get("required_methodology", {}).get("validation_gates", [])
        passed_gates = target_process.get("passed_validation_gates", [])

        # Only check for missing gates if both required and passed gates are defined
        if required_gates and passed_gates:
            missing_gates = [gate for gate in required_gates if gate not in passed_gates]
            if missing_gates:
                issues.extend([f"Missing required validation gate: {gate}" for gate in missing_gates])
        # If no required gates or no passed gates, consider it as passing during system initialization

        # Determine status based on issues found
        if issues:
            status = GateStatus.FAIL
            message = f"Methodology adherence validation failed with {len(issues)} issue(s)"
        else:
            status = GateStatus.PASS
            message = "Methodology adherence validation passed"

        result = ValidationResult(
            gate=self.validation_gates._rules.get("methodology_adherence_check").gate
            if self.validation_gates._rules.get("methodology_adherence_check")
            else self.validation_gates._validate_methodology_adherence.__code__.co_name,
            status=status,
            message=message,
            timestamp=datetime.now(),
            metadata={"validation_type": "methodology_adherence", "issues_count": len(issues)},
            errors=issues
        )

        # Store validation result in memory
        self._store_validation_result(result, target_process)

        return result
    
    def validate_cognitive_patterns(self, target_cognition: Dict[str, Any]) -> ValidationResult:
        """Validate cognitive patterns against expected models"""
        issues = []
        
        # Check for pattern matching
        patterns_to_match = target_cognition.get("expected_patterns", [])
        actual_patterns = target_cognition.get("observed_patterns", [])
        
        for pattern in patterns_to_match:
            if pattern not in actual_patterns:
                issues.append(f"Expected cognitive pattern not found: {pattern}")
        
        # Check for pattern consistency over time
        if "pattern_sequence" in target_cognition:
            sequence = target_cognition["pattern_sequence"]
            if not self._validate_pattern_sequence(sequence):
                issues.append("Cognitive pattern sequence is inconsistent")
        
        # Determine status based on issues found
        if issues:
            status = GateStatus.FAIL
            message = f"Cognitive pattern validation failed with {len(issues)} issue(s)"
        else:
            status = GateStatus.PASS
            message = "Cognitive pattern validation passed"
        
        result = ValidationResult(
            gate=self.validation_gates._rules.get("behavior_consistency_check").gate
            if self.validation_gates._rules.get("behavior_consistency_check")
            else self.validation_gates._validate_behavioral_consistency.__code__.co_name,
            status=status,
            message=message,
            timestamp=datetime.now(),
            metadata={"validation_type": "cognitive_patterns", "issues_count": len(issues)},
            errors=issues
        )
        
        # Store validation result in memory
        self._store_validation_result(result, target_cognition)
        
        return result
    
    def _validate_pattern_sequence(self, sequence: List[str]) -> bool:
        """Validate that a pattern sequence is consistent"""
        # This is a simplified check - in a real system, this would use more sophisticated sequence analysis
        if len(sequence) < 2:
            return True  # Can't validate sequence with less than 2 items
        
        # Example: Check if certain patterns typically occur together
        # This would be expanded with actual domain knowledge in a real system
        return True
    
    def detect_cognitive_drift(self, current_behavior: Dict[str, Any], 
                              baseline_behavior: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Detect cognitive drift from baseline behavior"""
        drifts_detected = []
        
        if baseline_behavior is None:
            # If no baseline provided, use historical data or fail gracefully
            baseline_behavior = self._get_historical_baseline()
        
        if not baseline_behavior:
            self.logger.warning("No baseline behavior available for drift detection")
            return drifts_detected
        
        # Compare current behavior with baseline
        drifts = self._compare_behaviors(current_behavior, baseline_behavior)
        
        for drift_type, details in drifts.items():
            if details["detected"]:
                drift_record = {
                    "drift_type": drift_type,
                    "severity": details.get("severity", "medium"),
                    "details": details,
                    "timestamp": datetime.now().isoformat(),
                    "drift_id": f"drift_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.detected_drifts)}"
                }
                
                drifts_detected.append(drift_record)
                self.detected_drifts.append(drift_record)
                
                # Store drift in memory
                drift_entry = MemoryEntry(
                    id=f"cognitive_drift_{drift_record['drift_id']}",
                    content=drift_record,
                    creation_time=datetime.now(),
                    memory_type=MemoryType.SHORT_TERM,
                    tags=["cognitive", "drift", drift_type],
                    priority=9,
                    ttl=timedelta(hours=24)  # Keep drift records for 24 hours
                )
                self.memory_manager.store(drift_entry)
        
        return drifts_detected
    
    def _compare_behaviors(self, current: Dict[str, Any], baseline: Dict[str, Any]) -> Dict[str, Any]:
        """Compare two behavior models to detect drift"""
        drifts = {}
        
        # Detect reasoning deviation
        current_reasoning = current.get("reasoning_steps", [])
        baseline_reasoning = baseline.get("reasoning_steps", [])
        
        reasoning_deviation = len(current_reasoning) != len(baseline_reasoning)
        if not reasoning_deviation:
            # Check if the types of reasoning steps match
            current_types = [step.get("type") for step in current_reasoning]
            baseline_types = [step.get("type") for step in baseline_reasoning]
            reasoning_deviation = current_types != baseline_types
        
        drifts[CognitiveDriftType.REASONING_DEVIATION.value] = {
            "detected": reasoning_deviation,
            "severity": "high" if reasoning_deviation else "none",
            "baseline_count": len(baseline_reasoning),
            "current_count": len(current_reasoning)
        }
        
        # Detect response inconsistency
        current_responses = current.get("responses", [])
        baseline_responses = baseline.get("responses", [])
        
        response_inconsistency = len(current_responses) != len(baseline_responses)
        if not response_inconsistency and current_responses and baseline_responses:
            # Check if responses have similar characteristics
            current_style = current_responses[0].get("style") if current_responses else None
            baseline_style = baseline_responses[0].get("style") if baseline_responses else None
            response_inconsistency = current_style != baseline_style
        
        drifts[CognitiveDriftType.RESPONSE_INCONSISTENCY.value] = {
            "detected": response_inconsistency,
            "severity": "medium" if response_inconsistency else "none",
            "baseline_count": len(baseline_responses),
            "current_count": len(current_responses)
        }
        
        # Detect methodology violation
        current_methodology = current.get("methodology_followed", [])
        baseline_methodology = baseline.get("methodology_followed", [])
        
        methodology_violation = set(baseline_methodology) - set(current_methodology)
        drifts[CognitiveDriftType.METHODOLOGY_VIOLATION.value] = {
            "detected": bool(methodology_violation),
            "severity": "high" if methodology_violation else "none",
            "violated_steps": list(methodology_violation) if methodology_violation else []
        }
        
        # For other drift types, add similar logic as needed
        
        return drifts
    
    def _get_historical_baseline(self) -> Optional[Dict[str, Any]]:
        """Get historical baseline behavior from memory"""
        # Look for recent behavioral records in memory
        behavioral_entries = self.memory_manager.search(
            tags=["behavioral", "pattern"], 
            memory_type=MemoryType.LONG_TERM
        )
        
        # Return the most recent behavioral pattern as baseline
        if behavioral_entries:
            # Sort by creation time, most recent first
            behavioral_entries.sort(key=lambda x: x.creation_time, reverse=True)
            return behavioral_entries[0].content
        
        return None
    
    def _store_validation_result(self, result: ValidationResult, target: Any):
        """Store validation result in memory"""
        result_entry = MemoryEntry(
            id=f"validation_result_{result.gate.value}_{datetime.now().isoformat()}",
            content={
                "result": {
                    "gate": result.gate.value,
                    "status": result.status.value,
                    "message": result.message,
                    "metadata": result.metadata,
                    "errors": result.errors
                },
                "target": str(target) if target else "N/A",
                "timestamp": result.timestamp.isoformat()
            },
            creation_time=result.timestamp,
            memory_type=MemoryType.SHORT_TERM,
            tags=["cognitive_validation", "result", result.gate.value],
            ttl=self.config.timeout_seconds * 5  # Keep results for 5x timeout duration
        )
        self.memory_manager.store(result_entry)
    
    def run_comprehensive_validation(self, target: Dict[str, Any]) -> Dict[str, Any]:
        """Run all cognitive validations on a target"""
        validation_results = {
            "behavioral_consistency": self.validate_behavioral_consistency(target),
            "methodology_adherence": self.validate_methodology_adherence(target),
            "cognitive_patterns": self.validate_cognitive_patterns(target)
        }
        
        # Detect cognitive drifts
        drifts = self.detect_cognitive_drift(target)
        
        comprehensive_result = {
            "validation_results": {
                k: {
                    "status": v.status.value,
                    "message": v.message,
                    "metadata": v.metadata
                } for k, v in validation_results.items()
            },
            "detected_drifts": drifts,
            "overall_status": self._determine_overall_status(list(validation_results.values())),
            "timestamp": datetime.now().isoformat()
        }
        
        # Store comprehensive result in memory
        comprehensive_entry = MemoryEntry(
            id=f"comprehensive_cognitive_validation_{datetime.now().isoformat()}",
            content=comprehensive_result,
            creation_time=datetime.now(),
            memory_type=MemoryType.SHORT_TERM,
            tags=["cognitive_validation", "comprehensive"],
            ttl=self.config.timeout_seconds * 10  # Keep comprehensive results longer
        )
        self.memory_manager.store(comprehensive_entry)
        
        return comprehensive_result
    
    def _determine_overall_status(self, validation_results: List[ValidationResult]) -> str:
        """Determine overall status based on multiple validation results"""
        statuses = [result.status for result in validation_results]
        
        if GateStatus.FAIL in statuses:
            return "fail"
        elif GateStatus.PENDING in statuses:
            return "pending"
        else:
            return "pass"
    
    def get_cognitive_report(self) -> Dict[str, Any]:
        """Generate a comprehensive cognitive validation report"""
        report = {
            "summary": {
                "tracked_patterns": len(self.tracked_patterns),
                "detected_drifts": len(self.detected_drifts),
                "drift_history_count": len(self.drift_history),
                "timestamp": datetime.now().isoformat()
            },
            "drifts": {
                "current": self.detected_drifts,
                "history": self.drift_history[-20:]  # Last 20 drifts from history
            },
            "validation_stats": self.validation_gates.get_validation_stats() if self.validation_gates else {}
        }
        
        return report