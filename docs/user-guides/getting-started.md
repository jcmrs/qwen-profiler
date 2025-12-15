# Getting Started Guide for Qwen Profiler

## Overview

The Qwen Profiler is a multi-pillar validation system for AI agent configurations that combines rigorous technical architecture with systematic behavioral programming and semantic architecture. This guide will help you get started with the system.

## Prerequisites

- Python 3.9 or higher
- pip or conda package manager
- Git (for cloning the repository)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-organization/qwen-profiler.git
cd qwen-profiler
```

### 2. Set Up Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## Basic Usage

### Running the Main Application

To run the Qwen Profiler with default settings:

```bash
python -m src.main
```

### Configuration

The system is configured through YAML files in the `configs/` directory:

- `configs/development.yaml` - For development environment
- `configs/staging.yaml` - For staging environment  
- `configs/production.yaml` - For production environment

You can set the environment using the `ENVIRONMENT` environment variable:

```bash
ENVIRONMENT=production python -m src.main
```

### Core Components

The system consists of three main pillars:

#### 1. Technical Pillar
- **Infrastructure Architect**: Handles infrastructure validation and design
- **Validation Engineer**: Runs systematic testing and validation
- **SRE Specialist**: Manages reliability and monitoring

#### 2. Behavioral Pillar
- **Behavioral Architect**: Designs cognitive frameworks and response methodologies  
- **Cognitive Validator**: Monitors behavioral consistency and methodology adherence
- **Response Coordinator**: Handles response formation and quality governance

#### 3. Semantic Pillar
- **Domain Linguist**: Performs semantic validation and translation between user intent and domain implementations

## Core Concepts

### Validation Gates
The system uses a comprehensive validation framework with multiple gates:
- Technical validation
- Behavioral integrity
- Semantic accuracy
- Integration coherence
- Performance efficiency
- Vision alignment

### Memory Management
The system has both short-term and long-term memory systems:
- Short-term memory: For temporary data and operations (with TTL)
- Long-term memory: For persistent data and system state

### Dynamic Role Activation
Roles can be dynamically activated based on system needs:
- Context-aware triggering
- Adaptive sensitivity
- Priority-based activation

## Example: Validating an AI Agent Configuration

Here's a simple example of how to use the profiler to validate an AI agent configuration:

```python
from src.core.config import ConfigManager
from src.core.memory.manager import MemoryManager
from src.integration_layer.manager import IntegrationLayer
# Import other required components...

# Initialize the system
config_manager = ConfigManager()
memory_manager = MemoryManager()
# ... initialize other components

integration_layer = IntegrationLayer(
    # Pass initialized components...
)

# Define a target configuration to validate
target_config = {
    "user_intent": "make two agents talk to each other",
    "target_framework": "autogen", 
    "expected_concept": "ConversableAgent",
    "required_methodology": {
        "steps": ["analyze", "design", "validate", "deploy"],
        "validation_gates": ["tech_implementation_check", "behavior_consistency_check"]
    }
}

# Execute integrated profiling
results = integration_layer.execute_integrated_profiling(target_config)
print(results)
```

## Troubleshooting

### Common Issues

1. **Import errors**: Make sure you're running the application as a module using `python -m src.main`
2. **Configuration errors**: Check that your config files exist and have proper syntax
3. **Memory issues**: Ensure your system has sufficient resources for the operations you're performing

## Next Steps

- Read the architecture documentation for each pillar
- Explore the API reference for detailed component information
- Check out the advanced usage guide for complex scenarios