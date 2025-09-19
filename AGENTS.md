# AI Agent Instructions

## Project Overview
This is a CrewAI multi-agent system that generates LinkedIn content about AI/tech trends. Three AI agents collaborate: a **Coach** (researcher), **Influencer** (writer), and **Critic** (reviewer) working sequentially to produce refined LinkedIn posts.

## Architecture & Key Patterns

### 1. YAML-Driven Configuration
- **Agents**: `src/instagram/config/agents.yaml` - Define roles, goals, LLM models, and thinking behavior
- **Tasks**: `src/instagram/config/tasks.yaml` - Define workflow steps and expected outputs
- **Pattern**: Use `{current_year}` templating in goals for dynamic inputs

### 2. Local Ollama LLM Integration
- **Helper**: `src/instagram/helpers/ollama_helper.py` - Centralized LLM management
- **Key Pattern**: Pass thinking control via `model_kwargs["options"]["think"]` to disable LLM verbosity
- **Configuration**: Each agent can have different models and thinking settings
- **Connection**: Always uses `http://localhost:11434` base URL

### 3. CrewAI Framework Integration
- **Crew Class**: `src/instagram/crew.py` uses `@CrewBase` decorator with `@agent`, `@task`, `@crew` methods
- **Agent Creation**: Combine YAML config with programmatic LLM instances and tools
- **Pattern**: Use `self.agents_config['agent_name']` and `self.tasks_config['task_name']` for YAML loading

### 4. Custom Tools Architecture
- **Location**: `src/instagram/tools/` - All custom tools inherit from `BaseTool`
- **DuckDuckGo**: Modern implementation using `ddgs.DDGS().text()` API (not langchain_community)
- **Pattern**: Define `Input` schema with Pydantic, implement `_run()` method

## Critical Development Workflows

### Running the Crew
```bash
# Method 1: CrewAI CLI (preferred)
crewai run

# Method 2: Direct Python execution
python -c "import sys; sys.path.append('src'); from instagram.main import run; run()"
```

### Configuration Management
```bash
# Comprehensive status check
python config_helper.py --all

# Check Ollama connectivity
python config_helper.py --status

# Validate agent models exist
python config_helper.py --validate
```

### Adding New Agents
1. Add agent config to `agents.yaml` with `llm`, `thinking`, `role`, `goal`, `backstory`
2. Create `@agent` method in `crew.py` using `OllamaHelper.create_llm_instance()`
3. Add to crew's `agents=[]` list
4. Define corresponding task in `tasks.yaml`

## Project-Specific Conventions

### Helper Module Pattern
- **OllamaHelper**: LLM instance caching, YAML config loading, connection validation
- **ConfigHelper**: Model management, pulling, validation, comprehensive reporting
- Both provide CLI interfaces and programmatic APIs

### Input Handling
- Main execution uses `{'topic': 'AI LLMs', 'current_year': str(datetime.now().year)}`
- YAML configs support templating: `goal: "Find skills in {current_year}"`

### Thinking Control
- Set `thinking: false` in agent YAML to disable LLM verbosity
- Passed via `model_kwargs.options.think` to Ollama API
- Critical for clean output in production

## Integration Points

### External Dependencies
- **Ollama**: Local LLM server, requires `ollama serve` and model pulls
- **DuckDuckGo**: Real-time search via `ddgs` package (not langchain)
- **CrewAI**: Framework handles agent orchestration and task sequencing

### Key Files for Extension
- `src/instagram/tools/` - Add new capabilities (web scraping, APIs, etc.)
- `src/instagram/helpers/` - Add new LLM providers or config management
- `config/*.yaml` - Modify agent behavior without code changes

## Common Pitfalls
- Always run from project root (path dependencies)
- Ensure Ollama server is running before crew execution
- Check model exists locally before referencing in agent config
- Use `ddgs` directly, not `langchain_community.tools.DuckDuckGoSearchRun`
- Import tools properly: `from instagram.tools import DuckDuckGoSearchTool`

## Testing & Debugging
- Use `config_helper.py --all` to diagnose setup issues
- Check `verbose: true` in agent configs for detailed execution logs
- Validate YAML syntax and agent/task relationships before running crew