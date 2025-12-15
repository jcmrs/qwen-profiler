# API Reference for Qwen Profiler

## Core Components API

### ConfigManager

The `ConfigManager` handles system configuration loading, validation, and management.

#### Class: ConfigManager
- **Purpose**: Load, validate, and manage application configuration
- **Location**: `src.core.config.ConfigManager`

##### Methods:
- `__init__(config_path: Optional[str] = None)` - Initialize with optional config path
- `get_config() -> AppConfig` - Get the loaded configuration object
- `reload_config()` - Reload configuration from file

##### Usage:
```python
from src.core.config import ConfigManager

config_manager = ConfigManager()
config = config_manager.get_config()
print(f"Environment: {config.environment}")
```

---

### MemoryManager

The `MemoryManager` handles both short-term and long-term memory operations in the system.

#### Class: MemoryManager
- **Purpose**: Manage memory systems for short-term and long-term storage
- **Location**: `src.core.memory.manager.MemoryManager`

##### Methods:
- `__init__()` - Initialize memory stores
- `store(entry: MemoryEntry) -> bool` - Store a memory entry
- `retrieve(entry_id: str, memory_type: Optional[MemoryType] = None) -> Optional[MemoryEntry]` - Retrieve a memory entry by ID
- `search(tags: Optional[List[str]] = None, memory_type: Optional[MemoryType] = None) -> List[MemoryEntry]` - Search for memory entries by tags and/or type
- `update(entry_id: str, content: Any, tags: Optional[List[str]] = None) -> bool` - Update an existing memory entry
- `delete(entry_id: str, memory_type: Optional[MemoryType] = None) -> bool` - Delete a memory entry
- `cleanup_expired()` - Clean up expired entries from memory
- `get_statistics() -> Dict[str, Any]` - Get memory usage statistics
- `clear_memory(memory_type: Optional[MemoryType] = None)` - Clear entries from specified memory type

##### Usage:
```python
from src.core.memory.manager import MemoryManager, MemoryEntry, MemoryType
from datetime import datetime

memory_manager = MemoryManager()

# Create a memory entry
entry = MemoryEntry(
    id="example_entry",
    content={"key": "value"},
    creation_time=datetime.now(),
    memory_type=MemoryType.LONG_TERM,
    tags=["example", "test"]
)

# Store the entry
success = memory_manager.store(entry)

# Retrieve the entry
retrieved = memory_manager.retrieve("example_entry")
```

---

### ValidationGates

The `ValidationGates` manages validation protocols and quality assurance mechanisms.

#### Class: ValidationGates
- **Purpose**: Implement the validation gates system for quality assurance
- **Location**: `src.core.validation_gates.manager.ValidationGates`

##### Methods:
- `__init__(memory_manager: Optional[MemoryManager] = None)` - Initialize with optional memory manager
- `add_rule(rule: ValidationRule) -> bool` - Add a validation rule
- `remove_rule(rule_id: str) -> bool` - Remove a validation rule
- `validate_all(target: Any = None, context: Optional[Dict[str, Any]] = None) -> List[ValidationResult]` - Run all applicable validation rules
- `validate_rule(rule_id: str, target: Any = None, context: Optional[Dict[str, Any]] = None) -> Optional[ValidationResult]` - Run a specific validation rule
- `validate_gate(gate: ValidationGate, target: Any = None, context: Optional[Dict[str, Any]] = None) -> List[ValidationResult]` - Run all validation rules for a specific gate
- `get_validation_stats() -> Dict[str, Any]` - Get validation system statistics
- `get_recent_results(gate: Optional[ValidationGate] = None, limit: int = 10) -> List[ValidationResult]` - Get recent validation results
- `enable_gate(gate: ValidationGate)` - Enable all rules for a specific gate
- `disable_gate(gate: ValidationGate)` - Disable all rules for a specific gate

##### Usage:
```python
from src.core.validation_gates.manager import ValidationGates

validation_gates = ValidationGates()
results = validation_gates.validate_all(target="some_target_data")
```

---

### IntegrationLayer

The `IntegrationLayer` manages cross-pillar coordination and unified monitoring.

#### Class: IntegrationLayer
- **Purpose**: Handle cross-pillar coordination, unified monitoring, and integrated quality assurance
- **Location**: `src.integration_layer.manager.IntegrationLayer`

##### Methods:
- `__init__(**components)` - Initialize with all required pillar components
- `execute_integrated_profiling(target: Dict[str, Any]) -> Dict[str, Any]` - Execute profiling across all pillars
- `unified_monitoring() -> Dict[str, Any]` - Get unified monitoring report
- `get_integration_dashboard() -> Dict[str, Any]` - Get integration dashboard
- `_execute_technical_profiling(target: Dict[str, Any]) -> Dict[str, Any]` - Execute technical pillar profiling
- `_execute_behavioral_profiling(target: Dict[str, Any]) -> Dict[str, Any]` - Execute behavioral pillar profiling
- `_execute_semantic_profiling(target: Dict[str, Any]) -> Dict[str, Any]` - Execute semantic pillar profiling

##### Usage:
```python
from src.integration_layer.manager import IntegrationLayer

integration_layer = IntegrationLayer(
    # Initialize with all required components...
)

target = {
    "user_intent": "create conversational agents",
    "target_framework": "autogen",
    "expected_concept": "ConversableAgent"
}

results = integration_layer.execute_integrated_profiling(target)
```

---

## Pillar Components API

### DomainLinguist (Semantic Pillar)

The `DomainLinguist` handles semantic validation and translation between natural language user intent and domain-specific implementations.

#### Class: DomainLinguist
- **Purpose**: Perform semantic validation and translation between user intent and domain implementations
- **Location**: `src.semantic_pillar.domain_linguist.manager.DomainLinguist`

##### Methods:
- `__init__(memory_manager: MemoryManager, validation_gates: ValidationGates)` - Initialize with required managers
- `translate_user_intent(user_intent: str, target_framework: Union[str, DomainFramework]) -> SemanticValidationResult` - Translate user intent to technical concepts
- `build_semantic_bridge(user_intent: str, target_framework: Union[str, DomainFramework]) -> Dict[str, Any]` - Build semantic bridge between intent and implementation
- `validate_semantic_mapping(user_intent: str, expected_technical_concept: str) -> ValidationResult` - Validate semantic mapping accuracy
- `prevent_hallucination(input_text: str) -> SemanticValidationResult` - Prevent hallucinations with grounded validation
- `verify_ontological_correctness(target: Dict[str, Any]) -> ValidationResult` - Verify ontological correctness
- `get_semantic_report() -> Dict[str, Any]` - Get comprehensive semantic architecture report

##### Usage:
```python
from src.semantic_pillar.domain_linguist.manager import DomainLinguist

domain_linguist = DomainLinguist(memory_manager, validation_gates)

# Translate user intent
result = domain_linguist.translate_user_intent(
    "make agents talk to each other", 
    "autogen"
)
print(result.message)
```

---

### ValidationEngineer (Technical Pillar)

The `ValidationEngineer` handles systematic testing, configuration verification, and performance benchmarking.

#### Class: ValidationEngineer
- **Purpose**: Run systematic testing, configuration verification, and performance benchmarking
- **Location**: `src.technical_pillar.validation_engineer.manager.ValidationEngineer`

##### Methods:
- `__init__(memory_manager: MemoryManager, validation_gates: ValidationGates)` - Initialize with required managers
- `register_test(name: str, test_type: ValidationType, description: str = "", parameters: Dict[str, Any] = None) -> bool` - Register a new validation test
- `run_test(test_name: str, target: Any = None) -> Optional[ValidationResult]` - Run a specific validation test
- `run_all_tests(target: Any = None) -> List[ValidationResult]` - Run all enabled validation tests
- `get_test_report() -> Dict[str, Any]` - Generate validation test report
- `enable_test(name: str) -> bool` - Enable a validation test
- `disable_test(name: str) -> bool` - Disable a validation test

##### Usage:
```python
from src.technical_pillar.validation_engineer.manager import ValidationEngineer

validation_engineer = ValidationEngineer(memory_manager, validation_gates)

# Run all tests
results = validation_engineer.run_all_tests(target=config)
```

---

## Enums and Data Structures

### ValidationGate
The types of validation gates in the system:
- `TECHNICAL_VALIDATION`
- `BEHAVIORAL_INTEGRITY` 
- `SEMANTIC_ACCURACY`
- `INTEGRATION_COHERENCE`
- `PERFORMANCE_EFFICIENCY`
- `VISION_ALIGNMENT`

### MemoryType
The types of memory:
- `SHORT_TERM`
- `LONG_TERM`

### DomainFramework
Supported domain frameworks:
- `AUTOGEN`
- `LANGROID`
- `SEMANTIC_KERNEL`
- `CREWAI`
- `LANGGRAPH`