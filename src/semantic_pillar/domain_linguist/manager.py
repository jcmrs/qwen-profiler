"""
Domain Linguist and Ontological Translator Manager for the Qwen Profiler
Handles semantic validation, translation between user intent and domain concepts, and ontological verification
"""
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import logging
from enum import Enum
import re

from ...core.config import get_config
from ...core.memory.manager import MemoryManager, MemoryEntry, MemoryType
from ...core.validation_gates.manager import ValidationGates, ValidationResult, GateStatus


class DomainFramework(Enum):
    """Supported domain frameworks for knowledge graphs"""
    AUTOGEN = "autogen"
    LANGROID = "langroid"
    SEMANTIC_KERNEL = "semantic_kernel"
    CREWAI = "crewai"
    LANGGRAPH = "langgraph"


class TranslationQuality(Enum):
    """Quality levels for semantic translations"""
    EXCELLENT = "excellent"
    GOOD = "good"
    ADEQUATE = "adequate"
    POOR = "poor"
    FAILED = "failed"


class SemanticValidationResult:
    """Result of semantic validation"""
    def __init__(self, success: bool, message: str, translated_terms: Optional[Dict[str, str]] = None,
                 confidence: float = 0.0, errors: Optional[List[str]] = None):
        self.success = success
        self.message = message
        self.translated_terms = translated_terms or {}
        self.confidence = confidence
        self.errors = errors or []
        self.timestamp = datetime.now()


class DomainLinguist:
    """Manages semantic validation, translation between user intent and domain concepts, and ontological verification"""
    
    def __init__(self, memory_manager: Optional[MemoryManager] = None, 
                 validation_gates: Optional[ValidationGates] = None):
        self.config = get_config()
        self.memory_manager = memory_manager or MemoryManager()
        self.validation_gates = validation_gates or ValidationGates()
        self.logger = logging.getLogger(__name__)
        
        # Domain knowledge graphs
        self.knowledge_graphs: Dict[DomainFramework, Dict[str, Any]] = {
            DomainFramework.AUTOGEN: {},
            DomainFramework.LANGROID: {},
            DomainFramework.SEMANTIC_KERNEL: {},
            DomainFramework.CREWAI: {},
            DomainFramework.LANGGRAPH: {}
        }
        
        # Translation mappings
        self.translation_mappings: Dict[str, Dict[str, str]] = {}
        
        # Ontological verification cache
        self.ontology_cache: Dict[str, Any] = {}
        
        # Initialize with basic domain mappings
        self._init_domain_mappings()
    
    def _init_domain_mappings(self):
        """Initialize with basic domain mappings and terminology"""
        # Common ambiguous terms and their precise technical translations
        self.translation_mappings["general"] = {
            "make it talk to the other one": "register a Converseable Agent with a GroupChatManager",
            "connect them together": "establish communication protocol between agents",
            "work as a team": "configure collaborative agent framework",
            "coordinate activities": "implement coordination mechanisms",
            "share information": "configure shared memory or communication channel",
            "learn from each other": "implement knowledge transfer protocols",
            "make the agents talk to each other": "create a GroupChat with ConverseableAgent instances and register them"
        }

        # Domain-specific mappings for each framework
        self.translation_mappings["autogen"] = {
            "conversable agent": "ConversableAgent",
            "group chat manager": "GroupChatManager",
            "user proxy": "UserProxyAgent",
            "assistant": "AssistantAgent",
            "llm config": "llm_config",
            "group chat": "GroupChat",
            "converseable agent": "ConversableAgent",  # Common typo variation
        }

        self.translation_mappings["crewai"] = {
            "agent": "CrewAgent",
            "task": "CrewTask",
            "crew": "Crew",
            "tools": "CrewTools"
        }

        # Initialize knowledge graphs with comprehensive Autogen terms
        self.knowledge_graphs[DomainFramework.AUTOGEN] = {
            "agents": {
                "ConversableAgent": {
                    "description": "An agent that can engage in conversations",
                    "properties": ["llm_config", "human_input_mode", "max_consecutive_auto_reply"],
                    "relationships": ["GroupChatManager", "UserProxyAgent", "AssistantAgent"],
                    "usage_examples": [
                        "ConversableAgent(name='user_proxy', llm_config=False, human_input_mode='ALWAYS')",
                        "ConversableAgent(name='assistant', llm_config={'config_list': config_list})"
                    ]
                },
                "AssistantAgent": {
                    "description": "A subclass of ConversableAgent with specific default settings for assistants",
                    "properties": ["llm_config", "system_message", "human_input_mode"],
                    "relationships": ["ConversableAgent"],
                    "usage_examples": [
                        "AssistantAgent(name='assistant', llm_config={'config_list': config_list})"
                    ]
                },
                "UserProxyAgent": {
                    "description": "A subclass of ConversableAgent that can represent a human user",
                    "properties": ["human_input_mode", "max_consecutive_auto_reply", "code_execution_config"],
                    "relationships": ["ConversableAgent"],
                    "usage_examples": [
                        "UserProxyAgent(name='user_proxy', code_execution_config=False, human_input_mode='TERMINATE')"
                    ]
                }
            },
            "chats": {
                "GroupChat": {
                    "description": "A group chat environment for multiple agents",
                    "properties": ["agents", "admin_name", "max_round", "speaker_selection_method"],
                    "relationships": ["ConversableAgent"],
                    "usage_examples": [
                        "GroupChat(agents=agent_list, messages=[], max_round=12)"
                    ]
                },
                "GroupChatManager": {
                    "description": "Manages group conversations between agents",
                    "properties": ["agents", "admin_name", "max_round", "speaker_selection_method"],
                    "relationships": ["ConversableAgent", "GroupChat"],
                    "usage_examples": [
                        "GroupChatManager(groupchat=group_chat, llm_config=llm_config)"
                    ]
                }
            },
            "configurations": {
                "llm_config": {
                    "description": "Configuration for Large Language Model",
                    "properties": ["config_list", "temperature", "seed"],
                    "relationships": ["ConversableAgent", "AssistantAgent", "GroupChatManager"],
                    "usage_examples": [
                        "{'config_list': [{'model': 'gpt-4', 'api_key': '...'}]}",
                        "{'config_list': config_list, 'temperature': 0.7}"
                    ]
                }
            }
        }

        # Initialize other knowledge graphs
        self.knowledge_graphs[DomainFramework.CREWAI]["agents"] = {
            "CrewAgent": {
                "description": "An intelligent agent in CrewAI framework",
                "properties": ["role", "goal", "tools", "verbose"],
                "relationships": ["CrewTask"]
            }
        }
    
    def translate_user_intent(self, user_intent: str, target_framework) -> SemanticValidationResult:
        """Translate ambiguous user terminology to precise technical concepts"""
        original_intent = user_intent

        # Handle both string and enum types for target_framework
        if isinstance(target_framework, str):
            # Convert string to enum
            try:
                framework_value = DomainFramework(target_framework)
            except ValueError:
                # If the string is not a valid enum, use it as-is but log warning
                framework_value = target_framework
                logging.warning(f"Unknown framework name: {target_framework}, using as string")
        else:
            # It's already an enum, extract the value
            framework_value = target_framework
            target_framework = target_framework.value

        # Apply general translations first
        translated_intent = self._apply_translations(user_intent, "general")

        # Apply framework-specific translations
        framework_key = framework_value if isinstance(framework_value, str) else framework_value.value
        if framework_key in self.translation_mappings:
            translated_intent = self._apply_translations(translated_intent, framework_key)
        
        # Calculate confidence based on number of terms translated
        original_terms = len(user_intent.split())
        translated_terms = {}
        
        if original_intent != translated_intent:
            # Extract what was translated
            orig_words = set(re.findall(r'\b\w+\b', original_intent.lower()))
            trans_words = set(re.findall(r'\b\w+\b', translated_intent.lower()))
            changed_words = orig_words - trans_words
            
            for word in changed_words:
                # Find corresponding translation
                for gen_term, tech_term in self.translation_mappings["general"].items():
                    if word in gen_term.lower():
                        translated_terms[word] = tech_term
                        break
        
        # Perform ontological verification
        verification_result = self.verify_ontological_correctness({"input": translated_intent})
        
        result = SemanticValidationResult(
            success=True,
            message=f"Translated user intent from '{original_intent}' to '{translated_intent}' for {framework_key}",
            translated_terms=translated_terms,
            confidence=0.8 if translated_terms else 0.3,  # Higher confidence if terms were translated
            errors=[] if verification_result.status == GateStatus.PASS else ["Ontological verification failed"]
        )

        # Store translation in memory
        translation_entry = MemoryEntry(
            id=f"semantic_translation_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            content={
                "original_intent": original_intent,
                "translated_intent": translated_intent,
                "target_framework": framework_key,
                "translated_terms": translated_terms,
                "confidence": result.confidence,
                "timestamp": result.timestamp.isoformat()
            },
            creation_time=result.timestamp,
            memory_type=MemoryType.SHORT_TERM,
            tags=["semantic", "translation", framework_key],
            ttl=self.config.timeout_seconds * 10
        )
        self.memory_manager.store(translation_entry)
        
        return result
    
    def _apply_translations(self, text: str, domain: str) -> str:
        """Apply translations from a specific domain to the text"""
        if domain not in self.translation_mappings:
            return text
        
        result = text
        for ambiguous_term, precise_term in self.translation_mappings[domain].items():
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(ambiguous_term) + r'\b'
            result = re.sub(pattern, precise_term, result, flags=re.IGNORECASE)
        
        return result
    
    def verify_ontological_correctness(self, target: Dict[str, Any]) -> ValidationResult:
        """Verify ontological correctness against domain knowledge graphs"""
        # Extract the text or concepts to verify
        content_to_verify = target.get("input", str(target))
        content_lower = content_to_verify.lower()

        # Check if content contains known concepts from knowledge graphs
        issues = []
        found_concepts = []

        for framework, graph in self.knowledge_graphs.items():
            for concept_type, concepts in graph.items():
                for concept_name, concept_details in concepts.items():
                    # Check for the concept in the content (case-insensitive)
                    if concept_name.lower() in content_lower:
                        found_concepts.append({
                            "concept": concept_name,
                            "framework": framework.value,
                            "type": concept_type,
                            "description": concept_details.get("description", "")
                        })

                    # Also check for related terms or properties of the concept
                    for property_name in concept_details.get("properties", []):
                        if property_name.lower() in content_lower:
                            found_concepts.append({
                                "concept": concept_name,
                                "framework": framework.value,
                                "type": concept_type,
                                "related_property": property_name,
                                "description": concept_details.get("description", "")
                            })

        # If no known concepts were found, that might be an issue
        if not found_concepts:
            # But first check if it's a common phrase that we have translations for
            has_translations = any(phrase.lower() in content_lower for phrase in self.translation_mappings.get("general", {}).keys())
            if not has_translations:
                issues.append("No known domain concepts identified in input")

        # Determine validation result
        if issues:
            status = GateStatus.FAIL
            message = f"Ontological verification identified {len(issues)} issue(s)"
        else:
            status = GateStatus.PASS
            message = "Ontological verification passed"

        result = ValidationResult(
            gate=self.validation_gates._rules.get("ontological_verification").gate
            if self.validation_gates._rules.get("ontological_verification")
            else self.validation_gates._validate_ontological_correctness.__code__.co_name,
            status=status,
            message=message,
            timestamp=datetime.now(),
            metadata={"verification_type": "ontological_correctness", "found_concepts": len(found_concepts)},
            errors=issues
        )

        # Store validation result in memory
        validation_entry = MemoryEntry(
            id=f"ontological_verification_{datetime.now().isoformat()}",
            content={
                "target": content_to_verify,
                "result": {
                    "status": result.status.value,
                    "message": result.message,
                    "metadata": result.metadata,
                    "errors": result.errors
                },
                "found_concepts": found_concepts,
                "timestamp": result.timestamp.isoformat()
            },
            creation_time=result.timestamp,
            memory_type=MemoryType.SHORT_TERM,
            tags=["semantic", "validation", "ontological"],
            ttl=self.config.timeout_seconds * 5
        )
        self.memory_manager.store(validation_entry)

        return result
    
    def validate_semantic_mapping(self, user_intent: str, expected_technical_concept: str) -> ValidationResult:
        """Validate the accuracy of semantic mapping between user intent and domain concepts"""
        # Translate the user intent
        translation_result = self.translate_user_intent(
            user_intent,
            DomainFramework.AUTOGEN  # Using a default framework for this example
        )

        # Check if the expected technical concept appears in the translated content
        translated_content = translation_result.message + " " + " ".join(translation_result.translated_terms.values())
        contains_expected = expected_technical_concept.lower() in translated_content.lower()

        # Also check the knowledge graph to see if expected concept exists
        concept_found_in_kg = False
        for framework, graph in self.knowledge_graphs.items():
            for concept_type, concepts in graph.items():
                if expected_technical_concept in concepts:
                    concept_found_in_kg = True
                    break
            if concept_found_in_kg:
                break

        if contains_expected or concept_found_in_kg:
            status = GateStatus.PASS
            message = f"Semantic mapping validated: '{user_intent}' maps to expected concept '{expected_technical_concept}'"
            errors = []
        else:
            status = GateStatus.FAIL
            message = f"Semantic mapping failed: '{user_intent}' does not map to expected concept '{expected_technical_concept}'"
            errors = [f"Expected concept '{expected_technical_concept}' not found in translation or knowledge graph"]

        # Determine the appropriate validation gate with error handling
        try:
            if self.validation_gates._rules and "semantic_mapping_check" in self.validation_gates._rules:
                gate = self.validation_gates._rules["semantic_mapping_check"].gate
            else:
                # Fallback to a default gate if the specific rule is not found
                from ...core.validation_gates.manager import ValidationGate
                gate = ValidationGate.SEMANTIC_ACCURACY
        except Exception:
            from ...core.validation_gates.manager import ValidationGate
            gate = ValidationGate.SEMANTIC_ACCURACY

        result = ValidationResult(
            gate=gate,
            status=status,
            message=message,
            timestamp=datetime.now(),
            metadata={
                "validation_type": "semantic_mapping",
                "original_intent": user_intent,
                "expected_concept": expected_technical_concept,
                "translated_terms": list(translation_result.translated_terms.values()),
                "concept_in_kg": concept_found_in_kg
            },
            errors=errors
        )

        # Store validation result in memory
        validation_entry = MemoryEntry(
            id=f"semantic_mapping_validation_{datetime.now().isoformat()}",
            content={
                "original_intent": user_intent,
                "expected_technical_concept": expected_technical_concept,
                "translation_result": {
                    "translated_terms": translation_result.translated_terms,
                    "confidence": translation_result.confidence,
                    "full_message": translation_result.message
                },
                "result": {
                    "status": result.status.value,
                    "message": result.message,
                    "metadata": result.metadata,
                    "errors": result.errors
                },
                "timestamp": result.timestamp.isoformat()
            },
            creation_time=result.timestamp,
            memory_type=MemoryType.SHORT_TERM,
            tags=["semantic", "validation", "mapping"],
            ttl=self.config.timeout_seconds * 5
        )
        self.memory_manager.store(validation_entry)

        return result
    
    def add_to_knowledge_graph(self, framework: DomainFramework, concept_type: str, 
                              concept_name: str, details: Dict[str, Any]) -> bool:
        """Add a new concept to the knowledge graph for a specific framework"""
        if framework not in self.knowledge_graphs:
            return False
        
        if concept_type not in self.knowledge_graphs[framework]:
            self.knowledge_graphs[framework][concept_type] = {}
        
        self.knowledge_graphs[framework][concept_type][concept_name] = details
        
        # Store the knowledge graph update in memory
        knowledge_entry = MemoryEntry(
            id=f"knowledge_graph_update_{framework.value}_{concept_name}",
            content={
                "framework": framework.value,
                "concept_type": concept_type,
                "concept_name": concept_name,
                "details": details,
                "timestamp": datetime.now().isoformat()
            },
            creation_time=datetime.now(),
            memory_type=MemoryType.LONG_TERM,
            tags=["semantic", "knowledge_graph", framework.value, concept_type],
            priority=7
        )
        self.memory_manager.store(knowledge_entry)
        
        self.logger.info(f"Added concept '{concept_name}' to {framework.value} knowledge graph")
        return True
    
    def query_knowledge_graph(self, framework: DomainFramework, 
                            concept_name: str) -> Optional[Dict[str, Any]]:
        """Query the knowledge graph for a specific concept"""
        if framework not in self.knowledge_graphs:
            return None
        
        # Search through all concept types in the framework
        for concept_type, concepts in self.knowledge_graphs[framework].items():
            if concept_name in concepts:
                result = concepts[concept_name].copy()
                result["framework"] = framework.value
                result["concept_type"] = concept_type
                return result
        
        return None
    
    def prevent_hallucination(self, input_text: str) -> SemanticValidationResult:
        """Prevent hallucinations by validating against grounded semantic knowledge"""
        try:
            # Check if the input contains known concepts
            known_concepts_found = 0
            total_input_words = 0

            # Extract relevant words from input
            if input_text:
                # Clean the input text
                input_lower = input_text.lower()
                words = re.findall(r'\b\w+\b', input_lower)
                total_input_words = len(words)
            else:
                words = []
                total_input_words = 0

            # Look for any known concepts in the input text
            input_text_lower = input_text.lower() if input_text else ""

            # Walk through knowledge graphs to find known concepts
            for framework, graph in self.knowledge_graphs.items():
                for concept_type, concepts in graph.items():
                    for concept_name in concepts.keys():
                        if concept_name.lower() in input_text_lower:
                            known_concepts_found += 1

                    # Also check for properties of concepts
                    for concept_name, concept_details in concepts.items():
                        for prop_name in concept_details.get("properties", []):
                            if prop_name.lower() in input_text_lower:
                                known_concepts_found += 1

            # Also check for known translation mappings
            for mapping_key in self.translation_mappings.get("general", {}).keys():
                if mapping_key.lower() in input_text_lower:
                    known_concepts_found += 1

            for mapping_key in self.translation_mappings.get("autogen", {}).keys():
                if mapping_key.lower() in input_text_lower:
                    known_concepts_found += 1

            # Calculate confidence based on known concepts ratio
            if total_input_words > 0:
                # Normalize by total input words but ensure we don't get too penalized for longer text
                # with just a few known concepts
                if known_concepts_found > 0:
                    # If at least one known concept is found, provide more reasonable confidence
                    confidence = min(known_concepts_found / total_input_words * 3, 1.0)  # Cap at 1.0
                else:
                    confidence = 0.0
            else:
                confidence = 0.0  # No words found in input

            # Determine if hallucination risk is high
            hallucination_risk = "low" if confidence > 0.2 else "high"  # Lowered threshold

            if hallucination_risk == "high":
                success = False
                message = f"High hallucination risk detected: {known_concepts_found} known concepts found in {total_input_words} total words"
            else:
                success = True
                message = f"Low hallucination risk: {known_concepts_found} known concepts validated in {total_input_words} total words"

            result = SemanticValidationResult(
                success=success,
                message=message,
                confidence=confidence,
                errors=["High hallucination risk"] if hallucination_risk == "high" else []
            )
        except Exception as e:
            # Handle any error gracefully
            self.logger.error(f"Error in hallucination prevention: {str(e)}")
            result = SemanticValidationResult(
                success=False,
                message=f"Hallucination check failed due to error: {str(e)}",
                confidence=0.0,
                errors=[f"Hallucination check error: {str(e)}"]
            )

        # Store hallucination check in memory
        hallucination_entry = MemoryEntry(
            id=f"hallucination_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            content={
                "input_text": input_text,
                "result": {
                    "success": result.success,
                    "message": result.message,
                    "confidence": result.confidence,
                    "errors": result.errors
                },
                "timestamp": datetime.now().isoformat()
            },
            creation_time=datetime.now(),
            memory_type=MemoryType.SHORT_TERM,
            tags=["semantic", "hallucination"],
            ttl=self.config.timeout_seconds * 5
        )
        self.memory_manager.store(hallucination_entry)

        return result
    
    def build_semantic_bridge(self, user_intent: str, target_framework) -> Dict[str, Any]:
        """Build a semantic bridge between user intent and domain-specific implementation"""
        # Handle both string and enum types for target_framework
        if isinstance(target_framework, str):
            # Convert string to enum
            try:
                framework_value = DomainFramework(target_framework)
            except ValueError:
                # If the string is not a valid enum, use it as-is but log warning
                framework_value = target_framework
                framework_key = target_framework
                logging.warning(f"Unknown framework name: {target_framework}, using as string")
            else:
                framework_key = framework_value.value
        else:
            # It's already an enum, extract the value
            framework_value = target_framework
            framework_key = target_framework.value

        # Translate user intent
        translation_result = self.translate_user_intent(user_intent, framework_value)

        # Validate the translation
        validation_result = self.verify_ontological_correctness(
            {"input": translation_result.message}
        )

        # Prevent hallucinations
        hallucination_check = self.prevent_hallucination(translation_result.message)

        # Construct the semantic bridge
        bridge = {
            "user_intent": user_intent,
            "target_framework": framework_key,
            "translation_result": {
                "translated_intent": translation_result.message,
                "translated_terms": translation_result.translated_terms,
                "confidence": translation_result.confidence
            },
            "validation_result": {
                "status": validation_result.status.value,
                "message": validation_result.message,
                "errors": validation_result.errors
            },
            "hallucination_check": {
                "result": hallucination_check.success,
                "confidence": hallucination_check.confidence,
                "errors": hallucination_check.errors
            },
            "overall_success": (
                translation_result.confidence > 0.5 and
                validation_result.status == GateStatus.PASS and
                hallucination_check.success
            ),
            "timestamp": datetime.now().isoformat()
        }

        # Store semantic bridge in memory
        bridge_entry = MemoryEntry(
            id=f"semantic_bridge_{framework_key}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            content=bridge,
            creation_time=datetime.now(),
            memory_type=MemoryType.SHORT_TERM,
            tags=["semantic", "bridge", "translation", framework_key],
            ttl=self.config.timeout_seconds * 15
        )
        self.memory_manager.store(bridge_entry)
        
        return bridge
    
    def get_semantic_report(self) -> Dict[str, Any]:
        """Generate a comprehensive semantic architecture report"""
        report = {
            "summary": {
                "frameworks_supported": [f.value for f in DomainFramework],
                "total_knowledge_graphs": len(self.knowledge_graphs),
                "total_mappings": sum(len(m) for m in self.translation_mappings.values()),
                "timestamp": datetime.now().isoformat()
            },
            "knowledge_graphs": {
                framework.value: {
                    concept_type: len(concepts) 
                    for concept_type, concepts in graph.items()
                }
                for framework, graph in self.knowledge_graphs.items()
            },
            "translation_mappings": {
                domain: len(mappings) 
                for domain, mappings in self.translation_mappings.items()
            }
        }
        
        return report