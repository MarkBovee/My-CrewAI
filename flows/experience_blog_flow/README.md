# Experience Blog Flow

A CrewAI-powered multi-agent system for transforming personal experiences into comprehensive blog posts with enhanced research and context.

## Overview

This flow uses specialized AI agents to enhance personal experiences:
- **Experience Analyst**: Analyzes and structures personal experiences
- **Research Agent**: Conducts targeted research to add context and depth
- **Blog Writer**: Creates engaging, comprehensive blog posts

## Usage

### Via CrewAI CLI (from project root)
```bash
cd flows/experience_blog_flow
crewai run
```

### Via Python
```python
from experience_blog_flow.main import ExperienceBlogFlow

flow = ExperienceBlogFlow()
result = flow.kickoff(inputs={
    "experience_text": "Your personal experience here..."
})
```

### Via Web Interface
Start the web server from the project root:
```bash
# From project root
python web_server.py
# or
.\start-web.ps1
```

Then navigate to http://localhost:8000 and select "Create Blog From Experience Flow".

## Configuration

The flow is configured via YAML files in `src/experience_blog_flow/config/`:
- `agents.yaml` - Agent definitions, roles, and LLM models
- `tasks.yaml` - Task workflow and expected outputs

## Output

Generated blog posts are saved to:
- `output/blogs/` - Enhanced blog posts with research and context

## Token Management

This flow is designed to handle token limits efficiently by:
- Using structured task decomposition
- Implementing memory cleanup between tasks
- Optimizing prompt lengths for target models

## Models

Uses local Ollama models:
- **Analysis**: qwen2.5:14b (for structured thinking)
- **Research**: llama3.1:8b (for web search and fact gathering)
- **Writing**: qwq:32b (for creative, engaging content)
- **Embeddings**: mxbai-embed-large

Ensure Ollama is running locally on port 11434.