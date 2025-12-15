"""
Unit tests for the ResponseCoordinator component
"""
import pytest
from src.behavioral_pillar.response_coordinator.manager import ResponseCoordinator
from src.core.memory.manager import MemoryManager
from src.core.validation_gates.manager import ValidationGates
from src.behavioral_pillar.behavioral_architect.manager import BehavioralArchitect
from src.behavioral_pillar.cognitive_validator.manager import CognitiveValidator


class TestResponseCoordinator:
    """Test suite for ResponseCoordinator functionality"""

    def setup_method(self):
        """Setup method that runs before each test"""
        memory_manager = MemoryManager()
        validation_gates = ValidationGates()
        behavioral_architect = BehavioralArchitect()
        cognitive_validator = CognitiveValidator(
            memory_manager=memory_manager,
            validation_gates=validation_gates,
            behavioral_architect=behavioral_architect
        )
        
        self.response_coordinator = ResponseCoordinator(
            memory_manager=memory_manager,
            validation_gates=validation_gates,
            behavioral_architect=behavioral_architect,
            cognitive_validator=cognitive_validator
        )

    def test_coordinate_response_basic(self):
        """Test basic response coordination"""
        request = {
            "user_intent": "Explain how agents communicate",
            "context": "Autogen framework",
            "required_accuracy": "high",
            "response_format": "structured"
        }

        coordinated_response = self.response_coordinator.coordinate_response(request)

        # Verify the response structure
        assert coordinated_response is not None
        assert isinstance(coordinated_response, dict)
        assert "protocol" in coordinated_response
        assert "execution_results" in coordinated_response
        assert "validation_results" in coordinated_response
        assert "quality_assessment" in coordinated_response
        assert "overall_success" in coordinated_response
        assert "timestamp" in coordinated_response

        # Quality assessment should contain relevant information
        quality_assessment = coordinated_response["quality_assessment"]
        assert "individual_scores" in quality_assessment
        assert "weighted_average" in quality_assessment
        assert "overall_quality" in quality_assessment

    def test_assess_response_quality(self):
        """Test response quality assessment"""
        response_content = {
            "content": "This is a test response about agent communication.",
            "format": "structured",
            "accuracy_level": "high"
        }

        quality_result = self.response_coordinator.assess_response_quality(response_content)

        # Verify result structure
        assert quality_result is not None
        assert "individual_scores" in quality_result
        assert "weighted_average" in quality_result
        assert "overall_quality" in quality_result
        assert "timestamp" in quality_result

        # Verify individual scores structure
        individual_scores = quality_result["individual_scores"]
        assert "accuracy" in individual_scores
        assert "clarity" in individual_scores
        assert "relevance" in individual_scores

    def test_apply_systematic_observation(self):
        """Test applying systematic observation to a target"""
        target = {
            "content": "This is a target that needs systematic observation.",
            "context": "quality_assessment"
        }

        observation_result = self.response_coordinator.apply_systematic_observation(target)

        # Verify that the observation has been applied
        assert observation_result is not None
        assert "template" in observation_result
        assert "observations" in observation_result
        assert "timestamp" in observation_result

    def test_assess_response_quality_detailed(self):
        """Test the complete response quality assessment"""
        request = {
            "content": "This is a sample response for quality testing.",
            "structured": True,
            "topic_aligned": True,
            "complete_coverage": True
        }

        quality_result = self.response_coordinator.assess_response_quality(request)

        # Verify structure of quality results
        assert quality_result is not None
        assert isinstance(quality_result, dict)
        assert "individual_scores" in quality_result
        assert "weighted_average" in quality_result
        assert "overall_quality" in quality_result
        assert "timestamp" in quality_result

        # Verify individual scores
        individual_scores = quality_result["individual_scores"]
        for criterion in ["accuracy", "clarity", "relevance", "completeness", "timeliness"]:
            assert criterion in individual_scores
            assert "score" in individual_scores[criterion]
            assert "weight" in individual_scores[criterion]
            assert "threshold" in individual_scores[criterion]
            assert "passed" in individual_scores[criterion]

    def test_register_custom_protocol(self):
        """Test registering a custom response protocol"""
        protocol_definition = {
            "name": "Custom Protocol",
            "description": "A custom response protocol for testing",
            "requirement_steps": [
                "validate_content_accuracy",
                "check_formatting_standards"
            ],
            "validation_gates": ["tech_implementation_check"],
            "quality_checkpoints": ["accuracy", "compliance"]
        }

        success = self.response_coordinator.register_custom_protocol("custom_test_protocol", protocol_definition)

        # Verify the protocol was registered
        assert success is True
        assert "custom_test_protocol" in self.response_coordinator.response_protocols

        # Check that the stored protocol matches the definition
        stored_protocol = self.response_coordinator.response_protocols["custom_test_protocol"]
        assert stored_protocol["name"] == "Custom Protocol"
        assert len(stored_protocol["requirement_steps"]) >= 2

    def test_coordinate_response_with_custom_protocol(self):
        """Test response coordination with a custom protocol"""
        # First register a custom protocol
        protocol_definition = {
            "name": "Test Protocol",
            "description": "A protocol for testing coordination",
            "requirement_steps": [
                "validate_content_accuracy",
                "check_formatting_standards",
                "verify_citation_requirements"
            ],
            "validation_gates": ["tech_implementation_check"],
            "quality_checkpoints": ["accuracy", "compliance"]
        }

        self.response_coordinator.register_custom_protocol("test_coordination_protocol", protocol_definition)

        # Now coordinate a response using the custom protocol
        request = {
            "user_intent": "How do Autogen agents coordinate?",
            "context": {
                "framework": "Autogen",
                "agents_involved": ["UserProxyAgent", "AssistantAgent"],
                "communication_method": "GroupChat"
            }
        }

        result = self.response_coordinator.coordinate_response(request, protocol_name="test_coordination_protocol")

        # Verify the result structure
        assert result is not None
        assert isinstance(result, dict)
        assert "protocol" in result
        assert "execution_results" in result
        assert "validation_results" in result
        assert "quality_assessment" in result
        assert "overall_success" in result

        # Check that the correct protocol was used
        assert result["protocol"] == "test_coordination_protocol"

        # Check execution results
        execution_results = result["execution_results"]
        assert len(execution_results) >= 3  # Should have at least the 3 steps defined in the protocol

    def test_get_response_coordination_report(self):
        """Test getting a coordination report"""
        report = self.response_coordinator.get_response_coordination_report()

        # Verify structure of the report
        assert isinstance(report, dict)
        assert "summary" in report
        assert "protocols" in report
        assert "quality_criteria" in report

        summary = report["summary"]
        assert "registered_protocols" in summary
        assert "quality_criteria_count" in summary
        assert "observation_templates_count" in summary
        assert "timestamp" in summary