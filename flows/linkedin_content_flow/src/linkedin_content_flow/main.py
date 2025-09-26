#!/usr/bin/env python
from crewai.flow.flow import Flow, listen, start
from pydantic import BaseModel
from linkedin_content_flow.crews.content_crew.content_crew import ContentCrew


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