# LinkedIn Content Flow

A CrewAI-powered multi-agent system for generating LinkedIn content including research articles, blog posts, and social media posts.

## Overview

This flow uses a coordinated team of AI agents:
- **Coach**: Guides the overall content strategy and quality
- **Researcher**: Conducts web research and gathers information  
- **Writer**: Creates comprehensive articles and blog posts
- **Influencer**: Generates engaging social media posts

## Usage

### Via CrewAI CLI (from project root)
```bash
cd flows/linkedin_content_flow
crewai run
```

### Via Python
```python
from linkedin_content_flow.main import LinkedInContentFlow

flow = LinkedInContentFlow()
result = flow.kickoff(inputs={"topic": "AI trends in 2024"})
```

### Via Web Interface
Start the web server from the project root:
```bash
# From project root
python web_server.py
# or
.\start-web.ps1
```

Then navigate to http://localhost:8000 and select "Create New Post Flow".

## Configuration

The flow is configured via YAML files in `src/linkedin_content_flow/config/`:
- `agents.yaml` - Agent definitions, roles, and LLM models
- `tasks.yaml` - Task workflow and expected outputs

## Output

Generated content is saved to the project root `output/` directory:
- `output/articles/` - Research articles
- `output/blogs/` - Blog posts  
- `output/posts/` - LinkedIn posts

## Knowledge System

The flow maintains persistent knowledge using:
- Web search results stored in `/knowledge/web_search_results.json`
- Article memory to avoid duplicate topics in `/knowledge/article_memory.json`
- Local Ollama embeddings for similarity matching

## Models

Uses local Ollama models:
- **Text Generation**: llama3.1:8b, qwen2.5:14b
- **Embeddings**: mxbai-embed-large
- **Reasoning**: qwq:32b (for complex analysis)

Ensure Ollama is running locally on port 11434.