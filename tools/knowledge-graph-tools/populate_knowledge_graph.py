"""
Script to populate the DomainLinguist with the Autogen knowledge graph
"""
from src.semantic_pillar.domain_linguist.manager import DomainLinguist, DomainFramework
from src.core.memory.manager import MemoryManager
from src.core.validation_gates.manager import ValidationGates
from tools.knowledge_graph_tools.autogen_knowledge_graph import load_autogen_knowledge_graph


def populate_autogen_knowledge_graph(domain_linguist: DomainLinguist):
    """Populate the DomainLinguist with Autogen knowledge graph"""
    knowledge_graph = load_autogen_knowledge_graph()
    
    # Get all agents from the knowledge graph
    agents = knowledge_graph.get_agents()
    
    # Add each agent to the knowledge graph
    for agent_name, agent_details in agents.items():
        # Add to the DomainLinguist's knowledge graph
        success = domain_linguist.add_to_knowledge_graph(
            DomainFramework.AUTOGEN,
            "agents",  # We'll categorize agents under 'agents' type
            agent_name,
            agent_details
        )
        
        if success:
            print(f"Successfully added {agent_name} to knowledge graph")
        else:
            print(f"Failed to add {agent_name} to knowledge graph")


def main():
    """Main function to populate the Autogen knowledge graph"""
    # Initialize the DomainLinguist
    memory_manager = MemoryManager()
    validation_gates = ValidationGates()
    domain_linguist = DomainLinguist(
        memory_manager=memory_manager,
        validation_gates=validation_gates
    )
    
    print("Populating Autogen knowledge graph...")
    populate_autogen_knowledge_graph(domain_linguist)
    
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


if __name__ == "__main__":
    main()