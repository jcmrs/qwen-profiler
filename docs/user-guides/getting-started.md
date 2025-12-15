# Getting Started with Qwen Profiler

## Overview
The Qwen Profiler is a multi-pillar validation system for AI agent configurations that combines technical validation, behavioral SRE, and semantic architecture. This guide will help you get started with using the profiler.

## Prerequisites
- Python 3.9 or higher
- UV package manager (recommended) or pip
- Git for version control

## Installation

### Using UV (recommended):
```bash
# Clone the repository
git clone https://github.com/jcmrs/qwen-profiler.git
cd qwen-profiler

# Set up virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -e .
```

### Using pip:
```bash
# Clone the repository
git clone https://github.com/jcmrs/qwen-profiler.git
cd qwen-profiler

# Set up virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .
```

## Basic Usage

### Running the Profiler
To run the main profiler functionality:
```bash
python -m src.main
```

### Running Tests
To run the complete test suite:
```bash
python -m pytest
```

### Running Specific Tests
To run tests for a specific pillar:
```bash
# Unit tests
python -m pytest tests/unit/

# Integration tests
python -m pytest tests/integration/
```

## Configuration
The profiler uses YAML configuration files located in the `configs/` directory:
- `configs/development.yaml` - For development environment
- `configs/staging.yaml` - For staging environment
- `configs/production.yaml` - For production environment

You can set the environment with the ENVIRONMENT variable:
```bash
export ENVIRONMENT=development
python -m src.main
```

## Architecture Overview
The profiler consists of three interconnected pillars:

1. **Technical Pillar**: Validates infrastructure and implementation
2. **Behavioral Pillar**: Ensures cognitive consistency and response quality
3. **Semantic Pillar**: Maps user intent to domain-specific implementations

## Customization
The profiler can be customized using YAML configuration profiles in the `profiles/` directory:
- `collaboration.yaml` - For collaborative scenarios
- `developer.yaml` - For development workflows
- `engineer.yaml` - For engineering tasks
- `infrastructure.yaml` - For infrastructure management
- `researcher.yaml` - For research activities
- `translator.yaml` - For semantic translation tasks