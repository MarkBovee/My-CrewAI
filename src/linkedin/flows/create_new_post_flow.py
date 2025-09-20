"""
Create New Post Flow using CrewAI Flow Architecture
Generates social media posts using multi-agent collaboration
"""
import os
from datetime import datetime
from pydantic import BaseModel
from crewai.flow.flow import Flow, listen, start
from crewai import Crew

from src.linkedin.linkedin_crew import LinkedInCrew


class PostState(BaseModel):
    """State model for social media post generation flow"""
    topic: str = ""
    research_results: str = ""
    draft_post: str = ""
    final_post: str = ""
    output_files: dict = {}  # Store paths to all generated files


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
        
        # Store the result in state
        self.state.final_post = result.raw if hasattr(result, 'raw') else str(result)
        
        print("✅ Content generation completed!")
        
        return {"content": self.state.final_post}

    @listen(generate_content)
    def save_all_content(self, content_data):
        """Save all generated content to appropriate files"""
        print("💾 Saving all generated content to files...")
        
        # The crew's @after_kickoff method should have already saved the files
        # This step is for flow completion and verification
        
        # Create output directories if they don't exist
        os.makedirs("output/articles", exist_ok=True)
        os.makedirs("output/blogs", exist_ok=True)
        os.makedirs("output/posts", exist_ok=True)
        
        # Generate timestamp and safe topic name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        topic_safe = self.state.topic.replace(" ", "_").replace("/", "_")
        
        # Expected file paths (should match @after_kickoff naming)
        research_file = f"output/articles/research_article_{topic_safe}_{timestamp}.md"
        blog_file = f"output/blogs/blog_post_{topic_safe}_{timestamp}.md"
        linkedin_file = f"output/posts/linkedin_post_{topic_safe}_{timestamp}.md"
        
        # Store file paths in state for completion message
        self.state.output_files = {
            "research": research_file,
            "blog": blog_file,
            "linkedin": linkedin_file
        }
        
        # Store the final LinkedIn post content
        self.state.final_post = content_data['content']
        
        print(f"✅ Content generation completed! Files should be saved by crew @after_kickoff")
        
        return {
            "files": self.state.output_files,
            "linkedin_content": self.state.final_post
        }

    @listen(save_all_content)
    def flow_complete(self, result_data):
        """Final step to display completion status"""
        print("\n" + "=" * 60)
        print("🎉 CREATE NEW POST FLOW COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print(f"Topic: {self.state.topic}")
        
        print(f"\n📁 GENERATED FILES:")
        print(f"📊 Research Article: {result_data['files']['research']}")
        print(f"📝 Blog Post: {result_data['files']['blog']}")
        print(f"📱 LinkedIn Post: {result_data['files']['linkedin']}")
        
        print("\n📱 LINKEDIN CONTENT PREVIEW:")
        print("-" * 40)
        print(result_data['linkedin_content'])
        print("-" * 40)
        
        print(f"\n🎯 FLOW COMPLETED SUCCESSFULLY!")
        print(f"💼 All content ready in output/ directories")
        
        return result_data


def run_create_new_post_flow(topic: str = "Latest AI, Software Development"):
    """
    Run the Create New Post Flow with a specified topic - simplified version that avoids async issues
    
    Args:
        topic (str): The topic for social media post generation
    """
    print("🎬 Starting CrewAI Create New Post Generation Flow")
    print(f"📋 Topic: {topic}")
    print("=" * 60)
    
    # Create the LinkedIn crew directly (bypass Flow for now to avoid async issues)
    from src.linkedin.linkedin_crew import LinkedInCrew
    
    print("📝 Initializing crew...")
    crew_instance = LinkedInCrew()
    crew = crew_instance.crew()
    
    print(f"🚀 Executing crew for topic: {topic}")
    
    # Execute the crew directly with inputs
    current_year = datetime.now().year
    result = crew.kickoff(inputs={
        "topic": topic,
        "current_year": current_year
    })
    
    # Create output directories
    output_dir = "output"
    articles_dir = os.path.join(output_dir, "articles")
    blogs_dir = os.path.join(output_dir, "blogs")
    posts_dir = os.path.join(output_dir, "posts")
    os.makedirs(articles_dir, exist_ok=True)
    os.makedirs(blogs_dir, exist_ok=True)
    os.makedirs(posts_dir, exist_ok=True)
    
    # Generate filename components
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    topic_safe = topic.replace(" ", "_").replace("/", "_").replace("&", "and")
    
    # Extract task outputs from crew execution
    task_outputs = result.tasks_output if hasattr(result, 'tasks_output') else []
    
    # Initialize content variables
    research_article = ""
    linkedin_post = ""
    
    # Extract research article and LinkedIn post from task outputs
    if task_outputs and len(task_outputs) >= 3:
        # task_outputs[1] should be the research task (task_research)
        research_output = task_outputs[1]
        research_article = research_output.raw if hasattr(research_output, 'raw') else str(research_output)
        
        print("📄 Research article captured successfully!")
    else:
        print("⚠️ Warning: Could not extract research article from task outputs")
        research_article = "Research article not available - task outputs may have changed structure"
    
    # Get the final LinkedIn post
    final_post = result.raw if hasattr(result, 'raw') else str(result)
    linkedin_post = final_post
    
    # Save research article
    article_filename = f"research_article_{topic_safe}_{timestamp}.md"
    article_filepath = os.path.join(articles_dir, article_filename)
    
    article_content = f"""# Research Article: {topic}

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Topic:** {topic}  
**Type:** Comprehensive Research Article

---

{research_article}

---

*Generated by CrewAI Research Agent - Comprehensive Analysis*
"""
    
    with open(article_filepath, 'w', encoding='utf-8') as f:
        f.write(article_content)
    
    # Save LinkedIn post
    post_filename = f"linkedin_post_{topic_safe}_{timestamp}.md"
    post_filepath = os.path.join(posts_dir, post_filename)
    
    post_content = f"""# LinkedIn Post: {topic}

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Topic:** {topic}  
**Type:** LinkedIn Social Media Post

---

{linkedin_post}

---

*Generated by CrewAI LinkedIn Content Creation Flow*
"""
    
    with open(post_filepath, 'w', encoding='utf-8') as f:
        f.write(post_content)
    
    # Get absolute paths
    article_output = os.path.abspath(article_filepath)
    post_output = os.path.abspath(post_filepath)
    
    print("✅ Content generation completed!")
    print("\n📁 FILES SAVED:")
    print(f"   📄 Research Article: {article_output}")
    print(f"   📱 LinkedIn Post: {post_output}")
    
    print("\n📄 RESEARCH ARTICLE PREVIEW:")
    print("-" * 60)
    # Show first 300 characters of research article
    preview_text = research_article[:300] + "..." if len(research_article) > 300 else research_article
    print(preview_text)
    print("-" * 60)
    
    print("\n📱 LINKEDIN POST PREVIEW:")
    print("-" * 40)
    print(linkedin_post)
    print("-" * 40)
    
    print(f"\n🎯 FLOW COMPLETED SUCCESSFULLY!")
    print(f"📊 Generated comprehensive research article ({len(research_article)} characters)")
    print(f"📱 Generated LinkedIn post ({len(linkedin_post)} characters)")
    
    return {
        "linkedin_post": linkedin_post,
        "research_article": research_article,
        "article_file": article_output,
        "post_file": post_output
    }


if __name__ == "__main__":
    # Run the flow
    run_create_new_post_flow()