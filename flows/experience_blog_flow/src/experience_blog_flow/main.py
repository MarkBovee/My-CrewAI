#!/usr/bin/env python
import sys
import os
from crewai.flow.flow import Flow, listen, start
from pydantic import BaseModel
from experience_blog_flow.crews.blog_crew.blog_crew import BlogCrew

# Add helpers to path for output functionality
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'helpers'))
from output_helper import output_helper


class ExperienceBlogState(BaseModel):
    """State for the experience blog creation flow"""
    experience_text: str = ""
    experience_topic: str = ""
    analysis_results: str = ""
    research_results: str = ""
    blog_content: str = ""


class ExperienceBlogFlow(Flow[ExperienceBlogState]):
    """
    Experience Blog Creation Flow
    
    A flow that transforms personal experiences into comprehensive blog posts
    by analyzing themes, conducting research, and creating engaging content.
    """
    
    @start()
    def create_blog_from_experience(self):
        """
        Create a blog post from personal experience using the blog creation crew
        """
        print(f"🚀 Starting experience blog creation for: '{self.state.experience_topic}'")
        
        # Execute the blog crew with simplified single-task workflow
        inputs = {
            'experience_text': self.state.experience_text
        }
        
        result = BlogCrew().crew().kickoff(inputs=inputs)
        
        # Save the generated blog content to file
        if result:
            blog_content = None
            
            # Handle different result formats
            if hasattr(result, 'tasks_output') and result.tasks_output:
                # Extract the final task output (expanded blog post)
                final_task = result.tasks_output[-1]  # Last task should be the expanded version
                if hasattr(final_task, 'raw'):
                    blog_content = final_task.raw
                elif hasattr(final_task, 'output'):
                    blog_content = final_task.output
            elif hasattr(result, 'raw'):
                blog_content = result.raw
            
            if blog_content and blog_content.strip() and blog_content != "The polished, expanded, and publication-ready blog post is above.":
                # Create metadata for the file
                metadata = {
                    'topic': self.state.experience_topic,
                    'flow': 'experience_blog_two_stage',
                    'agents': 'research_writer + blog_writer', 
                    'generated_at': output_helper._generate_timestamp(),
                    'input_length': len(self.state.experience_text)
                }
                
                # Save content to organized output directory
                saved_path = output_helper.save_content(
                    flow_name='experience_blog',
                    content=blog_content,
                    filename_prefix='polished_blog_post',
                    file_extension='md',
                    include_timestamp=True,
                    metadata=metadata
                )
                
                print(f"💾 Polished blog post saved to: {saved_path}")
                
                # Store the content in state for potential downstream use
                self.state.blog_content = blog_content
            else:
                print("⚠️ No valid blog content found in result to save")
                
                # Debug: print result structure
                if hasattr(result, 'tasks_output'):
                    print(f"📊 Found {len(result.tasks_output)} task outputs")
                    for i, task_out in enumerate(result.tasks_output):
                        if hasattr(task_out, 'raw'):
                            print(f"  Task {i+1} content length: {len(task_out.raw)} chars")
                        elif hasattr(task_out, 'output'):
                            print(f"  Task {i+1} output length: {len(task_out.output)} chars")
        
        print("✅ Experience blog creation completed!")
        return result


def kickoff(experience_text: str = "", experience_topic: str = "Personal Development Experience"):
    """
    Run the experience blog flow.
    
    Args:
        experience_text: The personal experience to transform into a blog post
        experience_topic: A short topic description for the experience
    """
    flow = ExperienceBlogFlow()
    flow.state.experience_text = experience_text
    flow.state.experience_topic = experience_topic
    return flow.kickoff()


def plot():
    """
    Plot the experience blog flow.
    """
    flow = ExperienceBlogFlow()
    flow.plot()


if __name__ == "__main__":
    # Example usage
    sample_experience = """
    Last month, I had to migrate our legacy monolithic application to microservices on Kubernetes.
    The biggest challenge was handling data consistency across services while maintaining zero downtime.
    After researching different patterns, I implemented the Saga pattern with event sourcing.
    The result was a 40% improvement in deployment frequency and 60% reduction in rollback incidents.
    """
    
    kickoff(sample_experience, "Microservices Migration with Kubernetes")