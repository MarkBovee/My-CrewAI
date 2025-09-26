#!/usr/bin/env python3
"""
Test script for the Create Blog From Experience Flow
Tests the new flow functionality with a sample personal experience
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

def test_experience_flow():
    """Test the experience blog flow with sample data"""
    
    sample_experience = """
    Last week I spent three days debugging a performance issue in our React application that was 
    causing page load times to exceed 5 seconds. The problem seemed to be related to our data 
    fetching strategy - we were making multiple API calls on each page load instead of batching them.
    
    I tried several approaches:
    1. First, I implemented React.memo() to prevent unnecessary re-renders
    2. Then I used useCallback() hooks to memoize expensive functions
    3. Finally, I implemented a custom data fetching layer using React Query
    
    The results were impressive - page load times dropped to under 1.5 seconds, and we saw a 40% 
    reduction in API calls. The user experience improved dramatically, and our bounce rate decreased 
    by 25%. The key lesson was that performance optimization requires a systematic approach and 
    proper measurement tools.
    """
    
    try:
        print("🎬 Testing Create Blog From Experience Flow")
        print("=" * 60)
        
        from linkedin.flows.create_blog_from_experience_flow import run_create_blog_from_experience_flow
        
        print(f"📝 Sample Experience Length: {len(sample_experience)} characters")
        print("🚀 Starting flow execution...")
        
        # Run the flow
        result = run_create_blog_from_experience_flow(sample_experience)
        
        print("✅ Flow execution completed!")
        print(f"📊 Result type: {type(result)}")
        
        # Check output directory
        output_dir = Path("output/experience_blogs")
        if output_dir.exists():
            blog_files = list(output_dir.glob("*.md"))
            print(f"📁 Generated blog files: {len(blog_files)}")
            if blog_files:
                latest_file = max(blog_files, key=lambda x: x.stat().st_mtime)
                print(f"📄 Latest file: {latest_file}")
                
                # Show a preview of the generated content
                with open(latest_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    preview = content[:500] + "..." if len(content) > 500 else content
                    print(f"\n📝 Content Preview:")
                    print("-" * 40)
                    print(preview)
                    print("-" * 40)
        
        return result
        
    except Exception as e:
        print(f"❌ Error testing experience flow: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_experience_flow()