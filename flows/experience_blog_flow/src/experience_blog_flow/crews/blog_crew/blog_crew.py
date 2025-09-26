#!/usr/bin/env python
import sys
import os
from pathlib import Path

# FIRST: Set up paths before any imports that depend on them
current_file = Path(__file__)

# Find the actual project root by looking for pyproject.toml
def find_project_root(start_path):
    """Find project root by looking for pyproject.toml"""
    current_path = Path(start_path).resolve()
    while current_path.parent != current_path:  # Not at filesystem root
        if (current_path / 'pyproject.toml').exists():
            return current_path
        current_path = current_path.parent
    return None

project_root = find_project_root(current_file)
if project_root is None:
    # Fallback to relative path calculation
    project_root = current_file.parent.parent.parent.parent.parent.parent

# Add project root to path for shared components
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Now import everything
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import ScrapeWebsiteTool, FileReadTool, DirectoryReadTool

# Import tools and helpers (should work now with path set)
from tools.search_tool import search_tool
from helpers.llm_helper import LLMHelper


@CrewBase
class BlogCrew:
    """Experience Blog Creation Crew
    
    A simplified single-agent crew for transforming personal experiences 
    into comprehensive blog posts with research and context.
    """

    agents_config = "../../config/agents.yaml"
    tasks_config = "../../config/tasks.yaml"

    def __init__(self):
        super().__init__()
        # Set config path relative to the crew file location
        config_path = Path(__file__).parent.parent.parent / "config" / "agents.yaml"
        self.llm_helper = LLMHelper(str(config_path))

    @agent
    def writer(self) -> Agent:
        """Expert Blog Writer agent for creating comprehensive blog posts from personal experiences"""
        return Agent(
            config=self.agents_config['writer'],
            llm=self.llm_helper.create_llm_instance('writer'),
            tools=[
                search_tool,
                ScrapeWebsiteTool(),
                FileReadTool(),
                DirectoryReadTool()
            ],
            verbose=self.agents_config['writer'].get('verbose', True)
        )

    @agent 
    def blog_writer(self) -> Agent:
        """Long-form blog writer agent for polishing and expanding initial drafts"""
        return Agent(
            config=self.agents_config['blog_writer'],
            llm=self.llm_helper.create_llm_instance('blog_writer'),
            tools=[
                search_tool,
                ScrapeWebsiteTool(),
                FileReadTool(),
                DirectoryReadTool()
            ],
            verbose=self.agents_config['blog_writer'].get('verbose', True)
        )

    @task
    def create_blog_from_experience(self) -> Task:
        """Transform personal experience into a comprehensive blog post with research and context"""
        return Task(
            config=self.tasks_config['task_experience_blog'],
            agent=self.writer()
        )

    @task
    def rewrite_and_expand_blog_post(self) -> Task:
        """Polish and expand the initial blog draft into a publication-ready long-form article"""
        return Task(
            config=self.tasks_config['rewrite_and_expand_blog_post'],
            agent=self.blog_writer(),
            context=[self.create_blog_from_experience()]  # Depends on the first task
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Two-Stage Experience Blog Creation Crew"""
        print("🚀 Starting Two-Stage Experience Blog Crew")
        print("📝 Stage 1: Research Writer - Create initial blog with research and context")
        print("✨ Stage 2: Blog Writer - Expand and polish into publication-ready article")
        print("🎯 Input: Experience Text → Output: Polished Long-Form Blog Post")

        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            max_execution_time=None
        )