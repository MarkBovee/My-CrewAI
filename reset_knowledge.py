#!/usr/bin/env python3
"""
Knowledge Reset Utility for CrewAI LinkedIn Crew
Simple script to reset topic checking and knowledge data
"""

import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from linkedin.helpers.knowledge_helper import KnowledgeHelper, reset_topic_check, reset_web_knowledge, reset_all_knowledge


def main():
    parser = argparse.ArgumentParser(description="Reset CrewAI knowledge data")
    parser.add_argument(
        '--type', 
        choices=['topics', 'web', 'all'], 
        default='topics',
        help='What to reset: topics (article memory), web (search results), or all'
    )
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show knowledge statistics before and after reset'
    )
    
    args = parser.parse_args()
    
    helper = KnowledgeHelper()
    
    if args.stats:
        print("📊 Knowledge Statistics BEFORE Reset:")
        stats = helper.get_knowledge_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
        print()
    
    # Perform reset based on type
    if args.type == 'topics':
        print("🎯 Resetting topic checking (article memory)...")
        success = reset_topic_check()
    elif args.type == 'web':
        print("🔍 Resetting web search results...")
        success = reset_web_knowledge()
    elif args.type == 'all':
        print("💫 Resetting ALL knowledge data...")
        success = reset_all_knowledge()
    
    if args.stats and success:
        print("\n📊 Knowledge Statistics AFTER Reset:")
        stats = helper.get_knowledge_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())