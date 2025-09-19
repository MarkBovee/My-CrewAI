from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task, before_kickoff, after_kickoff
from crewai.agents.agent_builder.base_agent import BaseAgent
from .tools.search_tool import search_tool
from .helpers.llm_helper import LLMHelper
from .helpers.knowledge_helper import KnowledgeHelper, check_topic_similarity, store_article_completion
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
        self.llm_helper = LLMHelper()
        self.knowledge_helper = KnowledgeHelper()

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
    def process_output(self, output):
        """Process output after crew execution and save to files"""
        import os
        from datetime import datetime
        
        print(f"✅ LinkedIn crew completed successfully!")
        print(f"📊 Token usage: {output.token_usage}")
        
        # Extract topic from output for knowledge storage
        try:
            # Try to extract topic from the crew output
            topic = "Generated Content"  # Default fallback
            if hasattr(output, 'raw') and output.raw:
                # Try to extract topic from the content
                content_lines = str(output.raw).split('\n')
                for line in content_lines:
                    if 'topic' in line.lower() or 'subject' in line.lower():
                        topic = line.strip()
                        break
            
            # Store article completion in knowledge system
            output_dir = os.path.join(os.path.dirname(__file__), "..", "..", "output")
            article_files = []
            post_files = []
            
            # Find generated files
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    if file.endswith('.md'):
                        file_path = os.path.join(root, file)
                        if 'article' in file.lower():
                            article_files.append(file_path)
                        elif 'post' in file.lower():
                            post_files.append(file_path)
            
            # Store memory for the most recent files
            if article_files:
                article_path = max(article_files, key=os.path.getctime)  # Most recent
                post_path = max(post_files, key=os.path.getctime) if post_files else ""
                
                store_article_completion(topic, article_path, post_path)
                print(f"📖 Stored article completion in knowledge system")
            
            # Cleanup models after completion
            print("🧹 Cleaning up models...")
            cleanup_success = self.llm_helper.force_cleanup_memory()
            if cleanup_success:
                print("✅ Model cleanup completed successfully!")
            else:
                print("⚠️ Model cleanup partially successful")
                
        except Exception as e:
            print(f"⚠️ Warning: Could not complete post-processing: {e}")
        
        return output

    @agent
    def coach(self) -> Agent:
        """Senior Career Coach agent with search capabilities"""
        return Agent(
            config=self.agents_config['coach'], # type: ignore[index]
            llm=self.llm_helper.create_llm_instance('coach'),
            tools=[search_tool],  # Use the tool directly, not call it
            verbose=self.agents_config['coach'].get('verbose', False)
        )

    @agent
    def influencer(self) -> Agent:
        """LinkedIn Influencer Writer agent for content creation"""
        return Agent(
            config=self.agents_config['influencer'], # type: ignore[index]
            llm=self.llm_helper.create_llm_instance('influencer'),
            verbose=self.agents_config['influencer'].get('verbose', False)
        )

    @agent
    def researcher(self) -> Agent:
        """Content Researcher agent for in-depth article research"""
        return Agent(
            config=self.agents_config['researcher'], # type: ignore[index]
            llm=self.llm_helper.create_llm_instance('researcher'),
            tools=[search_tool],  # Search tool for comprehensive research
            verbose=self.agents_config['researcher'].get('verbose', False)
        )

    @agent
    def writer(self) -> Agent:
        """Tech Thought Leadership Writer agent for blog content creation"""
        return Agent(
            config=self.agents_config['writer'], # type: ignore[index]
            llm=self.llm_helper.create_llm_instance('writer'),
            verbose=self.agents_config['writer'].get('verbose', False)
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
        # Create knowledge sources for the crew using proper file-based sources
        knowledge_sources = []
        
        try:
            # Add web search results knowledge using JSONKnowledgeSource with relative path
            web_knowledge = self.knowledge_helper.get_web_results_knowledge_source()
            knowledge_sources.append(web_knowledge)
            print("📚 Added web search results to crew knowledge")
            
            # Add article memory knowledge using JSONKnowledgeSource with relative path
            article_knowledge = self.knowledge_helper.get_article_memory_knowledge_source()
            knowledge_sources.append(article_knowledge)
            print("📖 Added article memory to crew knowledge")
            
        except Exception as e:
            print(f"⚠️ Warning: Could not load all knowledge sources: {e}")
            print("🔄 Continuing with crew execution without knowledge sources")
        
        return Crew(
            agents=self.agents,  # Automatically collected by @agent decorator
            tasks=self.tasks,    # Automatically collected by @task decorator
            process=Process.sequential,
            verbose=True,
            max_execution_time=None,
            knowledge_sources=knowledge_sources,  # Re-enabled with proper configuration
            # Configure local Ollama embeddings to avoid OpenAI API dependency
            embedder={
                "provider": "ollama",
                "config": {
                    "model": "mxbai-embed-large",  # Local embedding model
                    "base_url": "http://localhost:11434"  # Local Ollama server
                }
            }
            # Note: Removed other OpenAI-dependent features for now
            # memory=True,  # Enable memory for better context retention
            # cache=True,   # Enable caching for performance 
            # planning=True,  # Enable planning feature
            # output_log_file="linkedin_crew_logs.json"  # Log execution details
        )
