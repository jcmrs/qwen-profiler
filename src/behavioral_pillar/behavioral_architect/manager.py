"""
Behavioral Architect Manager for the Qwen Profiler
Handles cognitive framework design, response methodology design, and behavioral pattern creation
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
from enum import Enum

from ...core.config import get_config
from ...core.memory.manager import MemoryManager, MemoryEntry, MemoryType
from ...core.validation_gates.manager import ValidationGates


class BehavioralPatternType(Enum):
    """Types of behavioral patterns"""
    RESPONSE_FORMATION = "response_formation"
    COGNITIVE_PROCESSING = "cognitive_processing"
    METHODOLOGY_ADHERENCE = "methodology_adherence"
    CONSISTENCY_PATTERNS = "consistency_patterns"


class BehavioralPattern:
    """Represents a behavioral pattern"""
    def __init__(self, name: str, pattern_type: BehavioralPatternType, 
                 definition: Dict[str, Any], description: str = ""):
        self.name = name
        self.type = pattern_type
        self.definition = definition  # Contains the actual pattern logic/structure
        self.description = description
        self.created_at = datetime.now()
        self.last_modified = datetime.now()
        self.enabled = True
        self.version = "1.0"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "name": self.name,
            "type": self.type.value,
            "definition": self.definition,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "last_modified": self.last_modified.isoformat(),
            "enabled": self.enabled,
            "version": self.version
        }


class BehavioralArchitect:
    """Manages cognitive framework design, response methodology design, and behavioral pattern creation"""
    
    def __init__(self, memory_manager: Optional[MemoryManager] = None, 
                 validation_gates: Optional[ValidationGates] = None):
        self.config = get_config()
        self.memory_manager = memory_manager or MemoryManager()
        self.validation_gates = validation_gates or ValidationGates()
        self.logger = logging.getLogger(__name__)
        
        # Behavioral patterns registry
        self.patterns: Dict[str, BehavioralPattern] = {}
        
        # Initialize with basic system patterns
        self._init_system_patterns()
    
    def _init_system_patterns(self):
        """Initialize with basic behavioral patterns"""
        system_patterns = [
            BehavioralPattern(
                name="default_response_formation",
                pattern_type=BehavioralPatternType.RESPONSE_FORMATION,
                definition={
                    "structure": ["context", "analysis", "response"],
                    "required_elements": ["acknowledgment", "solution", "follow_up"],
                    "tone": "professional",
                    "length": "concise"
                },
                description="Default pattern for forming responses"
            ),
            BehavioralPattern(
                name="cognitive_processing_flow",
                pattern_type=BehavioralPatternType.COGNITIVE_PROCESSING,
                definition={
                    "steps": ["perceive", "interpret", "reason", "decide", "act"],
                    "validation_points": ["input_quality", "assumption_check", "consistency_check"],
                    "feedback_loops": ["confidence_verification", "error_correction"]
                },
                description="Standard cognitive processing flow"
            ),
            BehavioralPattern(
                name="methodology_checkpoints",
                pattern_type=BehavioralPatternType.METHODOLOGY_ADHERENCE,
                definition={
                    "required_checks": ["validation_gate", "memory_consistency", "role_activation"],
                    "compliance_indicators": ["protocol_followed", "standards_met", "requirements_satisfied"]
                },
                description="Methodology adherence checkpoints"
            )
        ]
        
        for pattern in system_patterns:
            self.patterns[pattern.name] = pattern
    
    def register_pattern(self, name: str, pattern_type: BehavioralPatternType,
                        definition: Dict[str, Any], description: str = "") -> bool:
        """Register a new behavioral pattern"""
        if name in self.patterns:
            self.logger.warning(f"Pattern {name} already exists")
            return False
        
        pattern = BehavioralPattern(name, pattern_type, definition, description)
        self.patterns[name] = pattern
        
        # Store in memory for tracking
        memory_entry = MemoryEntry(
            id=f"behavioral_pattern_{name}",
            content=pattern.to_dict(),
            creation_time=datetime.now(),
            memory_type=MemoryType.LONG_TERM,
            tags=["behavioral", "pattern", pattern_type.value],
            priority=8
        )
        self.memory_manager.store(memory_entry)
        
        self.logger.info(f"Registered behavioral pattern: {name}")
        return True
    
    def get_pattern(self, name: str) -> Optional[BehavioralPattern]:
        """Get a behavioral pattern by name"""
        return self.patterns.get(name)
    
    def update_pattern(self, name: str, definition: Optional[Dict[str, Any]] = None,
                      description: Optional[str] = None) -> bool:
        """Update an existing behavioral pattern"""
        if name not in self.patterns:
            return False
        
        pattern = self.patterns[name]
        
        if definition is not None:
            pattern.definition = definition
            pattern.last_modified = datetime.now()
        
        if description is not None:
            pattern.description = description
            pattern.last_modified = datetime.now()
        
        # Update memory entry
        memory_entry = self.memory_manager.retrieve(f"behavioral_pattern_{name}")
        if memory_entry:
            memory_entry.content = pattern.to_dict()
            self.memory_manager.store(memory_entry)
        
        return True
    
    def validate_behavioral_framework(self, target_behavior: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a behavioral framework against registered patterns"""
        validation_results = []
        
        # Check against all enabled patterns
        for pattern in self.patterns.values():
            if not pattern.enabled:
                continue
            
            # Perform validation based on pattern type
            result = self._validate_against_pattern(target_behavior, pattern)
            validation_results.append({
                "pattern_name": pattern.name,
                "pattern_type": pattern.type.value,
                "result": result
            })
        
        # Store validation results in memory
        validation_entry = MemoryEntry(
            id=f"behavioral_validation_{datetime.now().isoformat()}",
            content={
                "target_behavior": target_behavior,
                "validation_results": validation_results,
                "timestamp": datetime.now().isoformat()
            },
            creation_time=datetime.now(),
            memory_type=MemoryType.SHORT_TERM,
            tags=["behavioral", "validation"],
            ttl=self.config.timeout_seconds * 4
        )
        self.memory_manager.store(validation_entry)
        
        return {
            "validation_results": validation_results,
            "timestamp": datetime.now().isoformat()
        }
    
    def _validate_against_pattern(self, target: Dict[str, Any], 
                                 pattern: BehavioralPattern) -> Dict[str, Any]:
        """Validate a target against a specific pattern"""
        # This is a simplified validation - in a real system, this would be more complex
        result = {
            "pattern_name": pattern.name,
            "compliant": True,
            "issues": [],
            "details": {}
        }
        
        # Example validation logic based on pattern type
        if pattern.type == BehavioralPatternType.RESPONSE_FORMATION:
            required_elements = pattern.definition.get("required_elements", [])
            for element in required_elements:
                if element not in target.get("response_elements", []):
                    result["compliant"] = False
                    result["issues"].append(f"Missing required element: {element}")
        
        elif pattern.type == BehavioralPatternType.COGNITIVE_PROCESSING:
            required_steps = pattern.definition.get("steps", [])
            target_steps = target.get("processing_steps", [])
            
            missing_steps = [step for step in required_steps if step not in target_steps]
            if missing_steps:
                result["compliant"] = False
                result["issues"].extend([f"Missing processing step: {step}" for step in missing_steps])
        
        elif pattern.type == BehavioralPatternType.METHODOLOGY_ADHERENCE:
            required_checks = pattern.definition.get("required_checks", [])
            target_checks = target.get("performed_checks", [])
            
            missing_checks = [check for check in required_checks if check not in target_checks]
            if missing_checks:
                result["compliant"] = False
                result["issues"].extend([f"Missing methodology check: {check}" for check in missing_checks])
        
        return result
    
    def create_cognitive_architecture(self, name: str, components: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a cognitive architecture from behavioral patterns"""
        architecture = {
            "name": name,
            "components": components,
            "created_at": datetime.now().isoformat(),
            "patterns_used": [],
            "validation_status": "pending"
        }
        
        # Identify and incorporate relevant patterns
        for component in components:
            pattern_name = component.get("based_on_pattern")
            if pattern_name and pattern_name in self.patterns:
                pattern = self.patterns[pattern_name]
                architecture["patterns_used"].append(pattern_name)
        
        # Store architecture in memory
        architecture_entry = MemoryEntry(
            id=f"cognitive_architecture_{name}",
            content=architecture,
            creation_time=datetime.now(),
            memory_type=MemoryType.LONG_TERM,
            tags=["behavioral", "architecture", "cognitive"],
            priority=9
        )
        self.memory_manager.store(architecture_entry)
        
        return architecture
    
    def generate_methodology(self, name: str, patterns_to_combine: List[str]) -> Dict[str, Any]:
        """Generate a methodology by combining behavioral patterns"""
        methodology = {
            "name": name,
            "description": f"Methodology combining patterns: {', '.join(patterns_to_combine)}",
            "patterns": [],
            "steps": [],
            "validation_requirements": [],
            "created_at": datetime.now().isoformat()
        }
        
        # Combine relevant patterns
        for pattern_name in patterns_to_combine:
            if pattern_name in self.patterns:
                pattern = self.patterns[pattern_name]
                methodology["patterns"].append({
                    "name": pattern.name,
                    "type": pattern.type.value,
                    "definition": pattern.definition
                })
                
                # Extract steps from the pattern if applicable
                if "steps" in pattern.definition:
                    methodology["steps"].extend(pattern.definition["steps"])
                
                # Extract validation requirements
                if "required_checks" in pattern.definition:
                    methodology["validation_requirements"].extend(
                        pattern.definition["required_checks"]
                    )
        
        # Remove duplicates while maintaining order
        methodology["steps"] = list(dict.fromkeys(methodology["steps"]))
        methodology["validation_requirements"] = list(
            dict.fromkeys(methodology["validation_requirements"])
        )
        
        # Store methodology in memory
        methodology_entry = MemoryEntry(
            id=f"methodology_{name}",
            content=methodology,
            creation_time=datetime.now(),
            memory_type=MemoryType.LONG_TERM,
            tags=["behavioral", "methodology"],
            priority=8
        )
        self.memory_manager.store(methodology_entry)
        
        return methodology
    
    def get_behavioral_report(self) -> Dict[str, Any]:
        """Generate a comprehensive behavioral patterns report"""
        report = {
            "summary": {
                "total_patterns": len(self.patterns),
                "by_type": {
                    pattern_type.value: len([p for p in self.patterns.values() 
                                           if p.type == pattern_type])
                    for pattern_type in BehavioralPatternType
                },
                "enabled_patterns": len([p for p in self.patterns.values() if p.enabled]),
                "timestamp": datetime.now().isoformat()
            },
            "patterns": [pattern.to_dict() for pattern in self.patterns.values()]
        }
        
        return report
    
    def enable_pattern(self, name: str) -> bool:
        """Enable a behavioral pattern"""
        if name not in self.patterns:
            return False
        self.patterns[name].enabled = True
        # Update memory
        memory_entry = self.memory_manager.retrieve(f"behavioral_pattern_{name}")
        if memory_entry:
            memory_entry.content = self.patterns[name].to_dict()
            self.memory_manager.store(memory_entry)
        return True
    
    def disable_pattern(self, name: str) -> bool:
        """Disable a behavioral pattern"""
        if name not in self.patterns:
            return False
        self.patterns[name].enabled = False
        # Update memory
        memory_entry = self.memory_manager.retrieve(f"behavioral_pattern_{name}")
        if memory_entry:
            memory_entry.content = self.patterns[name].to_dict()
            self.memory_manager.store(memory_entry)
        return True