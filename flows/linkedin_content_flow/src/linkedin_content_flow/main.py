#!/usr/bin/env python
import sys
import os
from crewai.flow.flow import Flow, listen, start
from pydantic import BaseModel
from linkedin_content_flow.crews.content_crew.content_crew import ContentCrew

# Add helpers to path for output functionality
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'helpers'))
from output_helper import output_helper


class LinkedInContentState(BaseModel):
    """State for the LinkedIn content creation flow"""
    topic: str = ""
    current_year: int = 2025
    research_results: str = ""
    blog_content: str = ""
    linkedin_post: str = ""


class LinkedInContentFlow(Flow[LinkedInContentState]):
    """
    LinkedIn Content Creation Flow
    
    A flow that creates comprehensive LinkedIn content by researching trending skills,
    writing detailed blog posts, and creating engaging social media posts.
    """
    
    @start()
    def generate_content(self):
        """
        Generate LinkedIn content using the content creation crew
        """
        print(f"🚀 Starting LinkedIn content generation for topic: '{self.state.topic}'")
        
        # Execute the content crew
        inputs = {
            'topic': self.state.topic,
            'current_year': self.state.current_year
        }
        
        result = ContentCrew().crew().kickoff(inputs=inputs)
        
        # Save the generated content to files
        if result and hasattr(result, 'tasks_output'):
            # LinkedIn content typically generates multiple outputs (research, blog, post)
            # Let's extract and save each type of content
            
            metadata = {
                'topic': self.state.topic,
                'flow': 'linkedin_content',
                'generated_at': output_helper._generate_timestamp(),
                'year': self.state.current_year
            }
            
            outputs_to_save = {}
            
            # Process each task output
            for i, task_output in enumerate(result.tasks_output):
                if hasattr(task_output, 'raw'):
                    content = task_output.raw
                    
                    # Determine content type based on task order or content
                    if i == 0 or 'research' in content.lower()[:200]:
                        outputs_to_save['research'] = content
                    elif i == 1 or any(word in content.lower()[:200] for word in ['blog', 'article', 'post']):
                        outputs_to_save['blog'] = content
                    elif i == 2 or 'linkedin' in content.lower()[:200]:
                        outputs_to_save['linkedin_post'] = content
                    else:
                        outputs_to_save[f'output_{i}'] = content
            
            # If we have consolidated output, save that too
            if hasattr(result, 'raw') and result.raw:
                outputs_to_save['complete'] = result.raw
            
            # Save all outputs with organized naming
            if outputs_to_save:
                saved_files = output_helper.save_multiple_outputs(
                    flow_name='linkedin_content',
                    outputs=outputs_to_save,
                    filename_prefix='content',
                    file_extension='md',
                    include_timestamp=True,
                    metadata=metadata
                )
                
                for output_type, file_path in saved_files.items():
                    print(f"💾 {output_type.title()} content saved to: {file_path}")
                
                # Store relevant content in state
                if 'blog' in outputs_to_save:
                    self.state.blog_content = outputs_to_save['blog']
                if 'linkedin_post' in outputs_to_save:
                    self.state.linkedin_post = outputs_to_save['linkedin_post']
                if 'research' in outputs_to_save:
                    self.state.research_results = outputs_to_save['research']
        
        print("✅ LinkedIn content generation completed!")
        return result


def kickoff(topic: str = "AI-powered development tools"):
    """
    Run the LinkedIn content flow.
    
    Args:
        topic: The topic to create content about
    """
    flow = LinkedInContentFlow()
    flow.state.topic = topic
    return flow.kickoff()


def plot():
    """
    Plot the LinkedIn content flow.
    """
    flow = LinkedInContentFlow()
    flow.plot()


if __name__ == "__main__":
    kickoff()