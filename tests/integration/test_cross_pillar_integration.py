"""
Integration tests for cross-pillar interactions
Tests the IntegrationLayer which connects all pillars together
"""
import pytest
from src.core.config import ConfigManager
from src.core.memory.manager import MemoryManager
from src.core.activation_system.manager import ActivationSystem
from src.core.validation_gates.manager import ValidationGates

# Technical pillar imports
from src.technical_pillar.infrastructure_architect.manager import InfrastructureArchitect
from src.technical_pillar.validation_engineer.manager import ValidationEngineer
from src.technical_pillar.sre_specialist.manager import SRESpecialist

# Behavioral pillar imports
from src.behavioral_pillar.behavioral_architect.manager import BehavioralArchitect
from src.behavioral_pillar.cognitive_validator.manager import CognitiveValidator
from src.behavioral_pillar.response_coordinator.manager import ResponseCoordinator

# Semantic pillar imports
from src.semantic_pillar.domain_linguist.manager import DomainLinguist

# Integration layer import
from src.integration_layer.manager import IntegrationLayer


class TestCrossPillarIntegration:
    """Test suite for cross-pillar integration functionality"""
    
    def setup_method(self):
        """Setup method that runs before each test"""
        # Initialize all core components
        self.config = ConfigManager().get_config()
        self.memory_manager = MemoryManager()
        self.validation_gates = ValidationGates(memory_manager=self.memory_manager)
        self.activation_system = ActivationSystem(memory_manager=self.memory_manager)
        
        # Initialize technical pillar components
        self.infrastructure_architect = InfrastructureArchitect(
            memory_manager=self.memory_manager,
            validation_gates=self.validation_gates
        )
        self.validation_engineer = ValidationEngineer(
            memory_manager=self.memory_manager,
            validation_gates=self.validation_gates
        )
        self.sre_specialist = SRESpecialist(
            memory_manager=self.memory_manager,
            validation_gates=self.validation_gates
        )
        
        # Initialize behavioral pillar components
        self.behavioral_architect = BehavioralArchitect(
            memory_manager=self.memory_manager,
            validation_gates=self.validation_gates
        )
        self.cognitive_validator = CognitiveValidator(
            memory_manager=self.memory_manager,
            validation_gates=self.validation_gates,
            behavioral_architect=self.behavioral_architect
        )
        self.response_coordinator = ResponseCoordinator(
            memory_manager=self.memory_manager,
            validation_gates=self.validation_gates,
            behavioral_architect=self.behavioral_architect,
            cognitive_validator=self.cognitive_validator
        )
        
        # Initialize semantic pillar components
        self.domain_linguist = DomainLinguist(
            memory_manager=self.memory_manager,
            validation_gates=self.validation_gates
        )
        
        # Initialize integration layer
        self.integration_layer = IntegrationLayer(
            memory_manager=self.memory_manager,
            activation_system=self.activation_system,
            validation_gates=self.validation_gates,
            infrastructure_architect=self.infrastructure_architect,
            validation_engineer=self.validation_engineer,
            sre_specialist=self.sre_specialist,
            behavioral_architect=self.behavioral_architect,
            cognitive_validator=self.cognitive_validator,
            response_coordinator=self.response_coordinator,
            domain_linguist=self.domain_linguist
        )
    
    def test_integration_layer_initialization(self):
        """Test that all components are properly connected in the IntegrationLayer"""
        # Verify that the integration layer was initialized with all required components
        assert self.integration_layer.memory_manager is not None
        assert self.integration_layer.activation_system is not None
        assert self.integration_layer.validation_gates is not None
        assert self.integration_layer.infrastructure_architect is not None
        assert self.integration_layer.validation_engineer is not None
        assert self.integration_layer.sre_specialist is not None
        assert self.integration_layer.behavioral_architect is not None
        assert self.integration_layer.cognitive_validator is not None
        assert self.integration_layer.response_coordinator is not None
        assert self.integration_layer.domain_linguist is not None
    
    def test_execute_integrated_profiling(self):
        """Test the integrated profiling of all pillars together"""
        target = {
            "user_intent": "make the agents talk to each other",
            "target_framework": "autogen",
            "expected_concept": "ConversableAgent",
            "required_methodology": {
                "steps": ["analyze", "design", "validate", "deploy"],
                "validation_gates": ["tech_implementation_check", "behavior_consistency_check"]
            }
        }
        
        # Execute integrated profiling
        results = self.integration_layer.execute_integrated_profiling(target)
        
        # Verify structure of results
        assert isinstance(results, dict)
        assert "technical_pillar" in results
        assert "behavioral_pillar" in results
        assert "semantic_pillar" in results
        assert "cross_pillar_validation" in results
        assert "integration_score" in results
        
        # Verify that each pillar produced results
        tech_results = results["technical_pillar"]
        behav_results = results["behavioral_pillar"]
        sem_results = results["semantic_pillar"]
        
        # Technical pillar should have validation tests
        assert "validation_tests" in tech_results
        
        # Behavioral pillar should have consistency and methodology checks
        assert "behavioral_consistency" in behav_results
        assert "methodology_adherence" in behav_results
        
        # Semantic pillar should have bridge and mapping validation
        assert "semantic_bridge" in sem_results
        assert "mapping_validation" in sem_results
    
    def test_unified_monitoring(self):
        """Test unified monitoring across all pillars"""
        # Run unified monitoring
        monitoring_report = self.integration_layer.unified_monitoring()

        # Verify structure of monitoring report
        assert isinstance(monitoring_report, dict)

        # Based on the actual structure returned by unified_monitoring(),
        # the report contains top-level entries for each pillar
        assert "technical_pillar" in monitoring_report
        assert "behavioral_pillar" in monitoring_report
        assert "semantic_pillar" in monitoring_report
        assert "integration_layer" in monitoring_report

        # Verify all pillars are represented with expected sub-sections
        technical_data = monitoring_report["technical_pillar"]
        assert "infrastructure_report" in technical_data
        assert "sre_dashboard" in technical_data
        assert "validation_stats" in technical_data

        behavioral_data = monitoring_report["behavioral_pillar"]
        assert "cognitive_report" in behavioral_data
        assert "patterns_report" in behavioral_data
        assert "coordination_report" in behavioral_data

        semantic_data = monitoring_report["semantic_pillar"]
        assert "semantic_report" in semantic_data
    
    def test_integration_dashboard(self):
        """Test the integration dashboard functionality"""
        # Get integration dashboard
        dashboard = self.integration_layer.get_integration_dashboard()
        
        # Verify structure of dashboard
        assert isinstance(dashboard, dict)
        assert "overview" in dashboard
        assert "pillar_health" in dashboard
        assert "integration_metrics" in dashboard
        
        # Verify overview section
        overview = dashboard["overview"]
        assert "total_integrated_events" in overview
        assert "last_integration_time" in overview
        assert "active_pillars" in overview
        
        # Verify pillar health section
        pillar_health = dashboard["pillar_health"]
        assert "technical" in pillar_health
        assert "behavioral" in pillar_health
        assert "semantic" in pillar_health
    
    def test_cross_pillar_validation(self):
        """Test cross-pillar validation functionality"""
        tech_results = {
            "validation_tests": [
                {"status": "pass", "gate": "technical_validation"},
                {"status": "pass", "gate": "security_check"}
            ]
        }
        behav_results = {
            "consistency_status": "pass",
            "methodology_adherence": "high"
        }
        sem_results = {
            "semantic_bridge": {"overall_success": True},
            "mapping_validation": {"status": "pass"}
        }
        
        # Perform cross-pillar validation
        validation_results = self.integration_layer._perform_cross_pillar_validation(
            tech_results, behav_results, sem_results
        )
        
        # Verify structure of validation results
        assert isinstance(validation_results, dict)
        assert "alignment_issues" in validation_results
        assert "technical_results_count" in validation_results
        assert "semantic_intents_count" in validation_results