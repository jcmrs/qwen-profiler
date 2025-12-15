"""
Knowledge graph tool for Autogen framework
Provides comprehensive knowledge about Autogen agents, configurations, and patterns
"""
from typing import Dict, Any, List
from enum import Enum


class KnowledgeType(Enum):
    """Types of knowledge in the graph"""
    AGENT = "agent"
    CONFIGURATION = "configuration"
    PATTERN = "pattern"
    METHOD = "method"
    PROPERTY = "property"


class AutogenKnowledgeGraph:
    """Comprehensive knowledge graph for the Autogen framework"""

    def __init__(self):
        self.knowledge_graph: Dict[KnowledgeType, Dict[str, Any]] = {
            KnowledgeType.AGENT: self._get_agents(),
            KnowledgeType.CONFIGURATION: self._get_configurations(),
            KnowledgeType.PATTERN: self._get_patterns(),
            KnowledgeType.METHOD: self._get_methods(),
            KnowledgeType.PROPERTY: self._get_properties()
        }

    def _get_agents(self) -> Dict[str, Any]:
        """Get agent knowledge"""
        return {
            "ConversableAgent": {
                "description": "Base class for agents that can engage in conversations",
                "inherits_from": ["Agent"],
                "properties": [
                    "name", "human_input_mode", "max_consecutive_auto_reply", 
                    "llm_config", "code_execution_config", "system_message"
                ],
                "methods": [
                    "send", "receive", "generate_reply", "generate_code_execution_reply",
                    "generate_function_call_reply", "generate_oai_reply"
                ],
                "usage_examples": [
                    "ConversableAgent(name='assistant', llm_config={'config_list': config_list})",
                    "ConversableAgent(name='user_proxy', llm_config=False, human_input_mode='ALWAYS')"
                ],
                "related_agents": ["AssistantAgent", "UserProxyAgent"]
            },
            "AssistantAgent": {
                "description": "A subclass of ConversableAgent optimized for assistant roles",
                "inherits_from": ["ConversableAgent"],
                "properties": [
                    "name", "system_message", "llm_config", "human_input_mode"
                ],
                "methods": [
                    "generate_oai_reply", "generate_reply", "reset"
                ],
                "usage_examples": [
                    "AssistantAgent(name='assistant', llm_config={'config_list': config_list})"
                ],
                "related_agents": ["ConversableAgent"]
            },
            "UserProxyAgent": {
                "description": "A subclass of ConversableAgent that simulates human user behavior",
                "inherits_from": ["ConversableAgent"],
                "properties": [
                    "name", "human_input_mode", "max_consecutive_auto_reply", 
                    "code_execution_config", "default_auto_reply"
                ],
                "methods": [
                    "human_input", "execute_code", "generate_reply", "run_code"
                ],
                "usage_examples": [
                    "UserProxyAgent(name='user_proxy', code_execution_config=False, human_input_mode='TERMINATE')"
                ],
                "related_agents": ["ConversableAgent"]
            },
            "GroupChat": {
                "description": "A chat environment for multiple agents",
                "properties": [
                    "agents", "admin_name", "max_round", "speaker_selection_method",
                    "allow_repeat_speaker", "messages", "speaker_transitions_dict"
                ],
                "methods": [
                    "agent_by_name", "next_agent", "print_messages", "select_speaker_msg",
                    "select_speaker", "update_all_possible_transitions", "get_speaker_transitions"
                ],
                "usage_examples": [
                    "GroupChat(agents=[agent1, agent2], messages=[], max_round=12)"
                ],
                "related_agents": ["GroupChatManager", "ConversableAgent"]
            },
            "GroupChatManager": {
                "description": "Manages group conversations between agents",
                "inherits_from": ["ConversableAgent"],
                "properties": [
                    "groupchat", "name", "admin_name", "max_round", "speaker_selection_method"
                ],
                "methods": [
                    "generate_reply", "process_all_messages_before_reply", "check_intended_reply",
                    "get_last_speaker", "get_human_input"
                ],
                "usage_examples": [
                    "GroupChatManager(groupchat=group_chat, llm_config=llm_config)"
                ],
                "related_agents": ["GroupChat", "ConversableAgent"]
            }
        }

    def _get_configurations(self) -> Dict[str, Any]:
        """Get configuration knowledge"""
        return {
            "llm_config": {
                "description": "Configuration for Large Language Model calls",
                "properties": ["config_list", "temperature", "top_p", "max_tokens", "seed"],
                "usage_examples": [
                    "{'config_list': [{'model': 'gpt-4', 'api_key': '...'}]}",
                    "{'config_list': config_list, 'temperature': 0.7}",
                    "{'config_list': [{'model': 'gpt-4', 'api_key': '...', 'base_url': '...'}], 'seed': 42}"
                ]
            },
            "code_execution_config": {
                "description": "Configuration for code execution",
                "properties": [
                    "use_docker", "work_dir", "timeout", "last_n_messages", 
                    "functions", "name", "is_local"
                ],
                "usage_examples": [
                    "{'use_docker': False}",
                    "{'work_dir': 'coding', 'use_docker': False}",
                    "{'last_n_messages': 2, 'timeout': 60}"
                ]
            }
        }

    def _get_patterns(self) -> Dict[str, Any]:
        """Get pattern knowledge"""
        return {
            "two_agent_chat": {
                "description": "Basic pattern with an assistant and a user proxy",
                "components": ["AssistantAgent", "UserProxyAgent"],
                "usage_examples": [
                    """
assistant = AssistantAgent(name='assistant', llm_config={'config_list': config_list})
user_proxy = UserProxyAgent(name='user_proxy', code_execution_config=False, human_input_mode='TERMINATE')
user_proxy.initiate_chat(assistant, message='Hello, assistant!')
"""
                ]
            },
            "group_chat": {
                "description": "Pattern with multiple agents in a group conversation",
                "components": ["ConversableAgent", "GroupChat", "GroupChatManager"],
                "usage_examples": [
                    """
group_chat = GroupChat(agents=[agent1, agent2, agent3], messages=[], max_round=12)
manager = GroupChatManager(groupchat=group_chat, llm_config=llm_config)
agent1.initiate_chat(manager, message='Let\\'s solve this problem.')
"""
                ]
            },
            "function_calling": {
                "description": "Pattern using function calling capabilities",
                "components": ["ConversableAgent", "functions"],
                "usage_examples": [
                    """
def my_function(param1, param2):
    return f"Result: {param1 + param2}"

assistant = ConversableAgent(
    name='assistant',
    llm_config={'config_list': config_list},
    functions=[{"name": "my_function", "description": "..."}]
)
"""
                ]
            }
        }

    def _get_methods(self) -> Dict[str, Any]:
        """Get method knowledge"""
        return {
            "initiate_chat": {
                "description": "Start a chat with another agent",
                "parameters": ["recipient", "clear_history", "silent", "cache", "summary_method", "max_turns"],
                "usage_examples": [
                    "user_proxy.initiate_chat(assistant, message='Solve this: 2+2')",
                    "agent1.initiate_chat(agent2, message='Hello', max_turns=2)"
                ],
                "related_to": ["ConversableAgent", "AssistantAgent", "UserProxyAgent"]
            },
            "register_function": {
                "description": "Register a function that can be called by an agent",
                "parameters": ["function_map"],
                "usage_examples": [
                    "user_proxy.register_function(function_map={'calculator': calculator_fn})"
                ],
                "related_to": ["ConversableAgent", "AssistantAgent"]
            },
            "register_reply": {
                "description": "Register a reply function for an agent",
                "parameters": ["recipient", "condition", "reply_func", "position"],
                "usage_examples": [
                    "assistant.register_reply([ConversableAgent, None], custom_reply_function)"
                ],
                "related_to": ["ConversableAgent", "AssistantAgent", "UserProxyAgent"]
            }
        }

    def _get_properties(self) -> Dict[str, Any]:
        """Get property knowledge"""
        return {
            "human_input_mode": {
                "description": "Controls how and when to ask for human input",
                "valid_values": [
                    "'ALWAYS' - Always ask for human input",
                    "'NEVER' - Never ask for human input",
                    "'TERMINATE' - Ask for input before terminating",
                    "'AUTO' - Determine automatically based on context"
                ],
                "related_to": ["ConversableAgent", "UserProxyAgent"]
            },
            "max_consecutive_auto_reply": {
                "description": "Maximum number of consecutive auto-replies before asking for human input",
                "valid_values": ["int - number of replies", "None - unlimited"],
                "related_to": ["ConversableAgent", "AssistantAgent", "UserProxyAgent"]
            },
            "speaker_selection_method": {
                "description": "Method for selecting the next speaker in group chats",
                "valid_values": [
                    "'auto' - Automatic selection based on context",
                    "'round_robin' - Rotate between speakers",
                    "'random' - Random selection",
                    "custom function - Custom selection logic"
                ],
                "related_to": ["GroupChat"]
            }
        }

    def get_knowledge(self, knowledge_type: KnowledgeType = None) -> Dict[KnowledgeType, Dict[str, Any]]:
        """Get the complete knowledge graph or specific type"""
        if knowledge_type:
            return {knowledge_type: self.knowledge_graph[knowledge_type]}
        return self.knowledge_graph

    def get_agents(self) -> Dict[str, Any]:
        """Get agent knowledge"""
        return self.knowledge_graph[KnowledgeType.AGENT]

    def get_configurations(self) -> Dict[str, Any]:
        """Get configuration knowledge"""
        return self.knowledge_graph[KnowledgeType.CONFIGURATION]

    def get_patterns(self) -> Dict[str, Any]:
        """Get pattern knowledge"""
        return self.knowledge_graph[KnowledgeType.PATTERN]

    def get_methods(self) -> Dict[str, Any]:
        """Get method knowledge"""
        return self.knowledge_graph[KnowledgeType.METHOD]

    def get_properties(self) -> Dict[str, Any]:
        """Get property knowledge"""
        return self.knowledge_graph[KnowledgeType.PROPERTY]

    def search_knowledge(self, query: str) -> List[Dict[str, Any]]:
        """Search for knowledge based on a query string"""
        query_lower = query.lower()
        results = []

        for k_type, knowledge_items in self.knowledge_graph.items():
            for name, details in knowledge_items.items():
                # Check if query matches in name, description, or usage examples
                if query_lower in name.lower() or query_lower in details.get('description', '').lower():
                    results.append({
                        'type': k_type.value,
                        'name': name,
                        'description': details.get('description', ''),
                        'details': details
                    })
                # Check if query appears in usage examples
                elif 'usage_examples' in details:
                    matching_examples = [
                        ex for ex in details['usage_examples'] 
                        if query_lower in ex.lower()
                    ]
                    if matching_examples:
                        results.append({
                            'type': k_type.value,
                            'name': name,
                            'description': details.get('description', ''),
                            'details': details,
                            'matching_examples': matching_examples
                        })

        return results


def load_autogen_knowledge_graph():
    """Factory function to create and return the Autogen knowledge graph"""
    return AutogenKnowledgeGraph()


if __name__ == "__main__":
    # Example usage
    kg = load_autogen_knowledge_graph()
    
    print("Autogen Knowledge Graph Overview:")
    print(f"- Agents: {len(kg.get_agents())}")
    print(f"- Configurations: {len(kg.get_configurations())}")
    print(f"- Patterns: {len(kg.get_patterns())}")
    print(f"- Methods: {len(kg.get_methods())}")
    print(f"- Properties: {len(kg.get_properties())}")
    
    print("\nSearching for 'ConversableAgent':")
    results = kg.search_knowledge("ConversableAgent")
    for result in results:
        print(f"- {result['name']}: {result['description']}")