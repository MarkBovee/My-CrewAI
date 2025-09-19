# CrewAI Instagram Project

Welcome to the CrewAI Instagram Project, powered by [crewAI](https://crewai.com) and integrated with local Ollama LLM. This project demonstrates a multi-agent AI system for researching and creating LinkedIn content about AI and tech skills trends.

## Features

- 🔍 **DuckDuckGo Search Integration**: Research latest AI and tech trends
- 🤖 **Three-Agent Crew System**: Coach, Influencer Writer, and Critic working together
- 🧠 **Local Ollama LLM**: Uses `qwen3:4b` model for AI processing
- ⚙️ **Modular Architecture**: Organized helpers and tools
- 🛠️ **Configuration Management**: Comprehensive utilities for managing models and settings

## Project Structure

```
src/
└── instagram/
    ├── config/          # Agent and task configurations
    │   ├── agents.yaml
    │   └── tasks.yaml
    ├── helpers/         # Utility modules
    │   ├── ollama_helper.py
    │   ├── config_helper.py
    │   └── __init__.py
    ├── tools/           # Custom CrewAI tools
    │   ├── duckduckgo_search_tool.py
    │   └── __init__.py
    ├── crew.py          # Main crew definition
    └── main.py          # Entry point
```

## Installation

Ensure you have Python >=3.10 <3.14 and Ollama installed on your system.

### Prerequisites

1. **Install Ollama**: Download from [ollama.ai](https://ollama.ai)
2. **Pull the qwen3:4b model**:
   ```bash
   ollama pull qwen3:4b
   ```
3. **Start Ollama server**:
   ```bash
   ollama serve
   ```

### Install Dependencies

```bash
pip install uv
crewai install
```

## Configuration

The project uses YAML configuration files for agents and tasks:

- `src/instagram/config/agents.yaml` - Define agent roles, goals, and LLM models
- `src/instagram/config/tasks.yaml` - Define tasks and expected outputs

### Configuration Helper

Use the configuration helper to manage your setup:

```bash
# Check status and validate configuration
python config_helper.py --all

# Check Ollama status
python config_helper.py --status

# List available models
python config_helper.py --models

# Validate agent configurations
python config_helper.py --validate
```

## Running the Project

### Method 1: Using CrewAI CLI
```bash
crewai run
```

### Method 2: Direct Python Execution
```bash
python -c "import sys; sys.path.append('src'); from instagram.main import run; run()"
```

This will start the crew execution, where agents collaborate to:
1. **Research**: Coach agent searches for latest AI/tech skills using DuckDuckGo
2. **Create**: Influencer agent writes a LinkedIn post based on research
3. **Critique**: Critic agent reviews and refines the content

## Crew Agents

### 🎯 Senior Career Coach
- **Role**: Research specialist for AI and tech trends
- **Tools**: DuckDuckGo Search
- **Goal**: Find emerging career skills in AI and tech

### ✍️ LinkedIn Influencer Writer  
- **Role**: Content creation expert
- **Goal**: Write engaging LinkedIn posts (max 200 words)
- **Style**: Includes emojis and hashtags

### 🔍 Expert Writing Critic
- **Role**: Quality assurance specialist
- **Goal**: Provide actionable feedback and ensure content quality
- **Focus**: Concise, compelling, and properly formatted content

## Key Features

- **Local LLM Integration**: No API keys required, runs entirely on your machine
- **Modular Design**: Easily extensible helpers and tools
- **Configuration Management**: YAML-based setup with validation utilities
- **Real-time Search**: Current AI trends via DuckDuckGo integration

## Troubleshooting

### Common Issues

1. **Ollama not running**: Ensure `ollama serve` is active
2. **Model not found**: Pull the required model with `ollama pull qwen3:4b`
3. **Import errors**: Verify you're running from the project root directory

### Getting Help

For more information about CrewAI concepts:

- [Official CrewAI Documentation](https://docs.crewai.com)
- [Agents Documentation](https://docs.crewai.com/en/concepts/agents)
- [Tasks Documentation](https://docs.crewai.com/en/concepts/tasks)  
- [Crews Documentation](https://docs.crewai.com/en/concepts/crews)
- [Tools Documentation](https://docs.crewai.com/en/concepts/tools)
- [Knowledge Documentation](https://docs.crewai.com/en/concepts/knowledge)
- [Collaboration Documentation](https://docs.crewai.com/en/concepts/collaboration)
- [Flows Documentation](https://docs.crewai.com/en/concepts/flows)
- [Event Listener Documentation](https://docs.crewai.com/en/concepts/event-listener)

## Support

For support, questions, or feedback:

- [CrewAI Documentation](https://docs.crewai.com)
- [CrewAI GitHub Repository](https://github.com/joaomdmoura/crewai)
- [Join the Discord Community](https://discord.com/invite/X4JWnZnxPb)

---

*Built with ❤️ using CrewAI and Ollama for local LLM processing*
