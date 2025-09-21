---
applyTo: '**'
---
# CrewAI Multi-Agent System Instructions

This is a CrewAI multi-agent system for AI-powered content generation with web interface and knowledge management.

**📋 Follow the general coding workflow from `default.instructions.md` + these CrewAI-specific patterns.**

---

## 🏗️ Architecture Overview

**Multi-Agent Content Creation System:**
- **4 Specialized Agents**: Coach, Influencer, Researcher, Writer (defined in `agents.yaml`)
- **Sequential Task Flow**: Research → Analysis → Content Creation → Post Generation
- **Knowledge System**: Persistent learning from web searches and article history
- **Web Interface**: FastAPI server with real-time flow execution and management

**Key Components:**
- `src/linkedin/` - Main CrewAI implementation
- `knowledge/` - File-based knowledge sources (JSONKnowledgeSource with relative paths)
- `www/` - Web interface for flow management
- `web_server.py` - FastAPI server with streaming execution

---

## ⚡ Critical Workflows

### Running CrewAI Flows
```bash
# Method 1: CrewAI CLI (preferred)
crewai run

# Method 2: Direct Python execution  
python -c "import sys; sys.path.append('src'); from linkedin.main import run; run()"

# Method 3: Web interface
.\start-web.ps1    # Start web server on localhost:8000
```

### Knowledge Management
```bash
# Reset knowledge data
python reset_knowledge.py --type all --stats

# Check topic coverage
python -c "from src.linkedin.helpers.knowledge_helper import KnowledgeHelper; print(KnowledgeHelper().check_topic_covered('AI trends'))"
```

---

## 🔧 CrewAI-Specific Patterns

### 1. YAML-Driven Configuration
- **Agents**: `src/linkedin/config/agents.yaml` - Roles, goals, LLM models
- **Tasks**: `src/linkedin/config/tasks.yaml` - Workflow steps, expected outputs
- **Dynamic Templating**: Use `{current_year}` in goals for current context

### 2. Local Ollama Integration  
- **LLM Helper**: `src/linkedin/helpers/llm_helper.py`
- **Base URL**: Always `http://localhost:11434`
- **Embedding Model**: `mxbai-embed-large` for knowledge sources
- **Thinking Control**: `model_kwargs["options"]["think"]` to disable verbosity

### 3. Knowledge Sources (Critical)
- **Location**: Files MUST be in `/knowledge` directory at project root
- **File Paths**: Use relative paths from knowledge directory (`"web_search_results.json"`)
- **Source Type**: JSONKnowledgeSource (not StringKnowledgeSource)
- **Embeddings**: Local Ollama embeddings configured to avoid OpenAI API errors

```python
# Correct Knowledge Source Pattern
knowledge_source = JSONKnowledgeSource(
    file_paths=["web_search_results.json"],  # Relative from /knowledge
    metadata={"source": "web_search_results", "type": "search_data"}
)
```

### 4. Web Interface Integration
- **Server**: `web_server.py` with FastAPI and streaming responses
- **Endpoints**: `/api/execute-flow`, `/api/knowledge/*`, `/api/stats`
- **Frontend**: Vanilla JS with real-time updates via Server-Sent Events
- **Startup**: Use `start-web.ps1` PowerShell script

---

## 🚨 Common Pitfalls & Solutions

**❌ "Knowledge Search Failed" Errors:**
- Cause: OpenAI API dependency in CrewAI knowledge system
- Fix: Use local Ollama embeddings in crew configuration

**❌ Import Errors:**
- Always add `sys.path.append('src')` before importing from linkedin module
- Use absolute imports: `from linkedin.main import run`

**❌ Model Memory Issues:**
- Use `llm_helper.force_cleanup_memory()` after crew execution
- Implement cleanup in `@after_kickoff` decorator

**❌ Knowledge File Paths:**
- Never use absolute paths for knowledge sources
- Always use relative paths from `/knowledge` directory

---

## 📁 File Structure Patterns

```
src/linkedin/
├── config/           # YAML configurations
├── helpers/          # Utility classes (knowledge, ollama, config)
├── tools/            # CrewAI custom tools (search)
├── flows/            # CrewAI flow definitions
├── crew.py           # Main crew class with @agent, @task decorators
└── main.py           # Entry point

knowledge/            # Knowledge sources (relative paths)
├── web_search_results.json
└── article_memory.json

www/                  # Web interface
├── index.html
└── assets/css/style.css
```

---

## 🔍 Debugging & Verification

**Check Knowledge System:**
```python
from linkedin.helpers.knowledge_helper import KnowledgeHelper
helper = KnowledgeHelper()
stats = helper.get_knowledge_stats()
```

**Verify Ollama Connection:**
```python
from linkedin.helpers.llm_helper import LLMHelper  
helper = LLMHelper()
models = helper.list_available_models()
```

**Test Crew Execution:**
- Expect: No "Knowledge Search Failed" errors
- Expect: Local embeddings working with Ollama
- Expect: Generated content in `/output` directory