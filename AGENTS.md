# AI Agent Instructions

This is a CrewAI multi-agent system.

This project uses CrewAI framework to create a multi-agent system for generating themed videos with AI agents.

## Always Follow These Instructions
0. **Take time to plan before coding**
1. **Read the entire `AGENTS.md` file before starting any work.**
2. **Strictly adhere to all mandatory requirements and guidelines outlined below.**
3. **Do not deviate from the specified patterns, structures, or workflows. If you identify a need for change, document it and seek approval before proceeding.**
4. **Ensure all code is clean, well-documented, and production-ready.**
5. **Maintain clear progress documentation in `.github/copilot-progress.md`.**
6. **Clean up all unused or redundant code files after completing tasks to keep the project organized.**

## 📋 Progress Tracking & Documentation (Required)

### Development Session Management
When working on development tasks, especially complex implementations or multi-step processes:

1. **Always check for existing progress**: Start by checking if the `.github/copilot-progress.md` file exists. If not, create it. Then read it to understand any ongoing work or previous session context.

2. **Maintain progress documentation**: Update the progress file throughout your session with:
   - Current status and completed steps
   - Technical decisions and implementation details
   - Issues encountered and solutions applied
   - Next steps and remaining work

3. **🚨 REQUIRED SESSION CLEANUP**: When completing a task or major milestone:
   - **MANDATORY**: Clean up and organize script files by removing redundant/obsolete versions
   - **MANDATORY**: Update progress documentation with "Task Completed Successfully" section
   - **MANDATORY**: Document critical technical findings (like AutoGen compatibility issues)
   - **MANDATORY**: Include implementation details, key features delivered, and technical approaches
   - Note any follow-up actions needed for production

4. **Start of a new task (housekeeping)**:
   - If the previous task was completed successfully and the new task is unrelated, reset `.github/copilot-progress.md` so it contains only the new task’s progress. Do not keep prior task logs in this file.
   - If the new task is a direct continuation of the previous one, keep the same task entry and append progress under the existing header.
   - Optionally archive prior completed task notes elsewhere (e.g., a dated entry in a separate document) if historical context is needed, but keep `copilot-progress.md` focused on a single active task.

### Progress File Structure
The `.github/copilot-progress.md` should follow this pattern:
- **Header**: Task name, date, and completion status
- **Summary**: Brief overview of accomplishments (for completed tasks)
- **Detailed Steps**: Numbered list of completed work with checkmarks
- **Implementation Details**: Technical specifics, file changes, patterns used
- **Testing/Verification**: Test results, compilation status, validation steps
- **Next Steps**: Future work or production deployment notes

This approach ensures continuity between development sessions and provides clear documentation of progress for complex implementations.

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

## Critical Development Workflows

### Running the Crew
```bash
# Method 1: CrewAI CLI (preferred)
crewai run

# Method 2: Direct Python execution
python -c "import sys; sys.path.append('src'); from instagram.main import run; run()"
```

## Concepts & Documentation

The following resources are available, read them to understand CrewAI concepts:

- [Official CrewAI Documentation](https://docs.crewai.com)
- [Agents Documentation](https://docs.crewai.com/en/concepts/agents)
- [Tasks Documentation](https://docs.crewai.com/en/concepts/tasks)  
- [Crews Documentation](https://docs.crewai.com/en/concepts/crews)
- [Tools Documentation](https://docs.crewai.com/en/concepts/tools)
- [Knowledge Documentation](https://docs.crewai.com/en/concepts/knowledge)
- [Collaboration Documentation](https://docs.crewai.com/en/concepts/collaboration)
- [Flows Documentation](https://docs.crewai.com/en/concepts/flows)
- [Event Listener Documentation](https://docs.crewai.com/en/concepts/event-listener)