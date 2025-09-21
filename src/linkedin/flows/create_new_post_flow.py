"""
Create New Post Flow using CrewAI Flow Architecture
Generates social media posts using multi-agent collaboration
"""

import os
import tempfile
from datetime import datetime
from pydantic import BaseModel
from crewai.flow.flow import Flow, listen, start
from crewai import Crew

from src.linkedin.crew import LinkedInCrew


class PostState(BaseModel):
    """State model for social media post generation flow"""
    topic: str = ""
    research_results: str = ""
    draft_post: str = ""
    final_post: str = ""
    output_files: dict = {}  # Store paths to all generated files
    temp_dir: str = ""  # Temporary directory for intermediate files
    intermediate_files: dict = {}  # Store paths to intermediate task outputs


class CreateNewPostFlow(Flow[PostState]):
    """
    CrewAI Flow for generating social media posts using multi-agent collaboration
    """

    def __init__(self):
        super().__init__()
        self.crew_instance = LinkedInCrew()

    @start()
    def initialize_topic(self):
        """Initialize the flow with a topic for social media post generation"""
        print("🚀 Starting Create New Post Flow")
        print(f"📋 Topic: {self.state.topic}")
        print("=" * 60)
        
        # Create temporary directory for intermediate files to reduce memory usage
        self.state.temp_dir = tempfile.mkdtemp(prefix="crewai_flow_")
        self.state.intermediate_files = {}
        
        print(f"📁 Created temporary directory: {self.state.temp_dir}")
        
        # Return the topic to trigger the next step
        return {"topic": self.state.topic}

    @listen(initialize_topic)
    def generate_content(self, topic_data):
        """Generate social media content using the CrewAI crew"""
        print(f"📝 Generating social media content for: {topic_data['topic']}")
        
        # Enable flow execution mode in the crew
        self.crew_instance._enable_flow_execution()
        
        # Get the crew and execute it
        crew = self.crew_instance.crew()
        
        # Execute the crew with the topic and current year
        current_year = datetime.now().year
        result = crew.kickoff(inputs={
            "topic": topic_data["topic"],
            "current_year": current_year
        })
        
        # Extract and save task outputs to intermediate files to reduce memory usage
        task_outputs = {}
        if hasattr(result, 'tasks_output') and result.tasks_output:
            for idx, task_out in enumerate(result.tasks_output):
                try:
                    content = task_out.raw if hasattr(task_out, 'raw') else str(task_out)
                    
                    # Save intermediate content to file to reduce memory usage
                    temp_file = os.path.join(self.state.temp_dir, f"task_{idx}_output.txt")
                    with open(temp_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    # Store file path instead of content
                    task_outputs[idx] = temp_file
                    self.state.intermediate_files[f"task_{idx}"] = temp_file
                    
                    print(f"💾 Saved task {idx} output to: {temp_file}")
                    
                except Exception as e:
                    print(f"⚠️ Warning: Could not save task {idx} output: {e}")
                    task_outputs[idx] = str(task_out)
        
        # Store final post content
        self.state.final_post = result.raw if hasattr(result, 'raw') else str(result)
        
        print("✅ Content generation completed!")
        print(f"📊 Saved {len(task_outputs)} intermediate task outputs to disk")
        
        return {
            "content": self.state.final_post,
            "task_outputs": task_outputs
        }

    @listen(generate_content)
    def save_all_content(self, content_data):
        """Save all generated content to appropriate files"""
        print("💾 Saving all generated content to files...")
        
        # Create output directories if they don't exist
        os.makedirs("output/articles", exist_ok=True)
        os.makedirs("output/blogs", exist_ok=True)
        os.makedirs("output/posts", exist_ok=True)
        
        # Generate timestamp and safe topic name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        topic_safe = self.state.topic.replace(" ", "_").replace("/", "_")
        
        # File paths
        research_file = f"output/articles/research_article_{topic_safe}_{timestamp}.md"
        blog_file = f"output/blogs/blog_post_{topic_safe}_{timestamp}.md"
        linkedin_file = f"output/posts/linkedin_post_{topic_safe}_{timestamp}.md"
        
        # Extract content from task outputs
        task_outputs = content_data.get('task_outputs', {})
        
        # Task 0: Coach search results
        # Task 1: Researcher article  
        # Task 2: Writer blog post
        # Task 3: Influencer LinkedIn post
        
        research_content = task_outputs.get(1, "No research content available")
        blog_content = task_outputs.get(2, "No blog content available") 
        linkedin_content = task_outputs.get(3, content_data['content'])
        
        # Save research article
        research_md = f"""# Research Article: {self.state.topic}

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Topic:** {self.state.topic}  
**Type:** Comprehensive Research Article

---

{research_content}

---

*Generated by CrewAI Expert Technical Researcher & Analyst*
"""
        
        with open(research_file, 'w', encoding='utf-8') as f:
            f.write(research_md)
        
        # Save blog post
        blog_md = f"""# Blog Post: {self.state.topic}

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Topic:** {self.state.topic}  
**Type:** Tech Thought Leadership Blog Post

---

{blog_content}

---

*Generated by CrewAI Tech Thought Leadership Writer*
"""
        
        with open(blog_file, 'w', encoding='utf-8') as f:
            f.write(blog_md)
        
        # Save LinkedIn post
        linkedin_md = f"""# LinkedIn Post: {self.state.topic}

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Topic:** {self.state.topic}  
**Type:** LinkedIn Social Media Post

---

{linkedin_content}

---

*Generated by CrewAI LinkedIn Influencer Writer*
"""
        
        with open(linkedin_file, 'w', encoding='utf-8') as f:
            f.write(linkedin_md)
        
        # Store file paths in state
        self.state.output_files = {
            "research": research_file,
            "blog": blog_file,
            "linkedin": linkedin_file
        }
        
        # Store the final LinkedIn post content
        self.state.final_post = linkedin_content
        
        print(f"✅ All files saved successfully!")
        print(f"📊 Research Article: {len(research_content)} chars")
        print(f"📝 Blog Post: {len(blog_content)} chars") 
        print(f"📱 LinkedIn Post: {len(linkedin_content)} chars")
        
        return {
            "files": self.state.output_files,
            "linkedin_content": self.state.final_post
        }

    @listen(save_all_content)
    def flow_complete(self, result_data):
        """Final step to display completion status and cleanup"""
        print("\n" + "=" * 60)
        print("🎉 CREATE NEW POST FLOW COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print(f"� Topic: {self.state.topic}")
        
        print(f"\n📁 GENERATED FILES:")
        print(f"📊 Research Article: {result_data['files']['research']}")
        print(f"📝 Blog Post: {result_data['files']['blog']}")
        print(f"📱 LinkedIn Post: {result_data['files']['linkedin']}")
        
        print("\n📱 LINKEDIN CONTENT PREVIEW:")
        print("-" * 40)
        print(result_data['linkedin_content'])
        print("-" * 40)
        
        # Clean up temporary files to free memory
        try:
            import shutil
            if self.state.temp_dir and os.path.exists(self.state.temp_dir):
                shutil.rmtree(self.state.temp_dir)
                print(f"🧹 Cleaned up temporary directory: {self.state.temp_dir}")
        except Exception as e:
            print(f"⚠️ Warning: Could not clean up temporary directory: {e}")
        
        # Memory optimization: Clean up LLM models after flow completion
        try:
            from src.linkedin.helpers.llm_helper import LLMHelper
            llm_helper = LLMHelper()
            cleanup_success = llm_helper.force_cleanup_memory()
            if cleanup_success:
                print("🧠 LLM memory cleanup completed - GPU memory freed!")
            else:
                print("⚠️ LLM memory cleanup completed with warnings")
        except Exception as e:
            print(f"⚠️ Could not perform LLM memory cleanup: {e}")
        
        print(f"\n🎯 FLOW COMPLETED SUCCESSFULLY!")
        print(f"💼 All content ready in output/ directories")
        print(f"🧠 Memory optimized: intermediate files and LLM models cleaned up")
        
        return result_data
        return self.state.final_post


def run_create_new_post_flow(topic: str = "Latest AI, Software Development"):
    """
    Run the Create New Post Flow with a specified topic - simplified version that avoids async issues
    
    Args:
        topic (str): The topic for social media post generation
    """
    print("🎬 Starting CrewAI Create New Post Generation Flow")
    print(f"📋 Topic: {topic}")
    print("=" * 60)
    
    # Memory optimization: Clean up any loaded models before starting
    print("🧠 Optimizing memory before flow execution...")
    try:
        from src.linkedin.helpers.llm_helper import LLMHelper
        llm_helper = LLMHelper()
        cleanup_success = llm_helper.force_cleanup_memory()
        if cleanup_success:
            print("✅ Memory cleanup completed - GPU memory freed!")
        else:
            print("⚠️ Memory cleanup completed with warnings")
    except Exception as e:
        print(f"⚠️ Could not perform memory cleanup: {e}")
    
    # Initialize and run the Flow
    flow = CreateNewPostFlow()
    
    print("🚀 Executing Flow...")
    result = flow.kickoff(inputs={"topic": topic})
    
    print("✅ Flow execution completed!")
    return result


if __name__ == "__main__":
    # Run the flow
    run_create_new_post_flow()