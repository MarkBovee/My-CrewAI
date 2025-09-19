from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task, before_kickoff, after_kickoff
from crewai.agents.agent_builder.base_agent import BaseAgent
from .tools.search_tool import search_tool
from .helpers.ollama_helper import OllamaHelper
from typing import List

@CrewBase
class LinkedInCrew():
    """LinkedIn Content Creation Crew
    
    A multi-agent crew designed to research trending skills and create engaging 
    LinkedIn content following CrewAI best practices.
    """

    agents: List[BaseAgent]
    tasks: List[Task]

    # Configuration paths following CrewAI documentation patterns
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    def __init__(self):
        super().__init__()
        self.ollama_helper = OllamaHelper()

    @before_kickoff
    def prepare_inputs(self, inputs):
        """Prepare and validate inputs before crew execution"""
        # Add current year if not provided
        if 'current_year' not in inputs:
            import datetime
            inputs['current_year'] = datetime.datetime.now().year
        
        print(f"🚀 Starting LinkedIn crew with inputs: {inputs}")
        return inputs

    @after_kickoff
    def process_output(self, output):
        """Process output after crew execution"""
        print(f"✅ LinkedIn crew completed successfully!")
        print(f"📊 Token usage: {output.token_usage}")
        return output

    @agent
    def coach(self) -> Agent:
        """Senior Career Coach agent with search capabilities"""
        return Agent(
            config=self.agents_config['coach'], # type: ignore[index]
            llm=self.ollama_helper.create_llm_instance('coach'),
            tools=[search_tool],  # Use the tool directly, not call it
            verbose=self.agents_config['coach'].get('verbose', False)
        )

    @agent
    def influencer(self) -> Agent:
        """LinkedIn Influencer Writer agent for content creation"""
        return Agent(
            config=self.agents_config['influencer'], # type: ignore[index]
            llm=self.ollama_helper.create_llm_instance('influencer'),
            verbose=self.agents_config['influencer'].get('verbose', False)
        )

    @agent
    def researcher(self) -> Agent:
        """Content Researcher agent for in-depth article research"""
        return Agent(
            config=self.agents_config['researcher'], # type: ignore[index]
            llm=self.ollama_helper.create_llm_instance('researcher'),
            tools=[search_tool],  # Search tool for comprehensive research
            verbose=self.agents_config['researcher'].get('verbose', False)
        )

    @task
    def task_search(self) -> Task:
        """Research task for finding trending skills"""
        return Task(
            config=self.tasks_config['task_search'], # type: ignore[index]
            agent=self.coach()
        )

    @task
    def task_research(self) -> Task:
        """In-depth research task for creating comprehensive content"""
        return Task(
            config=self.tasks_config['task_research'], # type: ignore[index]
            agent=self.researcher(),
            context=[self.task_search()]  # Uses initial skill list as context
        )

    @task
    def task_post(self) -> Task:
        """Content creation task for LinkedIn post"""
        return Task(
            config=self.tasks_config['task_post'], # type: ignore[index]
            agent=self.influencer(),
            context=[self.task_research()]  # Now uses the in-depth research
        )

    @crew
    def crew(self) -> Crew:
        """Creates the LinkedIn Content Creation Crew following CrewAI best practices"""
        return Crew(
            agents=self.agents,  # Automatically collected by @agent decorator
            tasks=self.tasks,    # Automatically collected by @task decorator
            process=Process.sequential,
            verbose=True,
            max_execution_time=None,
            # Disable features that require OpenAI for now
            # memory=True,  # Enable memory for better context retention
            # cache=True,   # Enable caching for performance
            # planning=True,  # Enable planning feature
            # output_log_file="linkedin_crew_logs.json"  # Log execution details
        )
