# CrewAI Multi-Flow Control Center

Welcome to the CrewAI Multi-Flow Control Center, powered by [crewAI](https://crewai.com) and integrated with local Ollama LLM. This project demonstrates multiple specialized AI workflows with proper separation following CrewAI best practices.

## 🏗️ Project Structure

Following CrewAI examples repository patterns, this project uses isolated flows:

```
flows/
├── linkedin_content_flow/     # LinkedIn content generation
│   ├── src/linkedin_content_flow/
│   ├── pyproject.toml
│   └── README.md
├── experience_blog_flow/      # Experience-to-blog transformation
│   ├── src/experience_blog_flow/
│   ├── pyproject.toml
│   └── README.md
knowledge/                     # Shared knowledge sources
output/                        # Generated content
www/                          # Web interface
web_server.py                 # FastAPI server
```

## 🚀 Available Flows

### 1. LinkedIn Content Flow
Multi-agent system for LinkedIn content creation:
- **Coach**: Guides content strategy and quality
- **Researcher**: Conducts web research
- **Writer**: Creates comprehensive articles  
- **Influencer**: Generates engaging posts

### 2. Experience Blog Flow
Transform personal experiences into enhanced blog posts:
- **Experience Analyst**: Structures personal experiences
- **Research Agent**: Adds context and research
- **Blog Writer**: Creates comprehensive blog content

## 🌟 Features

- 🌐 **Web Interface**: Professional flow management and execution
- 🔄 **Multiple Flows**: Specialized workflows following CrewAI patterns
- 🔍 **DuckDuckGo Search**: Real-time research capabilities
- 🤖 **Optimized Agents**: Different LLMs for different tasks
- 🧠 **Local Ollama**: Multiple model support (llama3.1, qwen2.5, qwq)
- 📊 **Flow Visualization**: Real-time execution tracking
- 🛡️ **Token Management**: Efficient memory and token usage
- � **Modular Architecture**: Proper separation of concerns

## 📋 Usage

### Method 1: CrewAI CLI (Recommended)

Each flow can be run independently:

```bash
# LinkedIn Content Flow
cd flows/linkedin_content_flow
crewai run

# Experience Blog Flow  
cd flows/experience_blog_flow
crewai run
```

### Method 2: Web Interface

Start the web server for interactive management:

```bash
# Start web server
python web_server.py
# OR
.\start-web.ps1
```

Navigate to http://localhost:8000 for the web interface.

### Method 3: Direct Python Execution

```python
# LinkedIn Content Flow
from flows.linkedin_content_flow.src.linkedin_content_flow.main import LinkedInContentFlow
flow = LinkedInContentFlow()
result = flow.kickoff(inputs={"topic": "AI trends 2024"})

# Experience Blog Flow
from flows.experience_blog_flow.src.experience_blog_flow.main import ExperienceBlogFlow
flow = ExperienceBlogFlow()
result = flow.kickoff(inputs={"experience_text": "Your experience..."})
```

## 🧠 Knowledge Management

The system uses persistent knowledge management:

- **Web Search Results**: Stored in `knowledge/web_search_results.json`
- **Article Memory**: Topic tracking in `knowledge/article_memory.json`
- **Local Embeddings**: Uses `mxbai-embed-large` via Ollama

### Knowledge Reset

```bash
python reset_knowledge.py --type all --stats
```

## 🛠️ Installation

### Prerequisites

1. **Install Ollama**: Download from [ollama.ai](https://ollama.ai)
2. **Pull required models**:
   ```bash
   ollama pull llama3.1:8b
   ollama pull qwen2.5:14b  
   ollama pull qwq:32b
   ollama pull mxbai-embed-large
   ```
3. **Start Ollama server**:
   ```bash
   ollama serve
   ```

### Python Environment

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd My-CrewAI
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Test the installation**:
   ```bash
   # Test LinkedIn Content Flow
   cd flows/linkedin_content_flow
   python -c "from src.linkedin_content_flow.main import LinkedInContentFlow; print('✅ LinkedIn flow ready')"
   
   # Test Experience Blog Flow  
   cd ../experience_blog_flow
   python -c "from src.experience_blog_flow.main import ExperienceBlogFlow; print('✅ Blog flow ready')"
   ```

## 🎯 Model Usage Strategy

Different flows use optimized models for specific tasks:

- **llama3.1:8b**: General purpose, web search, content generation
- **qwen2.5:14b**: Structured analysis, experience processing  
- **qwq:32b**: Complex reasoning, creative writing, blog enhancement
- **mxbai-embed-large**: Knowledge source embeddings

## 🔧 Configuration

Each flow has its own configuration in:
- `flows/*/src/*/config/agents.yaml` - Agent definitions and models
- `flows/*/src/*/config/tasks.yaml` - Task workflows and outputs

## 📊 Output Structure

Generated content is organized by type:
```
output/
├── articles/        # Research articles (LinkedIn flow)
├── blogs/          # Blog posts (both flows)
└── posts/          # Social media posts (LinkedIn flow)
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
