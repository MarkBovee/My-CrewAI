#!/usr/bin/env python
"""
Main runner for the Instagram Crew.
Demonstrates thinking=false functionality for clean LLM output.
"""

import sys
sys.path.append('src')

from instagram.instagram_crew import InstagramCrew

def main():
    """Run the Instagram crew to generate a LinkedIn post about AI/tech skills."""
    print("🚀 Instagram Crew - LinkedIn Post Generator")
    print("=" * 50)
    print("🧠 Thinking: DISABLED (clean output)")
    print("📝 Verbose: ENABLED (detailed execution)")
    print("=" * 50)
    
    try:
        # Initialize the crew
        crew_instance = InstagramCrew()
        crew = crew_instance.crew()
        
        print(f"\n🎯 Crew Configuration:")
        print(f"   - Agents: {len(crew.agents)} (Coach, Influencer, Critic)")
        print(f"   - Tasks: {len(crew.tasks)} (Search, Post, Critique)")
        print(f"   - Process: Sequential workflow")
        
        print(f"\n🚀 Starting crew execution...")
        print("=" * 60)
        
        # Run the crew with current year
        inputs = {"current_year": "2025"}
        result = crew.kickoff(inputs=inputs)
        
        print("\n" + "=" * 60)
        print("✅ FINAL LINKEDIN POST:")
        print("=" * 60)
        print(result)
        
        return result
        
    except Exception as e:
        print(f"❌ Error running Instagram crew: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = main()
    
    if result:
        print("\n� Instagram Crew executed successfully!")
        print("📋 The thinking functionality is working - no <think> tags in output!")
    else:
        print("\n💥 Execution failed!")