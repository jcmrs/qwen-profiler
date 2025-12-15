"""
Script to test the DomainLinguist functionality after updates
"""
import sys
import os
# Add the project root to sys.path so we can import from src
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.semantic_pillar.domain_linguist.manager import DomainLinguist, DomainFramework
from src.core.memory.manager import MemoryManager
from src.core.validation_gates.manager import ValidationGates

def test_domain_linguist():
    """Test the DomainLinguist functionality"""
    # Initialize the DomainLinguist
    memory_manager = MemoryManager()
    validation_gates = ValidationGates()
    domain_linguist = DomainLinguist(
        memory_manager=memory_manager,
        validation_gates=validation_gates
    )

    # Generate a report to verify the knowledge was added
    report = domain_linguist.get_semantic_report()
    print(f"\nKnowledge graph report:")
    print(f"- Total knowledge graphs: {report['summary']['total_knowledge_graphs']}")
    print(f"- Total mappings: {report['summary']['total_mappings']}")
    print(f"- Knowledge graphs: {report['knowledge_graphs']}")

    # Test the semantic bridge with a common user intent
    print("\nTesting semantic bridge with 'make the agents talk to each other':")
    bridge = domain_linguist.build_semantic_bridge("make the agents talk to each other", DomainFramework.AUTOGEN)
    print(f"- Overall success: {bridge['overall_success']}")
    print(f"- Translation confidence: {bridge['translation_result']['confidence']}")
    print(f"- Validation status: {bridge['validation_result']['status']}")
    print(f"- Hallucination check: {bridge['hallucination_check']['result']}")

    # Test the semantic mapping validation
    print("\nTesting semantic mapping validation:")
    result = domain_linguist.validate_semantic_mapping("make the agents talk to each other", "ConversableAgent")
    print(f"- Validation status: {result.status.value}")
    print(f"- Validation message: {result.message}")

    # Test another example
    print("\nTesting with 'create a group chat':")
    bridge2 = domain_linguist.build_semantic_bridge("create a group chat", DomainFramework.AUTOGEN)
    print(f"- Overall success: {bridge2['overall_success']}")
    print(f"- Translation confidence: {bridge2['translation_result']['confidence']}")
    print(f"- Validation status: {bridge2['validation_result']['status']}")
    print(f"- Hallucination check: {bridge2['hallucination_check']['result']}")

    # Check if any Autogen concepts were found in the ontological verification
    print("\nTesting ontological verification with 'ConversableAgent':")
    verification_result = domain_linguist.verify_ontological_correctness({"input": "Create a ConversableAgent"})
    print(f"- Verification status: {verification_result.status.value}")
    print(f"- Verification message: {verification_result.message}")


def main():
    """Main function to test the DomainLinguist"""
    print("Testing DomainLinguist functionality after updates...")
    test_domain_linguist()


if __name__ == "__main__":
    main()