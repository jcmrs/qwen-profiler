"""
Minimal Viable Implementation for User Workflow Integration
This demonstrates how the three-pillar backroom integrates with the conversation flow
"""
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from src.core.config import get_config
from src.core.memory.manager import MemoryManager
from src.core.validation_gates.manager import ValidationGates
from src.integration_layer.manager import IntegrationLayer
from datetime import datetime


class ConversationDrivenProfiler:
    """
    A minimal implementation that demonstrates how the three-pillar system
    operates as a backroom during user conversations
    """
    
    def __init__(self):
        self.config = get_config()
        self.memory_manager = MemoryManager()
        self.validation_gates = ValidationGates(memory_manager=self.memory_manager)
        
        # Initialize the integration layer (which initializes all pillars)
        self.integration_layer = IntegrationLayer(
            memory_manager=self.memory_manager,
            validation_gates=self.validation_gates
        )
        
        print("Qwen Profiler backroom initialized and ready.")
        print("The three-pillar system (Technical, Behavioral, Semantic) is now operating as a backroom.")
        print("When you describe a project, the system will automatically engage all three pillars to analyze your requirements.")
    
    def analyze_project_request(self, user_input: str):
        """
        Analyze a user's project description using the three-pillar backroom
        """
        print(f"\nAnalyzing project request: '{user_input}'")
        
        # Create a target for the integrated profiling
        target = {
            "user_intent": user_input,
            "target_framework": "universal",  # Generic framework for initial analysis
            "expected_concept": "agent_configuration",
            "required_methodology": {
                "steps": ["analyze", "design", "validate"],
                "validation_gates": ["tech_implementation_check", "behavior_consistency_check", "semantic_accuracy_check"]
            }
        }
        
        # Execute integrated profiling using the three-pillar system
        results = self.integration_layer.execute_integrated_profiling(target)
        
        # Generate a summary of the analysis
        self._generate_analysis_summary(results, user_input)
        
        return results
    
    def _generate_analysis_summary(self, results: dict, original_request: str):
        """
        Generate a user-friendly summary of the three-pillar analysis
        """
        print(f"\n--- Analysis Summary for: '{original_request}' ---")
        
        # Technical pillar analysis
        tech_results = results.get("technical_pillar", {})
        print(f"\nTechnical Analysis:")
        if "validation_tests" in tech_results:
            passed_tests = [test for test in tech_results["validation_tests"] if test.get("status") == "pass"]
            failed_tests = [test for test in tech_results["validation_tests"] if test.get("status") == "fail"]
            print(f"  - Passed: {len(passed_tests)} tests")
            print(f"  - Failed: {len(failed_tests)} tests")
        
        # Behavioral pillar analysis  
        behav_results = results.get("behavioral_pillar", {})
        print(f"\nBehavioral Analysis:")
        if "behavioral_consistency" in behav_results:
            status = behav_results["behavioral_consistency"]["status"]
            print(f"  - Consistency: {status}")
        
        # Semantic pillar analysis
        sem_results = results.get("semantic_pillar", {})
        print(f"\nSemantic Analysis:")
        if "semantic_bridge" in sem_results:
            success = sem_results["semantic_bridge"]["overall_success"]
            translation = sem_results["semantic_bridge"]["translation_result"]["translated_intent"]
            print(f"  - Translation successful: {success}")
            print(f"  - Interpretation: {translation[:100]}...")
        
        # Integration score
        integration_score = results.get("integration_score", 0)
        print(f"\nOverall Integration Score: {integration_score:.2f}")
        print(f"--- End Analysis Summary ---\n")


def demo_conversation_flow():
    """
    Demonstrate the conversation-driven profiling workflow
    """
    print("=== Qwen Profiler: Conversation-Driven Analysis Demo ===\n")
    
    # Initialize the system
    profiler = ConversationDrivenProfiler()
    
    # Example user requests that would trigger the backroom analysis
    sample_requests = [
        "I need to set up a system where multiple AI agents can collaborate on research tasks",
        "Create an agent configuration for automating my software development workflow",
        "Design a multi-agent system that can handle customer service inquiries"
    ]
    
    for i, request in enumerate(sample_requests, 1):
        print(f"\n--- Sample Request {i} ---")
        results = profiler.analyze_project_request(request)
        
        # The system could then generate specific configurations based on the analysis
        print(f"Based on this analysis, the system could now generate specific agent configurations.")
        print(f"This is where the full configuration generation capabilities would be implemented.")
    
    print("\n=== Demo Complete ===")
    print("In a full implementation, this system would generate actual agent configuration files")
    print("based on the three-pillar analysis of user requirements.")


if __name__ == "__main__":
    demo_conversation_flow()