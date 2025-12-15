"""
Unit tests for the DomainLinguist component
"""
import pytest
from src.semantic_pillar.domain_linguist.manager import DomainLinguist, DomainFramework
from src.core.memory.manager import MemoryManager
from src.core.validation_gates.manager import ValidationGates


class TestDomainLinguist:
    """Test suite for DomainLinguist functionality"""
    
    def setup_method(self):
        """Setup method that runs before each test"""
        memory_manager = MemoryManager()
        validation_gates = ValidationGates()
        self.domain_linguist = DomainLinguist(
            memory_manager=memory_manager,
            validation_gates=validation_gates
        )
    
    def test_translate_user_intent_with_string_framework(self):
        """Test translating user intent with framework as string"""
        user_intent = "make the agents talk to each other"
        target_framework = "autogen"
        
        result = self.domain_linguist.translate_user_intent(user_intent, target_framework)
        
        # Verify result structure
        assert hasattr(result, 'success')
        assert hasattr(result, 'message')
        assert hasattr(result, 'confidence')
        assert isinstance(result.success, bool)
        assert isinstance(result.message, str)
        assert isinstance(result.confidence, float)
    
    def test_translate_user_intent_with_enum_framework(self):
        """Test translating user intent with framework as enum"""
        user_intent = "create a conversational agent"
        target_framework = DomainFramework.AUTOGEN
        
        result = self.domain_linguist.translate_user_intent(user_intent, target_framework)
        
        # Verify result structure
        assert hasattr(result, 'success')
        assert hasattr(result, 'message')
        assert hasattr(result, 'confidence')
        assert isinstance(result.success, bool)
        assert isinstance(result.message, str)
        assert isinstance(result.confidence, float)
    
    def test_translate_user_intent_unknown_framework(self):
        """Test translating user intent with unknown framework"""
        user_intent = "do something with agents"
        target_framework = "unknown_framework"
        
        result = self.domain_linguist.translate_user_intent(user_intent, target_framework)
        
        # Should still return a valid result even with unknown framework
        assert hasattr(result, 'success')
        assert hasattr(result, 'message')
        assert hasattr(result, 'confidence')
    
    def test_build_semantic_bridge_with_string_framework(self):
        """Test building semantic bridge with framework as string"""
        user_intent = "connect two agents for conversation"
        target_framework = "autogen"
        
        bridge = self.domain_linguist.build_semantic_bridge(user_intent, target_framework)
        
        # Verify bridge structure
        assert isinstance(bridge, dict)
        assert "user_intent" in bridge
        assert "target_framework" in bridge
        assert "translation_result" in bridge
        assert "validation_result" in bridge
        assert "overall_success" in bridge
        
        # Verify values
        assert bridge["user_intent"] == user_intent
        assert bridge["target_framework"] == target_framework
    
    def test_build_semantic_bridge_with_enum_framework(self):
        """Test building semantic bridge with framework as enum"""
        user_intent = "set up agent communication"
        target_framework = DomainFramework.CREWAI
        
        bridge = self.domain_linguist.build_semantic_bridge(user_intent, target_framework)
        
        # Verify bridge structure
        assert isinstance(bridge, dict)
        assert "user_intent" in bridge
        assert "target_framework" in bridge
        assert "translation_result" in bridge
        assert "validation_result" in bridge
        assert "overall_success" in bridge
        
        # For enum, make sure target_framework value is used
        assert bridge["target_framework"] == target_framework.value
    
    def test_validate_semantic_mapping(self):
        """Test semantic mapping validation"""
        user_intent = "create a conversational agent"
        expected_concept = "ConversableAgent"  # This is a known concept in our knowledge graph
        
        result = self.domain_linguist.validate_semantic_mapping(user_intent, expected_concept)
        
        # Verify result structure
        assert hasattr(result, 'status')
        assert hasattr(result, 'message')
        assert hasattr(result, 'gate')
        
        # The status might be pass or fail depending on actual mapping
        assert result.status.value in ['pass', 'fail', 'pending', 'skipped']
        assert isinstance(result.message, str)
    
    def test_prevent_hallucination_low_risk(self):
        """Test hallucination prevention with low-risk input"""
        input_text = "Create a ConversableAgent for Autogen framework"
        
        result = self.domain_linguist.prevent_hallucination(input_text)
        
        # Verify result structure
        assert hasattr(result, 'success')
        assert hasattr(result, 'confidence')
        assert hasattr(result, 'message')
        
        # Result should be a SemanticValidationResult object
        assert hasattr(result, 'errors')  # Assuming it has errors attribute
        assert isinstance(result.success, bool)
        assert isinstance(result.confidence, float)
        assert isinstance(result.message, str)
    
    def test_prevent_hallucination_high_risk(self):
        """Test hallucination prevention with high-risk input"""
        input_text = "Make up some fictional agent concept that doesn't exist"
        
        result = self.domain_linguist.prevent_hallucination(input_text)
        
        # Verify result structure
        assert hasattr(result, 'success')
        assert hasattr(result, 'confidence')
        assert hasattr(result, 'message')
        
        # This might have lower confidence due to less known concepts
        assert isinstance(result.success, bool)
        assert isinstance(result.confidence, float)
        assert isinstance(result.message, str)
    
    def test_prevent_hallucination_empty_input(self):
        """Test hallucination prevention with empty input"""
        input_text = ""
        
        result = self.domain_linguist.prevent_hallucination(input_text)
        
        # Should handle empty input gracefully
        assert hasattr(result, 'success')
        assert hasattr(result, 'confidence')
        assert hasattr(result, 'message')
        assert result.confidence == 0.0  # No words to check = 0 confidence
    
    def test_verify_ontological_correctness(self):
        """Test ontological correctness verification"""
        target = {"input": "Create a ConversableAgent in Autogen"}
        
        result = self.domain_linguist.verify_ontological_correctness(target)
        
        # Verify result structure
        assert hasattr(result, 'status')
        assert hasattr(result, 'message')
        assert hasattr(result, 'gate')
        
        # Status should be one of the valid statuses
        assert result.status.value in ['pass', 'fail', 'pending', 'skipped']
    
    def test_get_semantic_report(self):
        """Test getting semantic architecture report"""
        report = self.domain_linguist.get_semantic_report()
        
        # Verify report structure
        assert isinstance(report, dict)
        assert "summary" in report
        assert "frameworks_supported" in report["summary"]
        assert "total_knowledge_graphs" in report["summary"]
        assert "total_mappings" in report["summary"]
        
        # Verify frameworks are as expected
        supported_frameworks = report["summary"]["frameworks_supported"]
        assert "autogen" in supported_frameworks
        assert "crewai" in supported_frameworks