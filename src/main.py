"""
Main entry point for the Qwen Profiler application
"""
import logging
import structlog
from .core.config import get_config, ConfigManager
from .core.memory.manager import MemoryManager
from .core.activation_system.manager import ActivationSystem
from .core.validation_gates.manager import ValidationGates

# Technical pillar imports
from .technical_pillar.infrastructure_architect.manager import InfrastructureArchitect
from .technical_pillar.validation_engineer.manager import ValidationEngineer
from .technical_pillar.sre_specialist.manager import SRESpecialist

# Behavioral pillar imports
from .behavioral_pillar.behavioral_architect.manager import BehavioralArchitect
from .behavioral_pillar.cognitive_validator.manager import CognitiveValidator
from .behavioral_pillar.response_coordinator.manager import ResponseCoordinator

# Semantic pillar imports
from .semantic_pillar.domain_linguist.manager import DomainLinguist

# Integration layer import
from .integration_layer.manager import IntegrationLayer


def setup_logging():
    """Set up logging configuration"""
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configure root logger
    config = get_config()
    logging.basicConfig(
        level=getattr(logging, config.log_level),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )


def initialize_components():
    """Initialize all system components across all pillars"""
    config = get_config()
    logger = structlog.get_logger(__name__)

    # Initialize core components
    memory_manager = MemoryManager()
    logger.info("Memory manager initialized")

    validation_gates = ValidationGates(memory_manager=memory_manager)
    logger.info("Validation gates initialized")

    activation_system = ActivationSystem(memory_manager=memory_manager)
    logger.info("Activation system initialized")

    # Initialize technical pillar components
    infrastructure_architect = InfrastructureArchitect(
        memory_manager=memory_manager,
        validation_gates=validation_gates
    )
    logger.info("Infrastructure Architect initialized")

    validation_engineer = ValidationEngineer(
        memory_manager=memory_manager,
        validation_gates=validation_gates
    )
    logger.info("Validation Engineer initialized")

    sre_specialist = SRESpecialist(
        memory_manager=memory_manager,
        validation_gates=validation_gates
    )
    logger.info("SRE Specialist initialized")

    # Initialize behavioral pillar components
    behavioral_architect = BehavioralArchitect(
        memory_manager=memory_manager,
        validation_gates=validation_gates
    )
    logger.info("Behavioral Architect initialized")

    cognitive_validator = CognitiveValidator(
        memory_manager=memory_manager,
        validation_gates=validation_gates,
        behavioral_architect=behavioral_architect
    )
    logger.info("Cognitive Validator initialized")

    response_coordinator = ResponseCoordinator(
        memory_manager=memory_manager,
        validation_gates=validation_gates,
        behavioral_architect=behavioral_architect,
        cognitive_validator=cognitive_validator
    )
    logger.info("Response Coordinator initialized")

    # Initialize semantic pillar components
    domain_linguist = DomainLinguist(
        memory_manager=memory_manager,
        validation_gates=validation_gates
    )
    logger.info("Domain Linguist initialized")

    # Initialize integration layer
    integration_layer = IntegrationLayer(
        memory_manager=memory_manager,
        activation_system=activation_system,
        validation_gates=validation_gates,
        infrastructure_architect=infrastructure_architect,
        validation_engineer=validation_engineer,
        sre_specialist=sre_specialist,
        behavioral_architect=behavioral_architect,
        cognitive_validator=cognitive_validator,
        response_coordinator=response_coordinator,
        domain_linguist=domain_linguist
    )
    logger.info("Integration Layer initialized")

    return {
        # Core components
        'memory_manager': memory_manager,
        'activation_system': activation_system,
        'validation_gates': validation_gates,

        # Technical pillar
        'infrastructure_architect': infrastructure_architect,
        'validation_engineer': validation_engineer,
        'sre_specialist': sre_specialist,

        # Behavioral pillar
        'behavioral_architect': behavioral_architect,
        'cognitive_validator': cognitive_validator,
        'response_coordinator': response_coordinator,

        # Semantic pillar
        'domain_linguist': domain_linguist,

        # Integration layer
        'integration_layer': integration_layer
    }


def run():
    """Run the Qwen Profiler application"""
    logger = structlog.get_logger(__name__)

    try:
        # Load configuration
        config_manager = ConfigManager()
        config = config_manager.get_config()
        logger.info(f"Configuration loaded for environment: {config.environment}")

        # Set up logging
        setup_logging()
        logger.info("Logging configured")

        # Initialize all components
        components = initialize_components()
        logger.info("All components initialized successfully")

        # Perform initial integrated profiling to test the system
        test_target = {
            "user_intent": "make the agents talk to each other",
            "target_framework": "autogen",
            "expected_concept": "ConversableAgent",
            "required_methodology": {
                "steps": ["analyze", "design", "validate", "deploy"],
                "validation_gates": ["tech_implementation_check", "behavior_consistency_check"]
            }
        }

        integration_layer = components['integration_layer']
        results = integration_layer.execute_integrated_profiling(test_target)
        logger.info("Initial integrated profiling completed", results=results)

        # Run unified monitoring
        monitoring_report = integration_layer.unified_monitoring()
        logger.info("Unified monitoring report generated",
                   report_size=len(str(monitoring_report)))

        # Display integration dashboard
        dashboard = integration_layer.get_integration_dashboard()
        logger.info("Integration dashboard", dashboard=dashboard)

        logger.info("Qwen Profiler started successfully")
        return components

    except Exception as e:
        logger.error(f"Failed to start Qwen Profiler: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    run()