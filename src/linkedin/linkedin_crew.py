from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task, before_kickoff, after_kickoff
from crewai.agents.agent_builder.base_agent import BaseAgent
from .tools.search_tool import search_tool
from .helpers.ollama_helper import LLMHelper
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
        """Process the crew output (summary-only).

        NOTE: File persistence is handled by flows (e.g. `CreateNewPostFlow`).
        The crew should not write files directly to avoid duplicate outputs.
        This hook now collects a concise summary of task outputs and attaches
        it to the `result` object under `outputs_summary` for downstream
        flows or callers to persist if desired.
        """

        from datetime import datetime

        try:
            print("\n" + "=" * 60)
            print("📄 PROCESSING CREW OUTPUT (SUMMARY ONLY)")
            print("=" * 60)

            outputs_summary = []

            if hasattr(result, 'tasks_output') and result.tasks_output:
                tasks_output = result.tasks_output
                print(f"✅ Found {len(tasks_output)} task outputs")

                # Collect lightweight summaries for each task output
                for idx, task_out in enumerate(tasks_output):
                    try:
                        # Prefer raw attribute, fall back to str()
                        content = task_out.raw if hasattr(task_out, 'raw') else str(task_out)
                    except Exception:
                        content = str(task_out)

                    preview = content[:800].strip()  # keep previews short
                    outputs_summary.append({
                        'index': idx,
                        'preview': preview,
                        'length': len(content)
                    })

                # Attach summary and metadata to the result for flows to persist
                try:
                    setattr(result, 'outputs_summary', outputs_summary)
                    setattr(result, 'outputs_summary_generated_at', datetime.now().isoformat())
                except Exception:
                    # If result is not mutable, simply print the summary
                    print("ℹ️ Could not attach outputs_summary to result object; printing summary instead.")
                    for s in outputs_summary:
                        print(f" - Task {s['index']}: {s['length']} chars")

                print("🔁 NOTE: Crew no longer writes files. Use the flow to persist outputs.")

            else:
                print("⚠️  No task outputs found in crew result")

        except Exception as e:
            print(f"❌ Error in process_output (summary): {str(e)}")
            import traceback
            traceback.print_exc()

        # Final cleanup (models/memory)
        try:
            print("🧹 Cleaning up models...")
            cleanup_success = self.llm_helper.force_cleanup_memory()
            if cleanup_success:
                print("✅ Model cleanup completed successfully!")
            else:
                print("⚠️ Model cleanup partially successful")
        except Exception as cleanup_e:
            print(f"⚠️ Warning: Could not complete model cleanup: {cleanup_e}")

        return result

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
            tools=[search_tool],  # Add search tool for additional research during writing
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
            knowledge_sources=knowledge_sources  # File-based knowledge without embeddings
            # Note: Using StringKnowledgeSource to avoid embedding requirements
            # memory=True,  # Enable memory for better context retention
            # cache=True,   # Enable caching for performance 
            # planning=True,  # Enable planning feature
            # output_log_file="linkedin_crew_logs.json"  # Log execution details
        )
