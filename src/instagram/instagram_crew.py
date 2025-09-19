from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task, before_kickoff, after_kickoff
from crewai.agents.agent_builder.base_agent import BaseAgent
from instagram.tools import DuckDuckGoSearchTool
from instagram.helpers import OllamaHelper
from typing import List
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class InstagramCrew():
    """Instagram crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # Ollama LLM configuration using helper
    def __init__(self):
        super().__init__()
        self.ollama_helper = OllamaHelper()

    @agent
    def coach(self) -> Agent:
        return Agent(
            config=self.agents_config['coach'], # type: ignore[index]
            tools=[DuckDuckGoSearchTool()],
            llm=self.ollama_helper.create_llm_instance('coach'),
            verbose=self.agents_config['coach'].get('verbose', False)
        )

    @agent
    def influencer(self) -> Agent:
        return Agent(
            config=self.agents_config['influencer'], # type: ignore[index]
            llm=self.ollama_helper.create_llm_instance('influencer'),
            verbose=self.agents_config['influencer'].get('verbose', False)
        )

    @agent
    def critic(self) -> Agent:
        return Agent(
            config=self.agents_config['critic'], # type: ignore[index]
            llm=self.ollama_helper.create_llm_instance('critic'),
            verbose=self.agents_config['critic'].get('verbose', False)
        )

    @task
    def task_search(self) -> Task:
        return Task(
            config=self.tasks_config['task_search'], # type: ignore[index]
        )

    @task
    def task_post(self) -> Task:
        return Task(
            config=self.tasks_config['task_post'], # type: ignore[index]
        )

    @task
    def task_critique(self) -> Task:
        return Task(
            config=self.tasks_config['task_critique'], # type: ignore[index]
        )

    # @before_kickoff
    # def before_kickoff_function(self, inputs):
    #     print(f"Before kickoff function with inputs: {inputs}")
    #     return inputs # You can return the inputs or modify them as needed

    # @after_kickoff
    # def after_kickoff_function(self, result):
    #     print(f"After kickoff function with result: {result}")
    #     return result # You can return the result or modify it as needed    

    @crew
    def crew(self) -> Crew:
        """Creates the InstagramCrew crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=[self.coach(), self.influencer(), self.critic()], # Specific agents for our use case
            tasks=[self.task_search(), self.task_post(), self.task_critique()], # Specific tasks for our use case
            process=Process.sequential,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
            verbose=True,
            max_execution_time=None
        )
