"""
Main entry point for the Qwen Profiler application
"""
import logging
import structlog
from .core.config import get_config, ConfigManager
from .conversational_profiler import ConversationalProfiler


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

        # Initialize the conversational profiler which handles all component initialization
        logger.info("Initializing Conversational Profiler with three-pillar backroom...")
        conversational_profiler = ConversationalProfiler()
        logger.info("Conversational Profiler with complete backroom system initialized successfully")

        # Example usage: Process a user request to demonstrate the integrated workflow
        sample_request = "I need to set up a multi-agent system where agents can collaborate to solve research tasks"

        logger.info("Processing sample user request through three-pillar backroom...")
        response = conversational_profiler.process_user_request(sample_request, framework_hint="autogen")
        logger.info(f"Response generated with {len(response.get('recommendations', {}))} recommendations")

        # Display the analysis summary to the user
        analysis_results = response.get("analysis", {})
        summary = conversational_profiler.get_analysis_summary(analysis_results)
        print("\n" + "="*60)
        print("THREE-PILLAR ANALYSIS SUMMARY")
        print("="*60)
        # Replace any Unicode characters that cause encoding issues
        safe_summary = summary.encode('ascii', errors='replace').decode('ascii')
        print(safe_summary)
        print("="*60)

        logger.info("Qwen Profiler started successfully with conversational interface")
        return conversational_profiler

    except Exception as e:
        logger.error(f"Failed to start Qwen Profiler: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    run()