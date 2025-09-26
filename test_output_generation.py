"""
Test script to validate output file generation for CrewAI flows.
"""

import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

# Add flows to path
sys.path.append(os.path.join(project_root, 'flows', 'experience_blog_flow', 'src'))
sys.path.append(os.path.join(project_root, 'flows', 'linkedin_content_flow', 'src'))

from helpers.output_helper import output_helper
from experience_blog_flow.main import kickoff as experience_kickoff

def test_output_helper():
    """Test the output helper functionality"""
    print("🧪 Testing OutputHelper...")
    
    # Test basic file saving
    test_content = "# Test Blog Post\n\nThis is a test blog post to verify our output system works correctly."
    
    saved_path = output_helper.save_content(
        flow_name='test',
        content=test_content,
        filename_prefix='test_blog',
        file_extension='md',
        include_timestamp=True,
        metadata={
            'test': True,
            'purpose': 'validation'
        }
    )
    
    print(f"✅ Test file saved to: {saved_path}")
    
    # Verify file exists and has correct content
    if os.path.exists(saved_path):
        with open(saved_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if test_content in content:
                print("✅ File content verification passed")
            else:
                print("❌ File content verification failed")
    else:
        print("❌ File was not created")

def test_experience_blog_flow():
    """Test the experience blog flow with file saving"""
    print("\n🧪 Testing Experience Blog Flow...")
    
    sample_experience = """
    Last week, I implemented a new caching strategy for our API that reduced response times by 75%.
    The key was using Redis with smart invalidation patterns and proper cache warming strategies.
    This taught me the importance of measuring before optimizing and how small changes can have big impacts.
    """
    
    try:
        result = experience_kickoff(
            experience_text=sample_experience,
            experience_topic="API Performance Optimization"
        )
        
        print("✅ Experience blog flow completed successfully")
        
        # Check if output files were created
        output_files = output_helper.list_output_files('experience_blog', 'md')
        print(f"📁 Found {len(output_files)} output files in experience_blog directory")
        
        for file_path in output_files[-3:]:  # Show last 3 files
            print(f"  📄 {os.path.basename(file_path)}")
            
    except Exception as e:
        print(f"❌ Experience blog flow failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Starting output file generation tests...\n")
    
    # Test 1: Basic output helper functionality
    test_output_helper()
    
    # Test 2: Experience blog flow with file saving
    test_experience_blog_flow()
    
    print("\n✅ All tests completed!")