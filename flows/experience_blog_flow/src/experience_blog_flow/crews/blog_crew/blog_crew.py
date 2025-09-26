#!/usr/bin/env python
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import ScrapeWebsiteTool
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
    
    A specialized crew for transforming personal experiences into comprehensive
    blog posts with industry context and technical depth.
    """

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def __init__(self):
        super().__init__()
        self.llm_helper = LLMHelper()

    @agent
    def coach(self) -> Agent:
        """Senior Career Coach agent for analyzing experiences"""
        return Agent(
            config=self.agents_config['coach'],
            llm=self.llm_helper.create_llm_instance('coach'),
            tools=[search_tool],
            verbose=self.agents_config['coach'].get('verbose', False)
        )

    @agent
    def researcher(self) -> Agent:
        """Content Researcher agent for enhancing experiences with industry insights"""
        return Agent(
            config=self.agents_config['researcher'],
            llm=self.llm_helper.create_llm_instance('researcher'),
            tools=[search_tool, ScrapeWebsiteTool()],
            verbose=self.agents_config['researcher'].get('verbose', False)
        )

    @agent
    def writer(self) -> Agent:
        """Tech Writer agent for creating comprehensive blog posts"""
        return Agent(
            config=self.agents_config['writer'],
            llm=self.llm_helper.create_llm_instance('writer'),
            tools=[search_tool, ScrapeWebsiteTool()],
            verbose=self.agents_config['writer'].get('verbose', False)
        )

    @task
    def analyze_experience(self) -> Task:
        """Analyze the personal experience to extract key themes"""
        return Task(
            config=self.tasks_config['task_experience_analysis'],
            agent=self.coach()
        )

    @task
    def research_context(self) -> Task:
        """Research industry context to enhance the experience"""
        return Task(
            config=self.tasks_config['task_experience_research'],
            agent=self.researcher(),
            context=[self.analyze_experience()]
        )

    @task
    def write_blog_post(self) -> Task:
        """Create comprehensive blog post from experience and research"""
        return Task(
            config=self.tasks_config['task_experience_blog'],
            agent=self.writer(),
            context=[self.research_context()]
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Experience Blog Creation Crew"""
        print("🚀 Starting Experience Blog Creation Crew")
        print("🔧 Using enhanced research to transform personal experiences")

        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            max_execution_time=None
        )