#!/usr/bin/env python3
"""
Main entry point for the CrewAI LinkedIn Crew
"""

import sys
from .linkedin_crew import LinkedInCrew


def run():
    """
    Run the CrewAI LinkedIn crew with default inputs
    """
    # Default inputs for testing
    inputs = {
        'topic': 'AI and Software Development',
        'current_year': 2025
    }
    
    print("🚀 Starting LinkedIn Content Creation Crew...")
    
    # Instantiate and run the crew
    crew = LinkedInCrew()
    result = crew.crew().kickoff(inputs=inputs)
    
    print("✅ Crew execution completed!")
    print(f"📄 Final Result: {result}")
    return result


if __name__ == "__main__":
    run()