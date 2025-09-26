#!/usr/bin/env python
from crewai.flow.flow import Flow, listen, start
from pydantic import BaseModel
from experience_blog_flow.crews.blog_crew.blog_crew import BlogCrew


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
        
        # Execute the blog crew
        inputs = {
            'experience_text': self.state.experience_text,
            'experience_topic': self.state.experience_topic
        }
        
        result = BlogCrew().crew().kickoff(inputs=inputs)
        
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