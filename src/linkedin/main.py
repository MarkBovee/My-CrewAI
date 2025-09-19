#!/usr/bin/env python3
"""
Main entry point for the CrewAI LinkedIn Crew
"""

import sys
from linkedin_crew import LinkedInCrew


def run():
    """
    Run the CrewAI LinkedIn crew
    """
    # Instantiate and run the crew
    crew = LinkedInCrew()
    crew.crew().kickoff()


if __name__ == "__main__":
    run()