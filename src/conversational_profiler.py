"""
Conversation-Driven Profiler for the Qwen Profiler project
Operates as the primary interface that integrates the three-pillar system
during user conversations to automatically analyze requirements and generate configurations
"""
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import logging
from src.core.config import get_config
from src.core.memory.manager import MemoryManager, MemoryEntry, MemoryType
from src.core.validation_gates.manager import ValidationGates
from src.integration_layer.manager import IntegrationLayer
from src.semantic_pillar.domain_linguist.manager import DomainLinguist
from src.behavioral_pillar.cognitive_validator.manager import CognitiveValidator
from src.technical_pillar.sre_specialist.manager import SRESpecialist


class ConversationalProfiler:
    """
    A conversation-driven profiler that operates as the primary interface
    connecting user inputs to the three-pillar backroom system for analysis
    and configuration generation.
    """
    
    def __init__(self):
        self.config = get_config()
        self.logger = logging.getLogger(__name__)
        
        # Initialize core components
        self.memory_manager = MemoryManager()
        self.validation_gates = ValidationGates(
            memory_manager=self.memory_manager
        )
        
        # Initialize the integration layer (which initializes all pillars)
        self.integration_layer = IntegrationLayer(
            memory_manager=self.memory_manager,
            validation_gates=self.validation_gates
        )
        
        # Store reference to individual pillar components
        self.domain_linguist = self.integration_layer.domain_linguist
        self.cognitive_validator = self.integration_layer.cognitive_validator
        self.sre_specialist = self.integration_layer.sre_specialist
        
        self.logger.info("Conversational Profiler initialized with three-pillar backroom")
        self.logger.info("System ready to analyze user project requirements")

    def process_user_request(self, user_input: str, framework_hint: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a user's project request using the three-pillar backroom system
        """
        self.logger.info(f"Processing user request: {user_input[:50]}...")
        
        # Automatically engage the three-pillar analysis system
        analysis_results = self._analyze_project_requirements(user_input, framework_hint)
        
        # Generate appropriate configuration outputs based on analysis
        configuration_recommendations = self._generate_configurations_from_analysis(analysis_results)
        
        # Package results for user delivery
        response = {
            "original_request": user_input,
            "analysis": analysis_results,
            "recommendations": configuration_recommendations,
            "processing_timestamp": datetime.now().isoformat()
        }

        # Store interaction in memory for learning and reference
        self._store_interaction(user_input, response)

        return response

    def get_analysis_summary(self, analysis_results: Dict[str, Any]) -> str:
        """
        Generate a user-friendly summary of the three-pillar analysis
        """
        summary = []
        summary.append("## Project Analysis Summary")
        summary.append("")

        # Technical pillar analysis
        tech_results = analysis_results.get("technical_pillar", {})
        tech_validation_tests = tech_results.get("validation_tests", [])
        if tech_validation_tests:
            passed_tests = [t for t in tech_validation_tests if t.get("status") == "pass"]
            summary.append(f"### Technical Analysis")
            summary.append(f"- Validation tests: {len(passed_tests)}/{len(tech_validation_tests)} passed")
            if len(passed_tests) < len(tech_validation_tests):
                summary.append("- ⚠️ Some technical validations failed - specific remediation may be required")
            else:
                summary.append("- ✅ All technical validations passed")

        # Behavioral pillar analysis
        behav_results = analysis_results.get("behavioral_pillar", {})
        summary.append(f"### Behavioral Analysis")
        if behav_results.get("behavioral_consistency", {}).get("status") == "pass":
            summary.append("- ✅ Behavioral consistency maintained")
        else:
            summary.append("- ⚠️ Behavioral consistency concerns identified")

        if behav_results.get("methodology_adherence", {}).get("status") == "pass":
            summary.append("- ✅ Methodology adherence confirmed")
        else:
            summary.append("- ⚠️ Methodology adherence issues detected")

        # Semantic pillar analysis
        sem_results = analysis_results.get("semantic_pillar", {})
        summary.append(f"### Semantic Analysis")
        if sem_results.get("semantic_bridge", {}).get("overall_success", False):
            summary.append("- ✅ Semantic translation successful")
        else:
            summary.append("- ⚠️ Semantic translation issues detected")

        if sem_results.get("hallucination_prevention", {}).get("success", False):
            summary.append("- ✅ Hallucination prevention effective")
        else:
            summary.append("- ⚠️ Hallucination risks detected")

        # Integration score
        integration_score = analysis_results.get("integration_score", 0)
        summary.append(f"### Integration Score")
        summary.append(f"- Overall system coherence: {integration_score:.2f}/1.0")

        return "\n".join(summary)

    def _analyze_project_requirements(self, user_input: str, framework_hint: Optional[str] = None) -> Dict[str, Any]:
        """
        Engage the three-pillar backroom to analyze user project requirements
        """
        self.logger.debug("Engaging three-pillar backroom analysis")
        
        # Create target for integrated profiling
        target = {
            "user_intent": user_input,
            "target_framework": framework_hint or "universal",  # Default to universal if not specified
            "expected_concept": "agent_configuration",  # Default expectation
            "required_methodology": {
                "steps": ["analyze", "design", "validate", "recommend"],
                "validation_gates": ["tech_implementation_check", "behavior_consistency_check", "semantic_accuracy_check"]
            }
        }

        # Execute integrated profiling using the three-pillar system
        results = self.integration_layer.execute_integrated_profiling(target)
        
        self.logger.debug("Three-pillar analysis completed")
        
        return results

    def _generate_configurations_from_analysis(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate configuration recommendations based on the three-pillar analysis
        """
        self.logger.debug("Generating configuration recommendations from analysis")
        
        # This is where the system would translate analysis results into concrete configurations
        # Based on the semantic bridge, technical validation, and behavioral consistency
        
        recommendations = {
            "technical_recommendations": self._extract_technical_recommendations(analysis_results),
            "behavioral_recommendations": self._extract_behavioral_recommendations(analysis_results),
            "semantic_recommendations": self._extract_semantic_recommendations(analysis_results),
            "framework_specific_configurations": self._generate_framework_configurations(analysis_results),
            "generation_timestamp": datetime.now().isoformat()
        }
        
        # Generate specific configuration files based on analysis
        configurations = self._create_concrete_configurations(recommendations)
        recommendations["configurations"] = configurations
        
        return recommendations

    def _extract_technical_recommendations(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract technical recommendations from analysis"""
        tech_results = analysis_results.get("technical_pillar", {})
        
        recommendations = {
            "infrastructure_suggestions": tech_results.get("infrastructure", {}).get("components_by_type", {}),
            "validation_results_summary": self._summarize_validation_results(
                tech_results.get("validation_tests", [])
            ),
            "sre_considerations": tech_results.get("sre_metrics", {}).get("reliability_metrics", {}),
            "performance_recommendations": []
        }
        
        # Add specific recommendations based on identified issues
        if tech_results.get("validation_tests"):
            failed_tests = [test for test in tech_results["validation_tests"] if test.get("status") == "fail"]
            if failed_tests:
                recommendations["performance_recommendations"].append(
                    f"Address {len(failed_tests)} technical validation failures identified in analysis"
                )
        
        return recommendations

    def _extract_behavioral_recommendations(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract behavioral recommendations from analysis"""
        behav_results = analysis_results.get("behavioral_pillar", {})
        
        recommendations = {
            "consistency_maintained": behav_results.get("behavioral_consistency", {}).get("status") == "pass",
            "methodology_adherence": behav_results.get("methodology_adherence", {}).get("status") == "pass",
            "cognitive_pattern_validation": behav_results.get("cognitive_patterns", {}).get("status") == "pass",
            "response_quality_assessment": behav_results.get("response_coordination", {}).get("quality_assessment", {})
        }
        
        return recommendations

    def _extract_semantic_recommendations(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract semantic recommendations from analysis"""
        sem_results = analysis_results.get("semantic_pillar", {})
        
        recommendations = {
            "semantic_bridge_quality": sem_results.get("semantic_bridge", {}).get("overall_success", False),
            "translation_confidence": sem_results.get("semantic_bridge", {}).get("translation_result", {}).get("confidence", 0),
            "mapping_validation_status": sem_results.get("mapping_validation", {}).get("status") == "pass",
            "hallucination_prevention_success": sem_results.get("hallucination_prevention", {}).get("success", False)
        }
        
        return recommendations

    def _generate_framework_configurations(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate framework-specific configuration based on analysis"""
        sem_results = analysis_results.get("semantic_pillar", {})
        user_intent = analysis_results.get("input", {}).get("user_intent", "unknown")
        
        # Extract the translated intent from semantic bridge
        translated_intent = sem_results.get("semantic_bridge", {}).get("translation_result", {}).get("translated_intent", "Unknown translation")
        
        # Determine which framework was identified
        target_framework = analysis_results.get("input", {}).get("target_framework", "universal")
        
        # Generate configuration based on framework
        framework_config = self._create_framework_specific_config(target_framework, user_intent, translated_intent)
        
        return {
            "target_framework": target_framework,
            "identified_requirements": translated_intent,
            "configuration_template": framework_config,
            "confidence_score": self._calculate_configuration_confidence(analysis_results)
        }

    def _create_framework_specific_config(self, framework: str, user_intent: str, translated_intent: str) -> str:
        """Create framework-specific configuration template"""
        # This would be expanded to generate actual configuration files for each framework
        templates = {
            "autogen": f"""# Autogen Configuration Template
# Based on user request: {user_intent}
# Translated to: {translated_intent}

from autogen import ConversableAgent, GroupChat, GroupChatManager

# Example configuration
user_proxy = ConversableAgent(
    name="user_proxy",
    llm_config=False,
    is_termination_msg=lambda msg: "TERMINATE" in msg.get("content", ""),
    human_input_mode="ALWAYS",
    max_consecutive_auto_reply=5,
)

# Additional agents would be configured based on detailed requirements
""",
            "crewai": f"""# CrewAI Configuration Template
# Based on user request: {user_intent}
# Translated to: {translated_intent}

from crewai import Agent, Task

# Example configuration
task = Task(
    description="{user_intent}",
    expected_output="Detailed implementation plan"
)

# Agents and tasks would be configured based on detailed requirements
""",
            "semantic_kernel": f"""# Semantic Kernel Configuration Template
# Based on user request: {user_intent}
# Translated to: {translated_intent}

import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion

# Example configuration
kernel = sk.Kernel()
kernel.add_chat_service("gpt", OpenAIChatCompletion(service_id="chat-gpt", ai_model_id="gpt-4"))

# Plugins and functions would be configured based on detailed requirements
""",
            "langgraph": f"""# LangGraph Configuration Template
# Based on user request: {user_intent}
# Translated to: {translated_intent}

from langgraph.graph import StateGraph

# Example configuration
# Graph structure would be configured based on detailed requirements
""",
            "langroid": f"""# Langroid Configuration Template
# Based on user request: {user_intent}
# Translated to: {translated_intent}

from langroid.agent.base_agent import BaseAgent
from langroid.my_agent import MyAgent

# Example configuration
# Agent interactions would be configured based on detailed requirements
""",
            "universal": f"""# Universal Configuration Template
# Based on user request: {user_intent}
# Translated to: {translated_intent}

# This is a conceptual template that would be refined based on 
# detailed requirements analysis from all three pillars
"""
        }
        
        return templates.get(framework.lower(), templates["universal"])

    def _create_concrete_configurations(self, recommendations: Dict[str, Any]) -> Dict[str, str]:
        """Create concrete configuration outputs ready for user implementation"""
        configurations = {}
        
        # Generate configuration files based on framework-specific recommendations
        framework_config = recommendations.get("framework_specific_configurations", {})
        if framework_config:
            target_framework = framework_config.get("target_framework", "universal")
            config_template = framework_config.get("configuration_template", "")
            
            configurations[target_framework] = config_template
        
        return configurations

    def _calculate_configuration_confidence(self, analysis_results: Dict[str, Any]) -> float:
        """Calculate overall confidence in the configuration based on all three pillars"""
        tech_score = analysis_results.get("technical_pillar", {}).get("validation_tests", [])
        behav_score = analysis_results.get("behavioral_pillar", {}).get("behavioral_consistency", {}).get("status") == "pass"
        sem_score = analysis_results.get("semantic_pillar", {}).get("semantic_bridge", {}).get("overall_success", False)
        
        # Convert to numeric scores
        valid_tech_tests = len([t for t in tech_score if t.get("status") == "pass"])
        total_tech_tests = len(tech_score) if tech_score else 1
        
        tech_confidence = valid_tech_tests / total_tech_tests if total_tech_tests > 0 else 0.5
        behav_confidence = 1.0 if behav_score else 0.3
        sem_confidence = 1.0 if sem_score else 0.4
        
        # Weighted average
        confidence = (tech_confidence * 0.4 + behav_confidence * 0.3 + sem_confidence * 0.3)
        
        return confidence

    def _summarize_validation_results(self, validation_tests: list) -> Dict[str, int]:
        """Summarize validation test results"""
        summary = {"pass": 0, "fail": 0, "skip": 0}
        
        for test in validation_tests:
            status = test.get("status", "unknown")
            if status in summary:
                summary[status] += 1
            else:
                summary["skip"] += 1  # Consider unknown as skip
        
        return summary
    
    def _store_interaction(self, user_input: str, response: Dict[str, Any]):
        """Store the user interaction in memory for future learning and reference"""
        interaction_entry = MemoryEntry(
            id=f"interaction_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            content={
                "user_input": user_input,
                "response": response,
                "timestamp": datetime.now().isoformat()
            },
            creation_time=datetime.now(),
            memory_type=MemoryType.SHORT_TERM,
            tags=["conversational_profiler", "interaction_log"],
            ttl=timedelta(hours=24)  # Keep for 24 hours
        )
        self.memory_manager.store(interaction_entry)

    def get_analysis_summary(self, analysis_results: Dict[str, Any]) -> str:
        """
        Generate a user-friendly summary of the three-pillar analysis
        """
        summary = []
        summary.append("## Project Analysis Summary")
        summary.append("")
        
        # Technical pillar summary
        tech_results = analysis_results.get("technical_pillar", {})
        tech_validation_tests = tech_results.get("validation_tests", [])
        if tech_validation_tests:
            passed_tests = [t for t in tech_validation_tests if t.get("status") == "pass"]
            summary.append(f"### Technical Analysis")
            summary.append(f"- Validation tests: {len(passed_tests)}/{len(tech_validation_tests)} passed")
            if len(passed_tests) < len(tech_validation_tests):
                summary.append("- ⚠️ Some technical validations failed - specific remediation may be required")
            else:
                summary.append("- ✅ All technical validations passed")
        
        # Behavioral pillar summary
        behav_results = analysis_results.get("behavioral_pillar", {})
        overall_success = analysis_results.get("cross_pillar_validation", {}).get("overall_success", False)
        summary.append(f"### Behavioral Analysis")
        if behav_results.get("behavioral_consistency", {}).get("status") == "pass":
            summary.append("- ✅ Behavioral consistency maintained")
        else:
            summary.append("- ⚠️ Behavioral consistency concerns identified")
        
        if behav_results.get("methodology_adherence", {}).get("status") == "pass":
            summary.append("- ✅ Methodology adherence confirmed")
        else:
            summary.append("- ⚠️ Methodology adherences issues detected")
        
        # Semantic pillar summary  
        sem_results = analysis_results.get("semantic_pillar", {})
        translation_success = sem_results.get("semantic_bridge", {}).get("overall_success", False)
        summary.append(f"### Semantic Analysis")
        if translation_success:
            summary.append("- ✅ Semantic translation successful")
        else:
            summary.append("- ⚠️ Semantic translation issues detected")
        
        if sem_results.get("hallucination_prevention", {}).get("success", False):
            summary.append("- ✅ Hallucination prevention effective")
        else:
            summary.append("- ⚠️ Hallucination risks detected")
        
        # Integration summary
        integration_score = analysis_results.get("integration_score", 0)
        summary.append(f"### Integration Score")
        summary.append(f"- Overall system coherence: {integration_score:.2f}/1.0")
        
        return "\n".join(summary)