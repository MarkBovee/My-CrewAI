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

## ⚠️ Knowledge Sources - DISABLED

**Important**: Vector-based knowledge sources have been **permanently disabled** in this project due to GPU memory exhaustion issues.

### Why Knowledge Sources Were Removed

CrewAI's knowledge sources feature uses vector embeddings (via models like `mxbai-embed-large`) that consume significant GPU memory. In our testing:

- **Problem**: Knowledge sources + Ollama embeddings consumed all available GPU memory
- **Result**: Agent models (qwen3:1.7b) failed with "out of memory" errors during execution
- **Impact**: Complete system failure when trying to run multi-agent workflows

### Alternative Approach

Instead of vector knowledge sources, agents now rely on:

- **DuckDuckGo Search Tool**: Real-time web search for current information
- **ScrapeWebsiteTool**: Direct website content extraction
- **File-based Context**: Task outputs passed between agents via flow state

This approach provides:

- ✅ **Zero GPU memory overhead** for knowledge storage
- ✅ **Real-time information** via web search
- ✅ **Scalable execution** without memory constraints
- ✅ **Reliable performance** on resource-constrained systems

### Future Considerations

If you have access to systems with more GPU memory (16GB+ dedicated GPU), you could re-enable knowledge sources by:

1. Modifying `src/linkedin/crew.py` to include knowledge sources configuration
2. Ensuring adequate GPU memory for both embeddings and agent models
3. Testing with your specific hardware configuration

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
    │   ├── llm_helper.py
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

## CrewAI Tools Overview

CrewAI provides 40+ pre-built tools to enhance your agents' capabilities. Here are the main tool categories available:

### 🔍 Search & Research Tools

- **SerperDevTool**: Google search API integration
- **DuckDuckGo Search**: Privacy-focused web search (currently used)
- **YouTubeSearchTool**: Search and analyze YouTube content
- **GitHubSearchTool**: Find and analyze code repositories

### 📄 File & Document Tools

- **FileReadTool**: Read various file formats (PDF, DOCX, JSON, CSV, etc.)
- **DirectoryReadTool**: Navigate and read directory structures
- **CSVSearchTool**: Search and analyze CSV files
- **JSONSearchTool**: Query JSON data structures

### 🌐 Web Scraping & Browsing Tools

- **ScrapeWebsiteTool**: Extract content from websites
- **FirecrawlTool**: Advanced web scraping with Firecrawl
- **SeleniumTool**: Browser automation for dynamic content

### 🗄️ Database & Data Tools

- **MySQLTool**: Connect to MySQL databases
- **PostgreSQLTool**: PostgreSQL database operations
- **SnowflakeTool**: Data warehouse queries
- **QdrantTool**: Vector database operations
- **WeaviateTool**: Vector search and storage

### 🤖 AI & Machine Learning Tools

- **CodeInterpreterTool**: Execute Python code dynamically
- **DALL-E Tool**: Generate images with OpenAI's DALL-E
- **RAGTool**: Implement Retrieval-Augmented Generation
- **VisionTool**: Process images and vision tasks

### ☁️ Cloud & Storage Tools

- **S3ReaderTool**: Access AWS S3 files
- **AmazonBedrockTool**: AWS AI services integration

### ⚙️ Automation Tools

- **ApifyTool**: Web scraping and automation platform
- **ComposioTool**: Connect with external services

### 🔧 Tool Usage Example

```python
from crewai_tools import FileReadTool, SerperDevTool

# Add tools to your agent
agent = Agent(
    role="Research Analyst",
    tools=[FileReadTool(), SerperDevTool()],
    # ... other configuration
)
```

For the complete list of tools and detailed documentation, visit: [CrewAI Tools Documentation](https://docs.crewai.com/en/tools/overview)

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
