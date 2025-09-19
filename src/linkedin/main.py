#!/usr/bin/env python3
"""
Main entry point for the CrewAI LinkedIn Crew
Enhanced with knowledge management and model cleanup
"""

import sys
from .linkedin_crew import LinkedInCrew
from .helpers.knowledge_helper import KnowledgeHelper


def run():
    """
    Run the CrewAI LinkedIn crew with default inputs and enhanced knowledge management
    """
    # Default inputs for testing
    inputs = {
        'topic': 'Latest AI and Software Development Trends',
        'current_year': 2025
    }
    
    print("🚀 Starting LinkedIn Content Creation Crew...")
    print("📚 Enhanced with Knowledge Management & Model Cleanup")
    
    try:
        # Initialize knowledge helper for pre-run checks
        knowledge_helper = KnowledgeHelper()
        
        # Show knowledge statistics
        print("\n📊 Knowledge Statistics:")
        stats = knowledge_helper.get_knowledge_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        # Check topic similarity before running
        topic_check = knowledge_helper.check_topic_covered(inputs['topic'])
        print(f"\n🔍 Topic Check: {topic_check['recommendation']}")
        
        if topic_check['covered']:
            print("⚠️ Similar topics found - consider adjusting focus for uniqueness")
            for article in topic_check['similar_articles']:
                print(f"  - {article['topic']} (similarity: {article['similarity']})")
        
        # Instantiate and run the crew
        print(f"\n🎯 Processing topic: '{inputs['topic']}'")
        crew_instance = LinkedInCrew()
        result = crew_instance.crew().kickoff(inputs=inputs)
        
        print("\n✅ Crew execution completed successfully!")
        print(f"� Final Token Usage: {result.token_usage}")
        
        # Final knowledge statistics
        print("\n📈 Updated Knowledge Statistics:")
        final_stats = knowledge_helper.get_knowledge_stats()
        for key, value in final_stats.items():
            print(f"  {key}: {value}")
        
        return result
        
    except Exception as e:
        print(f"\n❌ Error during crew execution: {e}")
        
        # Attempt cleanup even on error
        try:
            from .helpers.llm_helper import LLMHelper
            llm_helper = LLMHelper()
            print("🧹 Attempting emergency model cleanup...")
            llm_helper.force_cleanup_memory()
        except Exception as cleanup_error:
            print(f"⚠️ Warning: Emergency cleanup failed: {cleanup_error}")
        
        raise e


def run_with_topic(topic: str):
    """
    Run the crew with a custom topic
    
    Args:
        topic: Custom topic to research and create content about
    """
    inputs = {
        'topic': topic,
        'current_year': 2025
    }
    
    print(f"🎯 Running crew with custom topic: '{topic}'")
    
    # Use the main run function with custom inputs
    crew_instance = LinkedInCrew()
    return crew_instance.crew().kickoff(inputs=inputs)


if __name__ == "__main__":
    # Check if topic provided via command line
    if len(sys.argv) > 1:
        custom_topic = " ".join(sys.argv[1:])
        run_with_topic(custom_topic)
    else:
        run()