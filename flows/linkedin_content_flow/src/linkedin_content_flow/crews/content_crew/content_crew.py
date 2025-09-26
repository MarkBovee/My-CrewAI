#!/usr/bin/env python
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import ScrapeWebsiteTool
from linkedin_content_flow.tools.search_tool import search_tool
from linkedin_content_flow.helpers.llm_helper import LLMHelper


@CrewBase
class ContentCrew:
    """LinkedIn Content Creation Crew
    
    A specialized crew for creating LinkedIn content including research articles,
    blog posts, and social media posts.
    """

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def __init__(self):
        super().__init__()
        self.llm_helper = LLMHelper()

    @agent
    def coach(self) -> Agent:
        """Senior Career Coach agent with search capabilities"""
        return Agent(
            config=self.agents_config['coach'],
            llm=self.llm_helper.create_llm_instance('coach'),
            tools=[search_tool],
            verbose=self.agents_config['coach'].get('verbose', False)
        )

    @agent
    def researcher(self) -> Agent:
        """Content Researcher agent for in-depth article research"""
        return Agent(
            config=self.agents_config['researcher'],
            llm=self.llm_helper.create_llm_instance('researcher'),
            tools=[search_tool, ScrapeWebsiteTool()],
            verbose=self.agents_config['researcher'].get('verbose', False)
        )

    @agent
    def writer(self) -> Agent:
        """Tech Thought Leadership Writer agent for blog content creation"""
        return Agent(
            config=self.agents_config['writer'],
            llm=self.llm_helper.create_llm_instance('writer'),
            tools=[search_tool, ScrapeWebsiteTool()],
            verbose=self.agents_config['writer'].get('verbose', False)
        )
        
    @agent
    def influencer(self) -> Agent:
        """LinkedIn Influencer Writer agent for content creation"""
        return Agent(
            config=self.agents_config['influencer'],
            llm=self.llm_helper.create_llm_instance('influencer'),
            verbose=self.agents_config['influencer'].get('verbose', False)
        )

    @task
    def search_trending_skills(self) -> Task:
        """Research task for finding trending skills"""
        return Task(
            config=self.tasks_config['task_search'],
            agent=self.coach()
        )

    @task
    def research_topic(self) -> Task:
        """In-depth research task for creating comprehensive content"""
        return Task(
            config=self.tasks_config['task_research'],
            agent=self.researcher(),
            context=[self.search_trending_skills()]
        )

    @task
    def write_blog_article(self) -> Task:
        """Blog creation task for thought leadership content"""
        return Task(
            config=self.tasks_config['task_blog'],
            agent=self.writer(),
            context=[self.research_topic()]
        )

    @task
    def create_linkedin_post(self) -> Task:
        """Content creation task for LinkedIn post"""
        return Task(
            config=self.tasks_config['task_post'],
            agent=self.influencer(),
            context=[self.write_blog_article()]
        )

    @crew
    def crew(self) -> Crew:
        """Creates the LinkedIn Content Creation Crew"""
        print("🚀 Starting LinkedIn Content Creation Crew")
        print("🔧 Using search_tool for information gathering")

        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            max_execution_time=None
        )