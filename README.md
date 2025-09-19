# CrewAI Flow Control Center

Welcome to the CrewAI Flow Control Center, powered by [crewAI](https://crewai.com) and integrated with local Ollama LLM. This project demonstrates a multi-agent AI system with a professional web interface for managing and executing CrewAI flows.

## Features

- 🌐 **Web Interface**: Professional web-based flow management and execution
- 🔄 **CrewAI Flows**: Advanced flow architecture for complex multi-agent workflows
- 🔍 **DuckDuckGo Search Integration**: Research latest AI and tech trends
- 🤖 **Three-Agent Crew System**: Coach, Researcher, and Influencer Writer working together
- 🧠 **Local Ollama LLM**: Uses `qwen3:4b` model for AI processing
- 📊 **Flow Visualization**: Real-time flow plots and execution tracking
- ⚙️ **Modular Architecture**: Organized helpers and tools
- 🛠️ **Configuration Management**: Comprehensive utilities for managing models and settings

## Project Structure

```
src/
└── linkedin/
    ├── config/          # Agent and task configurations
    │   ├── agents.yaml
    │   └── tasks.yaml
    ├── flows/           # CrewAI flow definitions
    │   └── create_new_post_flow.py
    ├── helpers/         # Utility modules
    │   ├── ollama_helper.py
    │   ├── config_helper.py
    │   └── __init__.py
    ├── tools/           # Custom CrewAI tools
    │   ├── duckduckgo_search_tool.py
    │   └── __init__.py
    ├── crew.py          # Main crew definition
    └── main.py          # Entry point

www/                     # Web interface
├── index.html          # Main web interface
├── assets/
│   ├── css/style.css   # CrewAI-themed styling
│   └── js/app.js       # Frontend application logic
└── plots/              # Generated flow plots

web_server.py           # FastAPI backend server
start-web.ps1           # PowerShell startup script
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

- `src/linkedin/config/agents.yaml` - Define agent roles, goals, and LLM models
- `src/linkedin/config/tasks.yaml` - Define tasks and expected outputs

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

### 🌐 Web Interface (Recommended)

Start the CrewAI Flow Control Center web interface:

```powershell
# Using PowerShell script (Windows)
.\start-web.ps1

# With custom port
.\start-web.ps1 -Port 3000

# With auto-reload for development
.\start-web.ps1 -Reload
```

Or start manually:

```bash
# Install web dependencies
pip install -r requirements-web.txt

# Start the web server
python web_server.py
```

**Access the web interface at: http://localhost:8000**

Features:
- 🎛️ **Flow Management**: Execute flows with real-time progress tracking
- 📊 **Flow Visualization**: View generated flow plots and execution history
- 🎨 **Professional UI**: CrewAI-themed interface with dark theme and orange accents
- 📈 **Dashboard**: Statistics, flow runs, and success rates

### 💻 Command Line Options

#### Method 1: Using CrewAI CLI
```bash
crewai run
```

#### Method 2: Direct Python Execution
```bash
python -c "import sys; sys.path.append('src'); from linkedin.main import run; run()"
```

#### Method 3: Using CrewAI Flows
```bash
# Run the flow directly
python -c "import sys; sys.path.append('src'); from linkedin.flows.create_new_post_flow import run_create_new_post_flow; run_create_new_post_flow()"
```

This will start the crew execution, where agents collaborate to:
1. **Research**: Coach agent searches for latest AI/tech skills using DuckDuckGo
2. **Create**: Influencer agent writes a LinkedIn post based on research
2. **Research**: Researcher agent conducts in-depth research and creates comprehensive articles
3. **Content Creation**: Influencer Writer agent creates engaging LinkedIn posts

## Crew Agents

### 🎯 Senior Career Coach
- **Role**: Research specialist for AI and tech trends
- **Tools**: DuckDuckGo Search
- **Goal**: Find emerging career skills in AI and tech

### ✍️ LinkedIn Influencer Writer  
- **Role**: Content creation expert
- **Goal**: Write engaging LinkedIn posts (max 200 words)
- **Style**: Includes emojis and hashtags


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
