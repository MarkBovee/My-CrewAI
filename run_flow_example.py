#!/usr/bin/env python3
"""
Example script demonstrating proper flow-based execution
This is the recommended way to run the CrewAI content generation
"""

import sys
sys.path.append('src')

from src.linkedin.flows.create_new_post_flow import CreateNewPostFlow


def run_flow_with_topic(topic: str):
    """
    Execute the CrewAI flow with a specific topic
    
    Args:
        topic: The topic to research and create content about
    """
    print(f"🚀 Starting CrewAI Flow with topic: '{topic}'")
    print("=" * 60)
    
    try:
        # Create the flow instance
        flow = CreateNewPostFlow()
        
        # Set the topic in the flow state
        flow.state.topic = topic
        
        # Execute the flow
        result = flow.kickoff()
        
        print("\n✅ Flow execution completed successfully!")
        print(f"📄 Final result: {result}")
        
        return result
        
    except Exception as e:
        print(f"\n❌ Flow execution failed: {e}")
        raise e


if __name__ == "__main__":
    # Example topic - you can change this or pass as command line argument
    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:])
    else:
        topic = "mastering AI coding with GitHub SpecFlow"
    
    run_flow_with_topic(topic)