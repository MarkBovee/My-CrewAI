#!/usr/bin/env python3
"""
Main entry point for the CrewAI LinkedIn Crew
DEPRECATED: Direct crew execution is deprecated. Use flows instead.

For proper execution, use:
  python -c "from src.linkedin.flows.create_new_post_flow import CreateNewPostFlow; flow = CreateNewPostFlow(); flow.state.topic = 'your topic'; flow.kickoff()"
"""

import sys
import warnings
from .flows.create_new_post_flow import CreateNewPostFlow


def run(topic=None):
    """
    DEPRECATED: Direct crew execution is deprecated.
    Use CreateNewPostFlow instead for proper execution.
    
    Args:
        topic: Optional topic string.
    """
    warnings.warn(
        "Direct crew execution is deprecated. Use CreateNewPostFlow for proper execution.",
        DeprecationWarning,
        stacklevel=2
    )
    
    print("❌ DEPRECATED: Direct crew execution is no longer supported.")
    print("✅ Use flows for proper execution:")
    print("")
    print("Python example:")
    print("  from src.linkedin.flows.create_new_post_flow import CreateNewPostFlow")
    print("  flow = CreateNewPostFlow()")
    print("  flow.state.topic = 'your topic here'")
    print("  result = flow.kickoff()")
    print("")
    print("Or use the web interface: python web_server.py")
    
    # Offer to redirect to flow execution
    if topic:
        print(f"\n� Redirecting to flow execution for topic: '{topic}'")
        return run_via_flow(topic)
    else:
        print("\n⚠️ No topic provided. Please use flow-based execution.")
        return None


def run_via_flow(topic: str):
    """
    Execute via CreateNewPostFlow (recommended approach)
    
    Args:
        topic: Topic to research and create content about
    """
    print(f"🚀 Executing via CreateNewPostFlow for topic: '{topic}'")
    
    try:
        # Create and execute flow
        flow = CreateNewPostFlow()
        flow.state.topic = topic
        result = flow.kickoff()
        
        print("✅ Flow execution completed successfully!")
        return result
        
    except Exception as e:
        print(f"❌ Flow execution failed: {e}")
        raise e


def run_with_topic(topic: str):
    """
    DEPRECATED: Use run_via_flow instead.
    
    Args:
        topic: Custom topic to research and create content about
    """
    warnings.warn(
        "run_with_topic is deprecated. Use run_via_flow instead.",
        DeprecationWarning,
        stacklevel=2
    )
    
    print("❌ DEPRECATED: run_with_topic is deprecated.")
    print("🔄 Redirecting to flow execution...")
    
    return run_via_flow(topic)


if __name__ == "__main__":
    # Check if topic provided via command line
    if len(sys.argv) > 1:
        custom_topic = " ".join(sys.argv[1:])
        run_with_topic(custom_topic)
    else:
        run()