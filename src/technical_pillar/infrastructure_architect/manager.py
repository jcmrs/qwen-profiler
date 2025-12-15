"""
Infrastructure Architect Manager for the Qwen Profiler
Handles technical infrastructure validation and design
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
import logging

from ...core.config import get_config
from ...core.memory.manager import MemoryManager, MemoryEntry, MemoryType
from ...core.validation_gates.manager import ValidationGates


class InfrastructureType(Enum):
    """Types of infrastructure in the system"""
    COMPUTE = "compute"
    STORAGE = "storage"
    NETWORK = "network"
    SECURITY = "security"
    MONITORING = "monitoring"


class InfrastructureComponent:
    """Represents an infrastructure component"""
    def __init__(self, name: str, component_type: InfrastructureType, 
                 properties: Dict[str, Any] = None):
        self.name = name
        self.type = component_type
        self.properties = properties or {}
        self.created_at = datetime.now()
        self.dependencies: List[str] = []
        self.status = "unknown"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "name": self.name,
            "type": self.type.value,
            "properties": self.properties,
            "created_at": self.created_at.isoformat(),
            "dependencies": self.dependencies,
            "status": self.status
        }


class InfrastructureArchitect:
    """Manages technical infrastructure validation and design"""
    
    def __init__(self, memory_manager: Optional[MemoryManager] = None, 
                 validation_gates: Optional[ValidationGates] = None):
        self.config = get_config()
        self.memory_manager = memory_manager or MemoryManager()
        self.validation_gates = validation_gates or ValidationGates()
        self.logger = logging.getLogger(__name__)
        
        # Infrastructure components registry
        self.components: Dict[str, InfrastructureComponent] = {}
        
        # Initialize with basic system components
        self._init_system_components()
    
    def _init_system_components(self):
        """Initialize with basic system infrastructure components"""
        system_components = [
            InfrastructureComponent("system_monitoring", InfrastructureType.MONITORING),
            InfrastructureComponent("config_store", InfrastructureType.STORAGE),
            InfrastructureComponent("logging_system", InfrastructureType.MONITORING),
        ]
        
        for component in system_components:
            self.components[component.name] = component
    
    def register_component(self, name: str, component_type: InfrastructureType, 
                          properties: Dict[str, Any] = None) -> bool:
        """Register a new infrastructure component"""
        if name in self.components:
            self.logger.warning(f"Component {name} already exists")
            return False
        
        component = InfrastructureComponent(name, component_type, properties or {})
        self.components[name] = component
        
        # Store in memory for tracking
        memory_entry = MemoryEntry(
            id=f"infra_component_{name}",
            content=component.to_dict(),
            creation_time=datetime.now(),
            memory_type=MemoryType.LONG_TERM,
            tags=["infrastructure", "component", component_type.value],
            priority=7
        )
        self.memory_manager.store(memory_entry)
        
        self.logger.info(f"Registered infrastructure component: {name}")
        return True
    
    def validate_infrastructure(self, target: Any = None) -> Dict[str, Any]:
        """Validate the technical infrastructure"""
        # Use validation gates to run infrastructure-specific validations
        validation_results = self.validation_gates.validate_gate(
            self.validation_gates._rules.get("tech_infrastructure_check"), 
            target=target
        )
        
        # Additional infrastructure-specific validation
        infra_status = {
            "components_count": len(self.components),
            "components_by_type": {
                infra_type.value: len([c for c in self.components.values() 
                                     if c.type == infra_type])
                for infra_type in InfrastructureType
            },
            "validation_results": [result.to_dict() if hasattr(result, 'to_dict') else 
                                 {"gate": r.gate.value, "status": r.status.value, 
                                  "message": r.message} for r in validation_results],
            "timestamp": datetime.now().isoformat()
        }
        
        # Store infrastructure status in memory
        memory_entry = MemoryEntry(
            id=f"infra_status_{datetime.now().isoformat()}",
            content=infra_status,
            creation_time=datetime.now(),
            memory_type=MemoryType.SHORT_TERM,
            tags=["infrastructure", "status"],
            ttl=self.config.timeout_seconds * 2  # Keep status for 2x timeout duration
        )
        self.memory_manager.store(memory_entry)
        
        return infra_status
    
    def check_component_dependencies(self, component_name: str) -> Dict[str, Any]:
        """Check dependencies for a specific component"""
        if component_name not in self.components:
            return {"error": f"Component {component_name} not found"}
        
        component = self.components[component_name]
        dependency_status = {
            "component": component_name,
            "dependencies": component.dependencies,
            "dependency_status": {},
            "timestamp": datetime.now().isoformat()
        }
        
        for dep_name in component.dependencies:
            if dep_name in self.components:
                dep_status = self.components[dep_name].status
                dependency_status["dependency_status"][dep_name] = dep_status
            else:
                dependency_status["dependency_status"][dep_name] = "missing"
        
        return dependency_status
    
    def update_component_status(self, name: str, status: str) -> bool:
        """Update the status of an infrastructure component"""
        if name not in self.components:
            return False
        
        self.components[name].status = status
        
        # Update memory entry as well
        memory_entry = self.memory_manager.retrieve(f"infra_component_{name}")
        if memory_entry:
            content = memory_entry.content
            content["status"] = status
            memory_entry.content = content
            self.memory_manager.store(memory_entry)
        
        return True
    
    def get_infrastructure_report(self) -> Dict[str, Any]:
        """Generate a comprehensive infrastructure report"""
        report = {
            "summary": {
                "total_components": len(self.components),
                "by_type": {
                    infra_type.value: len([c for c in self.components.values() 
                                         if c.type == infra_type])
                    for infra_type in InfrastructureType
                },
                "status_distribution": {},
                "timestamp": datetime.now().isoformat()
            },
            "components": [comp.to_dict() for comp in self.components.values()]
        }
        
        # Count status distribution
        status_counts = {}
        for comp in self.components.values():
            status = comp.status
            status_counts[status] = status_counts.get(status, 0) + 1
        report["summary"]["status_distribution"] = status_counts
        
        return report