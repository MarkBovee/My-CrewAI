from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task, before_kickoff, after_kickoff
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai_tools import FileReadTool, ScrapeWebsiteTool, CodeInterpreterTool, DirectoryReadTool
from .tools.search_tool import search_tool
from .helpers.llm_helper import LLMHelper
from .helpers.knowledge_helper import KnowledgeHelper, check_topic_similarity, store_article_completion
from typing import List
import warnings
import inspect

@CrewBase
class LinkedInCrew():
    """LinkedIn Content Creation Crew
    
    A multi-agent crew designed to research trending skills and create engaging 
    LinkedIn content following CrewAI best practices.
    
    IMPORTANT: Direct crew execution is deprecated. Use CreateNewPostFlow instead.
    """

    agents: List[BaseAgent]
    tasks: List[Task]

    # Configuration paths following CrewAI documentation patterns
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    def __init__(self):
        super().__init__()
        self.llm_helper = LLMHelper()
        self.knowledge_helper = KnowledgeHelper()
        self._flow_execution = False  # Track if executed via flow

    def _enable_flow_execution(self):
        """Enable flow execution mode (called by flows)"""
        self._flow_execution = True

    def _check_execution_mode(self):
        """Check if this is being called directly (not via flow)"""
        frame = inspect.currentframe()
        try:
            # Get caller information
            caller_frame = frame.f_back.f_back  # Go back two frames
            caller_filename = caller_frame.f_code.co_filename
            caller_function = caller_frame.f_code.co_name
            
            # Check if caller is a flow or approved execution method
            is_flow_execution = (
                'flow' in caller_filename.lower() or 
                caller_function in ['generate_content', 'run_via_flow'] or
                self._flow_execution
            )
            
            if not is_flow_execution:
                warnings.warn(
                    "Direct crew execution is deprecated. Use CreateNewPostFlow for proper execution.",
                    DeprecationWarning,
                    stacklevel=3
                )
                print("\n⚠️  SAFEGUARD WARNING: Direct crew execution detected!")
                print("✅ Recommended: Use CreateNewPostFlow for proper execution:")
                print("   from src.linkedin.flows.create_new_post_flow import CreateNewPostFlow")
                print("   flow = CreateNewPostFlow()")
                print("   flow.state.topic = 'your topic'")
                print("   result = flow.kickoff()")
                print("")
                
                # Allow execution but with warning
                print("🔄 Proceeding with direct execution (not recommended)...\n")
        
        finally:
            del frame

    @before_kickoff
    def prepare_inputs(self, inputs):
        """Prepare and validate inputs before crew execution"""
        # Add current year if not provided
        if 'current_year' not in inputs:
            import datetime
            inputs['current_year'] = datetime.datetime.now().year
        
        # Check if topic has been covered before
        topic = inputs.get('topic', 'general tech topic')
        coverage_check = check_topic_similarity(topic)
        
        print(f"🚀 Starting LinkedIn crew with inputs: {inputs}")
        print(f"📚 Topic coverage check: {coverage_check['recommendation']}")
        
        if coverage_check['covered'] and coverage_check['similar_articles']:
            print("⚠️ Similar topics found:")
            for article in coverage_check['similar_articles']:
                print(f"  - {article['topic']} (similarity: {article['similarity']})")
        
        return inputs

    @after_kickoff
    def process_output(self, result):
        """Process the crew output - attach task outputs to result for flow persistence"""
        from datetime import datetime

        try:
            # Attach task outputs to result for flow to access
            if hasattr(result, 'tasks_output') and result.tasks_output:
                setattr(result, 'outputs_summary_generated_at', datetime.now().isoformat())
        except Exception:
            pass  # Silently handle any issues

        # Cleanup memory
        try:
            self.llm_helper.force_cleanup_memory()
        except Exception:
            pass  # Silently handle cleanup issues

        return result

    @agent
    def coach(self) -> Agent:
        """Senior Career Coach agent with search capabilities"""
        return Agent(
            config=self.agents_config['coach'], # type: ignore[index]
            llm=self.llm_helper.create_llm_instance('coach'),
            tools=[search_tool],  # Search capabilities for career research
            verbose=self.agents_config['coach'].get('verbose', False)
        )

    @agent
    def researcher(self) -> Agent:
        """Content Researcher agent for in-depth article research"""
        return Agent(
            config=self.agents_config['researcher'], # type: ignore[index]
            llm=self.llm_helper.create_llm_instance('researcher'),
            tools=[search_tool, ScrapeWebsiteTool()],  # Web search and scraping for research
            verbose=self.agents_config['researcher'].get('verbose', False)
        )

    @agent
    def writer(self) -> Agent:
        """Tech Thought Leadership Writer agent for blog content creation"""
        return Agent(
            config=self.agents_config['writer'], # type: ignore[index]
            llm=self.llm_helper.create_llm_instance('writer'),
            tools=[search_tool, ScrapeWebsiteTool()],  # Search capabilities for additional research
            verbose=self.agents_config['writer'].get('verbose', False)
        )
        
    @agent
    def influencer(self) -> Agent:
        """LinkedIn Influencer Writer agent for content creation"""
        return Agent(
            config=self.agents_config['influencer'], # type: ignore[index]
            llm=self.llm_helper.create_llm_instance('influencer'),
            verbose=self.agents_config['influencer'].get('verbose', False)
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
    def task_blog(self) -> Task:
        """Blog creation task for thought leadership content"""
        return Task(
            config=self.tasks_config['task_blog'], # type: ignore[index]
            agent=self.writer(),  # Use the dedicated writer agent
            context=[self.task_research()]  # Uses the in-depth research
        )

    @task
    def task_post(self) -> Task:
        """Content creation task for LinkedIn post"""
        return Task(
            config=self.tasks_config['task_post'], # type: ignore[index]
            agent=self.influencer(),
            context=[self.task_blog()]  # Now correctly uses the blog content
        )

    @crew
    def crew(self) -> Crew:
        """Creates the LinkedIn Content Creation Crew following CrewAI best practices"""
        
        # Execute safeguard check
        self._check_execution_mode()
        
        # CLEAN SOLUTION: Avoid knowledge_sources entirely to prevent API errors
        # Instead, agents will access data through search_tool which reads the same files
        print("📚 Knowledge data accessible via search_tool (no API required)")
        print("🔍 Agents can search web_search_results.json and article_memory.json directly")
        
        return Crew(
            agents=self.agents,  # Automatically collected by @agent decorator
            tasks=self.tasks,    # Automatically collected by @task decorator
            process=Process.sequential,
            verbose=True,
            max_execution_time=None
            # Note: No knowledge_sources to avoid any embedding/API requirements
            # All data accessible via search_tool which reads the same JSON files
            # memory=True,  # Enable memory for better context retention
            # cache=True,   # Enable caching for performance 
            # planning=True,  # Enable planning feature
            # output_log_file="crew_logs.json"  # Log execution details
        )
