"""
Validation gates for the Qwen Profiler
Implements validation protocols and quality assurance mechanisms
"""
import asyncio
import threading
from typing import Dict, List, Optional, Callable, Any, Set, Awaitable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging
import functools
from ..memory.manager import MemoryManager, MemoryEntry, MemoryType
from ..activation_system.manager import ActivationSystem, ActivationContext


class ValidationGate(Enum):
    """Types of validation gates in the system"""
    TECHNICAL_VALIDATION = "technical_validation"
    BEHAVIORAL_INTEGRITY = "behavioral_integrity"
    SEMANTIC_ACCURACY = "semantic_accuracy"
    INTEGRATION_COHERENCE = "integration_coherence"
    PERFORMANCE_EFFICIENCY = "performance_efficiency"
    VISION_ALIGNMENT = "vision_alignment"


class GateStatus(Enum):
    """Status of a validation gate"""
    PASS = "pass"
    FAIL = "fail"
    PENDING = "pending"
    SKIPPED = "skipped"


@dataclass
class ValidationResult:
    """Result of a validation operation"""
    gate: ValidationGate
    status: GateStatus
    message: str
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)


@dataclass
class ValidationRule:
    """A rule that defines what to validate"""
    id: str
    gate: ValidationGate
    description: str
    validator_func: Callable
    enabled: bool = True
    priority: int = 5  # 1-10 scale
    dependencies: List[str] = field(default_factory=list)
    timeout: timedelta = field(default_factory=lambda: timedelta(seconds=30))


class ValidationGates:
    """Implements the validation gates system for quality assurance"""
    
    def __init__(self, memory_manager: Optional[MemoryManager] = None, 
                 activation_system: Optional[ActivationSystem] = None):
        self._rules: Dict[str, ValidationRule] = {}
        self._results: List[ValidationResult] = []
        self._lock = threading.RLock()
        self._memory_manager = memory_manager or MemoryManager()
        self._activation_system = activation_system or ActivationSystem(self._memory_manager)
        self._init_default_rules()
        self._history_limit = 100  # Keep only last 100 results
    
    def _init_default_rules(self):
        """Initialize default validation rules"""
        # Technical validation rules
        self.add_rule(ValidationRule(
            id="tech_infrastructure_check",
            gate=ValidationGate.TECHNICAL_VALIDATION,
            description="Check technical infrastructure health",
            validator_func=self._validate_technical_infrastructure,
            priority=8
        ))
        
        self.add_rule(ValidationRule(
            id="tech_implementation_check",
            gate=ValidationGate.TECHNICAL_VALIDATION,
            description="Validate technical implementation",
            validator_func=self._validate_technical_implementation,
            priority=7
        ))
        
        # Behavioral integrity rules
        self.add_rule(ValidationRule(
            id="behavior_consistency_check",
            gate=ValidationGate.BEHAVIORAL_INTEGRITY,
            description="Check behavioral consistency",
            validator_func=self._validate_behavioral_consistency,
            priority=9
        ))
        
        self.add_rule(ValidationRule(
            id="methodology_adherence_check",
            gate=ValidationGate.BEHAVIORAL_INTEGRITY,
            description="Validate methodology adherence",
            validator_func=self._validate_methodology_adherence,
            priority=8
        ))
        
        # Semantic accuracy rules
        self.add_rule(ValidationRule(
            id="semantic_mapping_check",
            gate=ValidationGate.SEMANTIC_ACCURACY,
            description="Validate semantic mapping accuracy",
            validator_func=self._validate_semantic_mapping,
            priority=9
        ))
        
        self.add_rule(ValidationRule(
            id="ontological_verification",
            gate=ValidationGate.SEMANTIC_ACCURACY,
            description="Verify ontological correctness",
            validator_func=self._validate_ontological_correctness,
            priority=8
        ))
        
        # Integration coherence rules
        self.add_rule(ValidationRule(
            id="cross_pillar_integration_check",
            gate=ValidationGate.INTEGRATION_COHERENCE,
            description="Validate cross-pillar integration",
            validator_func=self._validate_cross_pillar_integration,
            priority=10
        ))
        
        # Performance efficiency rules
        self.add_rule(ValidationRule(
            id="performance_metrics_check",
            gate=ValidationGate.PERFORMANCE_EFFICIENCY,
            description="Validate performance metrics",
            validator_func=self._validate_performance_metrics,
            priority=7
        ))
        
        # Vision alignment rules
        self.add_rule(ValidationRule(
            id="vision_alignment_check",
            gate=ValidationGate.VISION_ALIGNMENT,
            description="Validate alignment with project vision",
            validator_func=self._validate_vision_alignment,
            priority=6
        ))
    
    def add_rule(self, rule: ValidationRule) -> bool:
        """Add a validation rule to the system"""
        with self._lock:
            if rule.id in self._rules:
                return False
            self._rules[rule.id] = rule
            return True
    
    def remove_rule(self, rule_id: str) -> bool:
        """Remove a validation rule from the system"""
        with self._lock:
            if rule_id not in self._rules:
                return False
            del self._rules[rule_id]
            return True
    
    def validate_all(self, target: Any = None, context: Optional[Dict[str, Any]] = None) -> List[ValidationResult]:
        """Run all applicable validation rules"""
        results = []
        
        # Sort rules by priority (highest first)
        sorted_rules = sorted(self._rules.values(), 
                             key=lambda r: r.priority, reverse=True)
        
        for rule in sorted_rules:
            if rule.enabled:
                result = self.validate_rule(rule.id, target, context)
                if result:
                    results.append(result)
        
        # Store results in memory
        self._store_results_in_memory(results)
        
        return results
    
    def validate_rule(self, rule_id: str, target: Any = None, 
                     context: Optional[Dict[str, Any]] = None) -> Optional[ValidationResult]:
        """Run a specific validation rule"""
        with self._lock:
            if rule_id not in self._rules:
                return None
            
            rule = self._rules[rule_id]
            if not rule.enabled:
                return None
            
            # Check dependencies
            for dep_id in rule.dependencies:
                if dep_id in self._rules and not self._rules[dep_id].enabled:
                    return ValidationResult(
                        gate=rule.gate,
                        status=GateStatus.SKIPPED,
                        message=f"Skipped due to disabled dependency: {dep_id}",
                        timestamp=datetime.now(),
                        metadata={"rule_id": rule_id, "dependency": dep_id}
                    )
            
            try:
                # Execute the validation function
                result = rule.validator_func(target, context, rule)
                
                # Validate the result format
                if isinstance(result, tuple) and len(result) >= 2:
                    status, message = result[0], result[1]
                    metadata = result[2] if len(result) > 2 else {}
                    errors = result[3] if len(result) > 3 else []
                else:
                    # Default to failure if unexpected result format
                    status, message = GateStatus.FAIL, f"Invalid result format from validator: {result}"
                    metadata, errors = {}, []
                
                validation_result = ValidationResult(
                    gate=rule.gate,
                    status=status,
                    message=message,
                    timestamp=datetime.now(),
                    metadata={**metadata, "rule_id": rule_id},
                    errors=errors
                )
                
                # Add to results history
                self._results.append(validation_result)
                if len(self._results) > self._history_limit:
                    self._results.pop(0)  # Remove oldest results
                
                return validation_result
                
            except Exception as e:
                logging.error(f"Validation rule {rule_id} failed with error: {e}")
                result = ValidationResult(
                    gate=rule.gate,
                    status=GateStatus.FAIL,
                    message=f"Validation rule failed with exception: {str(e)}",
                    timestamp=datetime.now(),
                    metadata={"rule_id": rule_id},
                    errors=[str(e)]
                )
                
                # Add to results history
                self._results.append(result)
                if len(self._results) > self._history_limit:
                    self._results.pop(0)
                
                return result
    
    def validate_gate(self, gate: ValidationGate, target: Any = None, 
                     context: Optional[Dict[str, Any]] = None) -> List[ValidationResult]:
        """Run all validation rules for a specific gate"""
        results = []
        
        for rule in self._rules.values():
            if rule.gate == gate and rule.enabled:
                result = self.validate_rule(rule.id, target, context)
                if result:
                    results.append(result)
        
        return results
    
    # Validation functions for different gates
    def _validate_technical_infrastructure(self, target: Any, context: Optional[Dict], rule: ValidationRule) -> tuple:
        """Validate the technical infrastructure"""
        # Check for required infrastructure components
        issues = []
        try:
            # Check if essential components are properly initialized
            if self._memory_manager is None:
                issues.append("Memory manager not initialized")

            # In a real system, this might check for service availability, resource usage, etc.
            # Here we'll check for basic system components that should be present
            if self._activation_system is None:
                issues.append("Activation system not initialized")

            # Check if there are any system-level errors in context
            if context and context.get("system_errors"):
                issues.extend(context["system_errors"])

            # Check for basic configuration
            from ..config import get_config
            try:
                config = get_config()
                if config is None:
                    issues.append("Configuration not loaded")
            except Exception as e:
                issues.append(f"Configuration error: {str(e)}")

            if not issues:
                return (GateStatus.PASS, "Technical infrastructure is healthy",
                       {"infrastructure_status": "healthy"}, [])
            else:
                return (GateStatus.FAIL, f"Technical infrastructure validation failed with {len(issues)} issue(s)",
                       {"infrastructure_status": "unhealthy", "issues": issues}, issues)
        except Exception as e:
            return (GateStatus.FAIL, f"Technical infrastructure validation failed: {str(e)}",
                   {}, [str(e)])
    
    def _validate_technical_implementation(self, target: Any, context: Optional[Dict], rule: ValidationRule) -> tuple:
        """Validate the technical implementation"""
        issues = []
        try:
            # Check if target is a valid implementation to validate
            if target is None:
                return (GateStatus.PASS, "No specific target to validate, implementation is valid in general", {}, [])

            # Check if target has the expected attributes for implementation validation
            if isinstance(target, dict):
                # Validate configuration-specific implementation details
                if "required_methodology" in target:
                    required_steps = target["required_methodology"].get("steps", [])
                    validation_gates = target["required_methodology"].get("validation_gates", [])

                    if not required_steps:
                        issues.append("No required methodology steps defined")
                    if not validation_gates:
                        issues.append("No required validation gates defined")

                # Check for proper validation gate compliance
                passed_gates = target.get("passed_validation_gates", [])
                required_gates = target.get("required_methodology", {}).get("validation_gates", [])

                for required_gate in required_gates:
                    if required_gate not in passed_gates:
                        issues.append(f"Missing required validation gate: {required_gate}")

            # Check for implementation consistency if applicable
            if hasattr(target, '__dict__') or isinstance(target, dict):
                # Check for required attributes that indicate proper implementation
                target_dict = target.__dict__ if hasattr(target, '__dict__') else target
                required_attrs = ['timestamp', 'validation_results']  # Example required attributes

                for attr in required_attrs:
                    if attr not in target_dict:
                        issues.append(f"Missing required attribute: {attr}")

            if not issues:
                return (GateStatus.PASS, "Technical implementation is valid",
                       {"implementation_status": "valid"}, [])
            else:
                return (GateStatus.FAIL, f"Technical implementation validation failed with {len(issues)} issue(s)",
                       {"implementation_status": "invalid", "issues": issues}, issues)
        except Exception as e:
            return (GateStatus.FAIL, f"Technical implementation validation failed: {str(e)}",
                   {}, [str(e)])
    
    def _validate_behavioral_consistency(self, target: Any, context: Optional[Dict], rule: ValidationRule) -> tuple:
        """Validate behavioral consistency"""
        issues = []
        try:
            # Validate behavioral consistency based on target content
            if target is None:
                return (GateStatus.PASS, "No target to validate for behavioral consistency", {}, [])

            # Check if target has behavioral attributes to validate
            if isinstance(target, dict):
                # Check for consistency in responses if they exist
                responses = target.get("responses", [])
                if responses and len(responses) > 1:
                    # Check for consistency across responses
                    first_response = responses[0]
                    for i, response in enumerate(responses[1:], 1):
                        if first_response.get("type") != response.get("type"):
                            issues.append(f"Inconsistent response type between response 0 and {i}")

                        if first_response.get("format") != response.get("format"):
                            issues.append(f"Inconsistent response format between response 0 and {i}")

                # Validate methodology adherence in the target
                required_steps = target.get("required_methodology", {}).get("steps", [])
                performed_steps = target.get("performed_steps", [])

                for step in required_steps:
                    if step not in performed_steps:
                        issues.append(f"Required methodology step '{step}' not performed")

                # Check for behavioral pattern compliance
                expected_patterns = target.get("expected_behavioral_patterns", [])
                observed_patterns = target.get("observed_patterns", [])

                for pattern in expected_patterns:
                    if pattern not in observed_patterns:
                        issues.append(f"Expected behavioral pattern '{pattern}' not observed")

            if not issues:
                return (GateStatus.PASS, "Behavioral consistency maintained",
                       {"consistency_status": "consistent"}, [])
            else:
                return (GateStatus.FAIL, f"Behavioral consistency validation failed with {len(issues)} issue(s)",
                       {"consistency_status": "inconsistent", "issues": issues}, issues)
        except Exception as e:
            return (GateStatus.FAIL, f"Behavioral consistency validation failed: {str(e)}",
                   {}, [str(e)])
    
    def _validate_methodology_adherence(self, target: Any, context: Optional[Dict], rule: ValidationRule) -> tuple:
        """Validate methodology adherence"""
        issues = []
        try:
            # Validate methodology adherence based on target content
            if target is None:
                return (GateStatus.PASS, "No target to validate for methodology adherence", {}, [])

            if isinstance(target, dict):
                # Check if required methodology steps were performed
                required_steps = target.get("required_methodology", {}).get("steps", [])
                performed_steps = target.get("performed_steps", [])

                # Only check for missing steps if both required and performed steps are defined
                if required_steps and performed_steps:
                    missing_steps = [step for step in required_steps if step not in performed_steps]
                    if missing_steps:
                        issues.extend([f"Missing required methodology step: {step}" for step in missing_steps])
                elif required_steps and not performed_steps:
                    # If required steps exist but no performed steps, that's an issue
                    issues.extend([f"Required methodology step not performed: {step}" for step in required_steps])

                # Check if required validation gates were passed
                required_gates = target.get("required_methodology", {}).get("validation_gates", [])
                passed_gates = target.get("passed_validation_gates", [])

                if required_gates and passed_gates:
                    missing_gates = [gate for gate in required_gates if gate not in passed_gates]
                    if missing_gates:
                        issues.extend([f"Missing required validation gate: {gate}" for gate in missing_gates])
                elif required_gates and not passed_gates:
                    # If required gates exist but no passed gates, that's an issue
                    issues.extend([f"Required validation gate not passed: {gate}" for gate in required_gates])

                # Validate methodology compliance score if available
                compliance_score = target.get("methodology_compliance_score")
                if compliance_score is not None and compliance_score < 0.7:  # 70% threshold
                    issues.append(f"Methodology compliance score too low: {compliance_score} (threshold: 0.7)")

            if not issues:
                return (GateStatus.PASS, "Methodology adherence confirmed",
                       {"methodology_status": "compliant"}, [])
            else:
                return (GateStatus.FAIL, f"Methodology adherence validation failed with {len(issues)} issue(s)",
                       {"methodology_status": "non_compliant", "issues": issues}, issues)
        except Exception as e:
            return (GateStatus.FAIL, f"Methodology adherence validation failed: {str(e)}",
                   {}, [str(e)])
    
    def _validate_semantic_mapping(self, target: Any, context: Optional[Dict], rule: ValidationRule) -> tuple:
        """Validate semantic mapping accuracy"""
        issues = []
        try:
            # Validate semantic mapping accuracy based on target content
            if target is None:
                return (GateStatus.PASS, "No target to validate for semantic mapping", {}, [])

            if isinstance(target, dict):
                # Check if user intent and expected concept are provided
                user_intent = target.get("user_intent", "")
                expected_concept = target.get("expected_concept", "")

                if not user_intent:
                    issues.append("Missing user intent to validate")

                if not expected_concept:
                    issues.append("Missing expected concept to validate against")

                # If we have both, check for potential mapping
                if user_intent and expected_concept:
                    # Simple text-based check for concept presence in intent or related context
                    user_intent_lower = user_intent.lower()
                    expected_concept_lower = expected_concept.lower()

                    # Check if expected concept or related terms appear in intent
                    if expected_concept_lower not in user_intent_lower:
                        # Check for related variations or synonyms (basic implementation)
                        related_terms = {
                            "ConversableAgent": ["agent", "convers", "chat", "talk", "communicat"],
                            "GroupChat": ["group", "chat", "convers", "team"],
                            "AssistantAgent": ["assistant", "help", "aid", "support"],
                            "UserProxyAgent": ["proxy", "user", "represent", "act"],
                            "llm_config": ["config", "model", "language", "llm", "setting"]
                        }

                        concept_found = False
                        if expected_concept in related_terms:
                            for term in related_terms[expected_concept]:
                                if term in user_intent_lower:
                                    concept_found = True
                                    break

                        if not concept_found:
                            issues.append(f"Expected concept '{expected_concept}' not found in user intent or related context")

            if not issues:
                return (GateStatus.PASS, "Semantic mapping is accurate",
                       {"mapping_status": "accurate"}, [])
            else:
                return (GateStatus.FAIL, f"Semantic mapping validation failed with {len(issues)} issue(s)",
                       {"mapping_status": "inaccurate", "issues": issues}, issues)
        except Exception as e:
            return (GateStatus.FAIL, f"Semantic mapping validation failed: {str(e)}",
                   {}, [str(e)])
    
    def _validate_ontological_correctness(self, target: Any, context: Optional[Dict], rule: ValidationRule) -> tuple:
        """Validate ontological correctness"""
        issues = []
        try:
            # Validate ontological correctness based on target content
            if target is None:
                return (GateStatus.PASS, "No target to validate for ontological correctness", {}, [])

            # In this context, we need to check if the target is properly structured according to known ontologies
            # This would typically connect to the DomainLinguist's knowledge graphs
            content_to_verify = target if isinstance(target, str) else str(target)

            # Check if we have access to the semantic pillar's knowledge
            # For this validation, we'll look for known framework concepts that should exist in knowledge graphs
            known_framework_concepts = [
                "ConversableAgent", "AssistantAgent", "UserProxyAgent", "GroupChat",
                "GroupChatManager", "llm_config", "crew", "agent", "task", "node",
                "graph", "state", "kernel", "plugin", "memory"
            ]

            content_lower = content_to_verify.lower()
            found_concepts = [concept for concept in known_framework_concepts
                            if concept.lower() in content_lower]

            if not found_concepts:
                # Check for common general terms that might indicate proper domain usage
                general_terms = ["agent", "chat", "config", "framework", "model", "ai", "conversation"]
                found_general = [term for term in general_terms if term in content_lower]

                if not found_general:
                    issues.append("No known domain concepts identified in target content")

            # Check if target has proper structure with required fields
            if isinstance(target, dict):
                # Check for required keys that indicate proper ontological structure
                required_keys = ["user_intent", "target_framework", "expected_concept"]
                missing_keys = [key for key in required_keys if key not in target]

                if missing_keys:
                    issues.extend([f"Missing required key for ontological validation: {key}" for key in missing_keys])

            if not issues:
                return (GateStatus.PASS, "Ontological correctness verified",
                       {"ontology_status": "valid"}, [])
            else:
                return (GateStatus.FAIL, f"Ontological correctness validation failed with {len(issues)} issue(s)",
                       {"ontology_status": "invalid", "issues": issues}, issues)
        except Exception as e:
            return (GateStatus.FAIL, f"Ontological correctness validation failed: {str(e)}",
                   {}, [str(e)])
    
    def _validate_cross_pillar_integration(self, target: Any, context: Optional[Dict], rule: ValidationRule) -> tuple:
        """Validate cross-pillar integration"""
        issues = []
        try:
            # Validate cross-pillar integration based on target content
            if target is None:
                return (GateStatus.PASS, "No target to validate for cross-pillar integration", {}, [])

            if isinstance(target, dict):
                # Check if target contains elements from multiple pillars
                has_technical = any(key in target for key in ["infrastructure", "validation_tests", "sre_metrics"])
                has_behavioral = any(key in target for key in ["behavioral_consistency", "methodology_adherence", "cognitive_patterns"])
                has_semantic = any(key in target for key in ["semantic_bridge", "mapping_validation", "hallucination_prevention"])

                # Check if all three pillars are represented
                pillars_present = sum([has_technical, has_behavioral, has_semantic])

                if pillars_present < 2:
                    issues.append(f"Cross-pillar integration requires at least 2 pillars, only {pillars_present} found")

                # Check for specific integration elements
                if "cross_pillar_validation" not in target:
                    issues.append("Missing cross-pillar validation element")

                if "integration_score" not in target:
                    issues.append("Missing integration score element")

                # Validate that integration elements are properly structured
                if "integration_score" in target:
                    score = target["integration_score"]
                    if not isinstance(score, (int, float)) or not (0 <= score <= 1):
                        issues.append(f"Integration score must be a number between 0 and 1, got: {score}")

            if not issues:
                return (GateStatus.PASS, "Cross-pillar integration is coherent",
                       {"integration_status": "coherent"}, [])
            else:
                return (GateStatus.FAIL, f"Cross-pillar integration validation failed with {len(issues)} issue(s)",
                       {"integration_status": "incoherent", "issues": issues}, issues)
        except Exception as e:
            return (GateStatus.FAIL, f"Cross-pillar integration validation failed: {str(e)}",
                   {}, [str(e)])
    
    def _validate_performance_metrics(self, target: Any, context: Optional[Dict], rule: ValidationRule) -> tuple:
        """Validate performance metrics"""
        issues = []
        try:
            # Validate performance metrics based on target content
            if target is None:
                return (GateStatus.PASS, "No target to validate for performance metrics", {}, [])

            if isinstance(target, dict):
                # Check for various performance-related metrics
                # Infrastructure performance
                sre_metrics = target.get("sre_metrics", {})
                reliability_metrics = sre_metrics.get("reliability_metrics", {})

                if reliability_metrics:
                    # Check uptime
                    uptime_str = reliability_metrics.get("uptime", "100%")
                    if isinstance(uptime_str, str) and "%" in uptime_str:
                        try:
                            uptime = float(uptime_str.replace("%", ""))
                            if uptime < 99.0:  # Less than 99% uptime
                                issues.append(f"Uptime {uptime_str} is below acceptable threshold (99%)")
                        except ValueError:
                            issues.append(f"Invalid uptime format: {uptime_str}")

                    # Check response time
                    avg_response_time = reliability_metrics.get("avg_response_time", "0ms")
                    if isinstance(avg_response_time, str):
                        try:
                            response_time = float(avg_response_time.replace("ms", ""))
                            if response_time > 500:  # More than 500ms response time
                                issues.append(f"Average response time {response_time}ms is above acceptable threshold (500ms)")
                        except ValueError:
                            issues.append(f"Invalid response time format: {avg_response_time}")

                    # Check error rate
                    error_rate_str = reliability_metrics.get("error_rate", "0%")
                    if isinstance(error_rate_str, str) and "%" in error_rate_str:
                        try:
                            error_rate = float(error_rate_str.replace("%", ""))
                            if error_rate > 1.0:  # More than 1% error rate
                                issues.append(f"Error rate {error_rate_str} is above acceptable threshold (1%)")
                        except ValueError:
                            issues.append(f"Invalid error rate format: {error_rate_str}")

                # Check for system resource metrics if available
                resource_metrics = target.get("resource_metrics", {})
                if resource_metrics:
                    cpu_usage = resource_metrics.get("cpu_usage")
                    if cpu_usage and cpu_usage > 80:  # More than 80% CPU usage
                        issues.append(f"CPU usage {cpu_usage}% is above acceptable threshold (80%)")

                    memory_usage = resource_metrics.get("memory_usage")
                    if memory_usage and memory_usage > 85:  # More than 85% memory usage
                        issues.append(f"Memory usage {memory_usage}% is above acceptable threshold (85%)")

            if not issues:
                return (GateStatus.PASS, "Performance metrics are within acceptable ranges",
                       {"performance_status": "acceptable"}, [])
            else:
                return (GateStatus.FAIL, f"Performance metrics validation failed with {len(issues)} issue(s)",
                       {"performance_status": "unacceptable", "issues": issues}, issues)
        except Exception as e:
            return (GateStatus.FAIL, f"Performance metrics validation failed: {str(e)}",
                   {}, [str(e)])
    
    def _validate_vision_alignment(self, target: Any, context: Optional[Dict], rule: ValidationRule) -> tuple:
        """Validate alignment with project vision"""
        issues = []
        try:
            # Validate alignment with project vision based on target content
            if target is None:
                return (GateStatus.PASS, "No target to validate for vision alignment", {}, [])

            # Check if the target aligns with the Qwen Profiler mission
            # The mission is to design a multi-pillar validation system for AI agent configurations
            # that combines rigorous technical architecture with systematic behavioral programming
            # and semantic architecture

            content_to_check = target if isinstance(target, str) else str(target)
            content_lower = content_to_check.lower()

            # Keywords associated with the project vision
            vision_keywords = [
                "validation", "ai agent", "configuration", "technical", "behavioral",
                "semantic", "multi-pillar", "architecture", "systematic", "framework",
                "reliability", "cognitive", "ontology", "knowledge graph", "agent configuration"
            ]

            # Check if target contains vision-related keywords
            vision_alignment = any(keyword in content_lower for keyword in vision_keywords)

            if not vision_alignment:
                issues.append("Target does not contain terms that align with project vision")

            # If target is a dict, check for specific structural alignment
            if isinstance(target, dict):
                # Check if target addresses at least one of the three pillars
                has_technical = any(key in target for key in ["infrastructure", "validation", "sre", "tech"])
                has_behavioral = any(key in target for key in ["behavior", "cognitive", "response", "pattern"])
                has_semantic = any(key in target for key in ["semantic", "ontology", "knowledge", "translation"])

                if not (has_technical or has_behavioral or has_semantic):
                    issues.append("Target does not address any of the three core pillars: technical, behavioral, or semantic")

            if not issues:
                return (GateStatus.PASS, "Vision alignment confirmed",
                       {"alignment_status": "aligned"}, [])
            else:
                return (GateStatus.FAIL, f"Vision alignment validation failed with {len(issues)} issue(s)",
                       {"alignment_status": "misaligned", "issues": issues}, issues)
        except Exception as e:
            return (GateStatus.FAIL, f"Vision alignment validation failed: {str(e)}",
                   {}, [str(e)])
    
    def _store_results_in_memory(self, results: List[ValidationResult]):
        """Store validation results in memory for tracking"""
        for result in results:
            memory_entry = MemoryEntry(
                id=f"validation_{result.gate.value}_{result.timestamp.isoformat()}",
                content={
                    "gate": result.gate.value,
                    "status": result.status.value,
                    "message": result.message,
                    "metadata": result.metadata,
                    "errors": result.errors
                },
                creation_time=result.timestamp,
                memory_type=MemoryType.SHORT_TERM,
                tags=["validation", result.gate.value, result.status.value],
                ttl=timedelta(hours=24)  # Keep validation results for 24 hours
            )
            self._memory_manager.store(memory_entry)
    
    def get_validation_stats(self) -> Dict[str, Any]:
        """Get validation system statistics"""
        with self._lock:
            if not self._results:
                return {
                    "total_validations": 0,
                    "pass_count": 0,
                    "fail_count": 0,
                    "pending_count": 0,
                    "skipped_count": 0,
                    "timestamp": datetime.now().isoformat()
                }
            
            stats = {
                "total_validations": len(self._results),
                "pass_count": len([r for r in self._results if r.status == GateStatus.PASS]),
                "fail_count": len([r for r in self._results if r.status == GateStatus.FAIL]),
                "pending_count": len([r for r in self._results if r.status == GateStatus.PENDING]),
                "skipped_count": len([r for r in self._results if r.status == GateStatus.SKIPPED]),
                "validation_counts_by_gate": {
                    gate.value: len([r for r in self._results if r.gate == gate])
                    for gate in ValidationGate
                },
                "latest_result_timestamp": max(r.timestamp for r in self._results).isoformat(),
                "timestamp": datetime.now().isoformat()
            }
            
            return stats
    
    def get_recent_results(self, gate: Optional[ValidationGate] = None, 
                          limit: int = 10) -> List[ValidationResult]:
        """Get recent validation results"""
        with self._lock:
            results = self._results[-limit:] if self._results else []
            
            if gate:
                results = [r for r in results if r.gate == gate]
            
            return results
    
    def enable_gate(self, gate: ValidationGate):
        """Enable all rules for a specific gate"""
        with self._lock:
            for rule in self._rules.values():
                if rule.gate == gate:
                    rule.enabled = True
    
    def disable_gate(self, gate: ValidationGate):
        """Disable all rules for a specific gate"""
        with self._lock:
            for rule in self._rules.values():
                if rule.gate == gate:
                    rule.enabled = False