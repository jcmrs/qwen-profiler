"""
Test script to verify that semantic mapping is not fixated on a single sentence
but can handle multiple different user intents.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.semantic_pillar.domain_linguist.manager import DomainLinguist, DomainFramework
from src.core.memory.manager import MemoryManager
from src.core.validation_gates.manager import ValidationGates


def test_multiple_semantic_mappings():
    """Test semantic mapping with multiple different user intents"""
    # Initialize the DomainLinguist
    memory_manager = MemoryManager()
    validation_gates = ValidationGates()
    domain_linguist = DomainLinguist(
        memory_manager=memory_manager,
        validation_gates=validation_gates
    )
    
    # Test cases with different user intents
    test_cases = [
        "make the agents talk to each other",  # Original failing case
        "connect two agents for conversation",  # From the tests
        "create a conversational agent",  # From the tests
        "establish communication between AI agents",  # New test case
        "set up agent communication",  # New test case
        "create a group chat",  # New test case
        "connect them together",  # From general mappings
        "work as a team",  # From general mappings
        "share information",  # From general mappings
    ]
    
    print("Testing multiple semantic mapping scenarios:")
    print("=" * 50)
    
    for i, user_intent in enumerate(test_cases, 1):
        print(f"\nTest {i}: '{user_intent}'")
        
        # Test semantic bridge
        bridge = domain_linguist.build_semantic_bridge(user_intent, DomainFramework.AUTOGEN)
        print(f"  - Bridge overall success: {bridge['overall_success']}")
        print(f"  - Translation confidence: {bridge['translation_result']['confidence']:.2f}")
        print(f"  - Validation status: {bridge['validation_result']['status']}")
        print(f"  - Hallucination check: {bridge['hallucination_check']['result']}")
        
        # Test semantic mapping validation with a relevant concept
        if "agent" in user_intent.lower():
            result = domain_linguist.validate_semantic_mapping(user_intent, "ConversableAgent")
            print(f"  - Agent mapping validation: {result.status.value}")
        elif "group" in user_intent.lower():
            result = domain_linguist.validate_semantic_mapping(user_intent, "GroupChat")
            print(f"  - Group mapping validation: {result.status.value}")
        elif "chat" in user_intent.lower():
            result = domain_linguist.validate_semantic_mapping(user_intent, "GroupChat")
            print(f"  - Chat mapping validation: {result.status.value}")
        
        # Show the translation result
        print(f"  - Translation result: {bridge['translation_result']['translated_intent'][:100]}...")


def main():
    """Main function to test semantic mapping generality"""
    print("Testing that semantic mapping is general and not fixated on a single example...")
    test_multiple_semantic_mappings()


if __name__ == "__main__":
    main()