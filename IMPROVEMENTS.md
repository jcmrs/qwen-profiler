# Qwen Profiler: Multi-Pillar AI Agent Configuration System

## Overview

The Qwen Profiler is a meta-validation system designed to ensure the quality and reliability of AI agent configurations across three critical dimensions: technical infrastructure, behavioral consistency, and semantic accuracy. Through empirical validation and behavioral SRE principles, the system bridges the gap between natural language user intent and precise AI requirements.

## Architecture

The system follows a three-pillar architecture:

### 1. Technical Pillar: Infrastructure & Validation
- **Components**: Infrastructure Architect, Validation Engineer, SRE Specialist
- **Responsibilities**: Systematic validation, reliability engineering, and technical implementation framework
- **Features**: Configuration validation, performance benchmarking, monitoring, and observability

### 2. Behavioral Pillar: Cognitive Consistency & Response Formation
- **Components**: Behavioral Architect, Cognitive Validator, Response Coordinator
- **Responsibilities**: Behavioral consistency monitoring, methodology adherence, and cognitive pattern validation
- **Features**: Behavioral drift detection, response quality assurance, cognitive validation

### 3. Semantic Pillar: Semantic Architecture
- **Component**: Domain Linguist and Ontological Translator
- **Responsibilities**: Translation between natural language user intent and domain-specific technical implementations
- **Features**: Ontological verification, semantic mapping, hallucination prevention

## Key Improvements

### Semantic Mapping Enhancement
- Implemented comprehensive Autogen knowledge graph with agent definitions, properties, methods, and usage examples
- Enhanced semantic bridge functionality to properly translate user intent to technical concepts
- Improved ontological verification to recognize domain-specific terminology
- Added hallucination prevention with confidence scoring

### Validation System Improvements  
- Updated configuration validation to properly handle Pydantic model configurations
- Enhanced implementation validation to support system components during initialization
- Improved performance validation with more flexible thresholds
- Added methodology adherence validation that properly handles initialization scenarios

### Activation System Dependencies
- Defined proper dependency relationships between behavioral components (Cognitive Validator depends on Behavioral Architect)
- Improved activation logic to handle component interdependencies

## Key Features

### Domain Knowledge Graphs
The system includes comprehensive knowledge graphs for various AI agent frameworks:

#### Autogen Framework
- **Agents**: ConversableAgent, AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
- **Configurations**: llm_config, code_execution_config
- **Patterns**: Two-agent chat, group chat, function calling
- **Methods**: initiate_chat, register_function, register_reply
- **Properties**: human_input_mode, max_consecutive_auto_reply, speaker_selection_method

### Semantic Bridge
- Translates ambiguous user terminology to precise technical concepts
- Example: "make the agents talk to each other" → "create a GroupChat with ConversableAgent instances and register them"
- Performs ontological verification against domain knowledge graphs
- Prevents hallucinations by validating against grounded semantic knowledge

### Cross-Pillar Integration
- Unified monitoring dashboard
- Integrated validation across all pillars
- Synergistic coordination mechanisms
- Validation gate protocols

## Usage

### Running the System
```bash
python -m src.main
```

### Testing
```bash
python -m pytest tests/
```

## Configuration

The system supports environment-specific configurations in the `configs/` directory:
- `development.yaml`
- `staging.yaml` 
- `production.yaml`

Configuration options include:
- Environment settings
- Logging levels
- Worker counts
- Timeout values
- Validation thresholds

## Directory Structure

```
qwen-profiler/
├── docs/                           # Documentation for the profiler system
├── research/                       # Research phase materials
├── src/                            # Source code
│   ├── technical-pillar/           # Infrastructure & Validation
│   ├── behavioral-pillar/          # Cognitive Consistency & Response Formation
│   ├── semantic-pillar/            # Semantic Architecture (Domain Linguist)
│   ├── integration-layer/          # Cross-pillar coordination
│   └── core/                       # Core systems (memory, validation, activation)
├── profiles/                       # YAML configuration profiles for roles
├── configs/                        # Configuration files for different environments
├── external-deliverables/          # Deliverables for external projects
├── tests/                          # Test suites for all pillars
├── tools/                          # Utility scripts and tools
└── reports/                        # Generated reports
```

## Testing

The system includes comprehensive test coverage:
- Unit tests for individual components
- Integration tests across pillars
- Validation scenario tests
- Behavioral SRE tests

Run all tests with:
```bash
python -m pytest tests/ -v
```

## Future Enhancements

- Extend knowledge graphs to include Langroid, Semantic Kernel, CrewAI, and LangGraph frameworks
- Implement advanced NLP for semantic parsing
- Enhance behavioral reliability metrics and SRE frameworks
- Improve activation system dependency management

## Contributing

See the CONTRIBUTING.md file for details on how to contribute to this project.

## License

This project is licensed under the terms found in the LICENSE file.