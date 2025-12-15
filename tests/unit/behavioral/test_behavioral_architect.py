"""
Unit tests for the BehavioralArchitect component
"""
import pytest
from src.behavioral_pillar.behavioral_architect.manager import BehavioralArchitect, BehavioralPattern
from src.core.memory.manager import MemoryManager
from src.core.validation_gates.manager import ValidationGates


class TestBehavioralArchitect:
    """Test suite for BehavioralArchitect functionality"""

    def setup_method(self):
        """Setup method that runs before each test"""
        memory_manager = MemoryManager()
        validation_gates = ValidationGates()
        self.behavioral_architect = BehavioralArchitect(
            memory_manager=memory_manager,
            validation_gates=validation_gates
        )

    def test_register_behavioral_pattern(self):
        """Test registering a new behavioral pattern"""
        from src.behavioral_pillar.behavioral_architect.manager import BehavioralPatternType

        success = self.behavioral_architect.register_pattern(
            name="test_pattern",
            pattern_type=BehavioralPatternType.RESPONSE_FORMATION,
            definition={
                "steps": ["step1", "step2", "step3"],
                "required_elements": ["validation1", "validation2"]
            },
            description="A test behavioral pattern"
        )

        # Verify the pattern was registered correctly
        assert success is True
        assert "test_pattern" in self.behavioral_architect.patterns

        # Verify the pattern was stored correctly
        stored_pattern = self.behavioral_architect.patterns["test_pattern"]
        assert stored_pattern.name == "test_pattern"
        assert stored_pattern.description == "A test behavioral pattern"
        assert stored_pattern.type == BehavioralPatternType.RESPONSE_FORMATION
        assert "step1" in stored_pattern.definition["steps"]

    def test_register_behavioral_pattern_with_correct_params(self):
        """Test registering a behavioral pattern with correct parameters"""
        from src.behavioral_pillar.behavioral_architect.manager import BehavioralPatternType

        success = self.behavioral_architect.register_pattern(
            name="test_registration",
            pattern_type=BehavioralPatternType.COGNITIVE_PROCESSING,
            definition={
                "steps": ["analyze", "design", "implement"],
                "required_checks": ["accuracy", "consistency"]
            },
            description="A test registration pattern"
        )

        assert success is True
        assert "test_registration" in self.behavioral_architect.patterns

        # Verify the pattern was stored correctly
        stored_pattern = self.behavioral_architect.patterns["test_registration"]
        assert stored_pattern.name == "test_registration"
        assert stored_pattern.description == "A test registration pattern"
        assert stored_pattern.type == BehavioralPatternType.COGNITIVE_PROCESSING

    def test_get_behavioral_pattern(self):
        """Test retrieving a behavioral pattern"""
        from src.behavioral_pillar.behavioral_architect.manager import BehavioralPatternType

        # First register a pattern
        self.behavioral_architect.register_pattern(
            name="retrieval_test",
            pattern_type=BehavioralPatternType.COGNITIVE_PROCESSING,
            definition={
                "steps": ["step_a", "step_b"],
                "required_checks": ["check_a", "check_b"]
            },
            description="A test retrieval pattern"
        )

        # Retrieve the pattern
        retrieved_pattern = self.behavioral_architect.get_pattern("retrieval_test")

        # Verify the pattern was retrieved correctly
        assert retrieved_pattern is not None
        assert isinstance(retrieved_pattern, BehavioralPattern)
        assert retrieved_pattern.name == "retrieval_test"
        assert retrieved_pattern.description == "A test retrieval pattern"

    def test_get_nonexistent_pattern(self):
        """Test retrieving a non-existent pattern"""
        retrieved_pattern = self.behavioral_architect.get_pattern("nonexistent_pattern")

        # Should return None for non-existent pattern
        assert retrieved_pattern is None

    def test_create_cognitive_architecture(self):
        """Test creating a cognitive architecture"""
        components = [
            {"name": "reasoning_component", "based_on_pattern": "cognitive_processing_flow"},
            {"name": "response_component", "based_on_pattern": "default_response_formation"}
        ]

        architecture = self.behavioral_architect.create_cognitive_architecture(
            name="test_architecture",
            components=components
        )

        # Verify the architecture was created correctly
        assert architecture is not None
        assert "name" in architecture
        assert "components" in architecture
        assert "patterns_used" in architecture
        assert "created_at" in architecture

        assert architecture["name"] == "test_architecture"
        assert len(architecture["components"]) == 2
        assert "cognitive_processing_flow" in architecture["patterns_used"]

    def test_generate_methodology(self):
        """Test generating a methodology by combining patterns"""
        methodology = self.behavioral_architect.generate_methodology(
            name="test_methodology",
            patterns_to_combine=["cognitive_processing_flow", "default_response_formation"]
        )

        # Verify the methodology was generated correctly
        assert methodology is not None
        assert "name" in methodology
        assert "patterns" in methodology
        assert "steps" in methodology
        assert "created_at" in methodology

        assert methodology["name"] == "test_methodology"
        assert len(methodology["patterns"]) >= 2  # Should have at least the 2 specified patterns

    def test_validate_behavioral_framework_pass(self):
        """Test validating a behavioral framework that should pass"""
        from src.behavioral_pillar.behavioral_architect.manager import BehavioralPatternType

        # Register a pattern to validate against
        self.behavioral_architect.register_pattern(
            name="processing_test_pattern",
            pattern_type=BehavioralPatternType.COGNITIVE_PROCESSING,
            definition={
                "steps": ["perceive", "interpret", "reason", "decide", "act"],
                "validation_points": ["input_quality", "assumption_check", "consistency_check"]
            },
            description="A pattern for processing testing"
        )

        # Test compliance with matching behavior
        compliant_behavior = {
            "processing_steps": ["perceive", "interpret", "reason", "decide", "act"],
            "response_elements": []  # This won't affect cognitive processing validation
        }

        result = self.behavioral_architect.validate_behavioral_framework(compliant_behavior)

        # Verify result structure
        assert result is not None
        assert "validation_results" in result

        # The result should have validation results
        assert isinstance(result["validation_results"], list)

    def test_validate_non_compliant_behavior(self):
        """Test validating non-compliant behavior"""
        from src.behavioral_pillar.behavioral_architect.manager import BehavioralPatternType

        # First register a pattern to validate against
        self.behavioral_architect.register_pattern(
            name="strict_pattern",
            pattern_type=BehavioralPatternType.COGNITIVE_PROCESSING,
            definition={
                "steps": ["step1", "step2", "step3"],
                "required_checks": ["validation_a", "validation_b"]
            },
            description="A strict pattern for testing"
        )

        # Test compliance with missing steps
        non_compliant_behavior = {
            "processing_steps": ["step1", "step3"],  # Missing "step2"
            "performed_checks": ["validation_a"]  # Missing "validation_b"
        }

        result = self.behavioral_architect.validate_behavioral_framework(non_compliant_behavior)

        # Verify result structure
        assert result is not None
        assert "validation_results" in result

        # The result should have validation results
        assert isinstance(result["validation_results"], list)

    def test_get_behavioral_report(self):
        """Test getting a comprehensive behavioral report"""
        report = self.behavioral_architect.get_behavioral_report()

        # Verify structure of the report
        assert isinstance(report, dict)
        assert "summary" in report
        assert "patterns" in report

        summary = report["summary"]
        assert "total_patterns" in summary
        assert "by_type" in summary
        assert "enabled_patterns" in summary
        assert "timestamp" in summary