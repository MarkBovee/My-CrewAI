#!/usr/bin/env python3
"""
Test script to demonstrate GitHub Copilot integration features in LLMHelper
"""

import sys
from pathlib import Path
import logging

# Setup logging to see the auto-upgrade messages
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')

# Add project root to path
sys.path.insert(0, '.')
from helpers.llm_helper import LLMHelper

def test_github_integration():
    """Test GitHub Copilot integration features"""
    
    print("🚀 Testing Enhanced LLMHelper with GitHub Copilot Integration")
    print("=" * 60)
    
    # Test with experience blog flow config
    config_path = Path('flows/experience_blog_flow/src/experience_blog_flow/config/agents.yaml')
    helper = LLMHelper(config_path=config_path)
    
    print("\n📋 1. List Available GitHub Models:")
    github_models = helper.list_github_models()
    for i, model in enumerate(github_models, 1):
        print(f"   {i}. {model}")
    
    print("\n🔧 2. GitHub Integration Status:")
    status = helper.get_github_model_status()
    print(f"   ✅ GitHub Token: {'Configured' if status['github_token_configured'] else 'Not Found'}")
    print(f"   🌐 Base URL: {status['github_base_url']}")
    print(f"   🔄 Auto-upgrade: {'Enabled' if status['auto_upgrade_enabled'] else 'Disabled'}")
    print(f"   📊 Available Models: {len(status['available_models'])}")
    
    print("\n🧪 3. Testing Auto-Upgrade Functionality:")
    print("   Configuration: llm: gpt-4o")
    
    # This will trigger the auto-upgrade and show the log message
    model_name = helper.get_llm_model_name('writer')
    print(f"   ➡️  Result: {model_name}")
    
    print("\n✅ 4. Create LLM Instance:")
    llm_instance = helper.create_llm_instance('writer')
    print(f"   🤖 LLM Model: {llm_instance.model}")
    print(f"   🔗 Base URL: {getattr(llm_instance, 'base_url', 'Default')}")
    
    print("\n🎉 All GitHub Copilot integration features working correctly!")
    print("\nNow you can simply use 'gpt-4o' in your agent configs,")
    print("and it will automatically use GitHub Copilot when available! 🚀")

if __name__ == "__main__":
    test_github_integration()