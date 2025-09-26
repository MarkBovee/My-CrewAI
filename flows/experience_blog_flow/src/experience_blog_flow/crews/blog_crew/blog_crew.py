#!/usr/bin/env python
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import ScrapeWebsiteTool, FileReadTool, DirectoryReadTool
import sys
import os
from pathlib import Path

# Add project root to path for shared components
project_root = Path(__file__).parent.parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from tools.search_tool import search_tool
from helpers.llm_helper import LLMHelper


@CrewBase
class BlogCrew:
    """Experience Blog Creation Crew
    
    A simplified single-agent crew for transforming personal experiences 
    into comprehensive blog posts with research and context.
    """

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def __init__(self):
        super().__init__()
        self.llm_helper = LLMHelper()

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

    @task
    def create_blog_from_experience(self) -> Task:
        """Transform personal experience into a comprehensive blog post with research and context"""
        return Task(
            config=self.tasks_config['task_experience_blog'],
            agent=self.writer()
        )

    @crew
    def crew(self) -> Crew:
        """Creates the simplified Experience Blog Creation Crew"""
        print("🚀 Starting Simple Experience Blog Crew")
        print("✍️ Single writer agent with comprehensive tools")
        print("📝 Input: Experience Text → Output: Enhanced Blog Post")

        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            max_execution_time=None
        )