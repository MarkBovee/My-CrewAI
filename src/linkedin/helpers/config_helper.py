#!/usr/bin/env python3
"""
Configuration Helper for CrewAI LinkedIn Project
Manages Ollama models and agent configurations with comprehensive utilities.
"""

import sys
import yaml
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
import subprocess
import requests
from datetime import datetime


class OllamaConfigManager:
    """Comprehensive Ollama configuration and model management utility"""
    
    def __init__(self, config_dir: Optional[str] = None):
        if config_dir is None:
            # Default path relative to this file
            self.config_dir = Path(__file__).parent.parent / "config"
        else:
            self.config_dir = Path(config_dir)
        self.agents_config_path = self.config_dir / "agents.yaml"
        self.tasks_config_path = self.config_dir / "tasks.yaml"
        self.ollama_url = "http://localhost:11434"
        
    def load_agents_config(self) -> Dict[str, Any]:
        """Load agents configuration from YAML"""
        try:
            with open(self.agents_config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"❌ Agents config not found: {self.agents_config_path}")
            return {}
        except yaml.YAMLError as e:
            print(f"❌ Error parsing agents.yaml: {e}")
            return {}
    
    def load_tasks_config(self) -> Dict[str, Any]:
        """Load tasks configuration from YAML"""
        try:
            with open(self.tasks_config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"❌ Tasks config not found: {self.tasks_config_path}")
            return {}
        except yaml.YAMLError as e:
            print(f"❌ Error parsing tasks.yaml: {e}")
            return {}
    
    def check_ollama_status(self) -> bool:
        """Check if Ollama server is running"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def list_ollama_models(self) -> List[Dict[str, Any]]:
        """List all available models in Ollama"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=10)
            if response.status_code == 200:
                return response.json().get("models", [])
            return []
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching Ollama models: {e}")
            return []
    
    def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific model"""
        try:
            response = requests.post(
                f"{self.ollama_url}/api/show",
                json={"name": model_name},
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
            return None
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching model info for {model_name}: {e}")
            return None
    
    def check_model_exists(self, model_name: str) -> bool:
        """Check if a specific model exists in Ollama"""
        models = self.list_ollama_models()
        return any(model["name"] == model_name for model in models)
    
    def pull_model(self, model_name: str) -> bool:
        """Pull a model from Ollama registry"""
        try:
            print(f"🔄 Pulling model: {model_name}")
            result = subprocess.run(
                ["ollama", "pull", model_name],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            success = result.returncode == 0
            if success:
                print(f"✅ Successfully pulled {model_name}")
            else:
                print(f"❌ Failed to pull {model_name}: {result.stderr}")
            return success
        except subprocess.TimeoutExpired:
            print(f"❌ Timeout pulling {model_name}")
            return False
        except Exception as e:
            print(f"❌ Error pulling {model_name}: {e}")
            return False
    
    def validate_agent_models(self) -> Dict[str, bool]:
        """Validate that all models referenced in agents.yaml exist"""
        agents_config = self.load_agents_config()
        results = {}
        
        for agent_name, agent_config in agents_config.items():
            if isinstance(agent_config, dict) and "llm" in agent_config:
                model_name = agent_config["llm"]
                # Remove the ollama/ prefix if present
                clean_model_name = model_name.replace("ollama/", "")
                exists = self.check_model_exists(clean_model_name)
                results[f"{agent_name} ({model_name})"] = exists
                
                if not exists:
                    print(f"❌ Model not found: {model_name} for agent {agent_name}")
                else:
                    print(f"✅ Model found: {model_name} for agent {agent_name}")
        
        return results
    
    def update_agent_model(self, agent_name: str, new_model: str) -> bool:
        """Update the model for a specific agent"""
        agents_config = self.load_agents_config()
        
        if agent_name not in agents_config:
            print(f"❌ Agent {agent_name} not found in configuration")
            return False
        
        # Ensure the model exists
        clean_model_name = new_model.replace("ollama/", "")
        if not self.check_model_exists(clean_model_name):
            print(f"❌ Model {clean_model_name} not found in Ollama")
            print("Available models:")
            self.list_models_summary()
            return False
        
        # Update the configuration
        agents_config[agent_name]["llm"] = f"ollama/{clean_model_name}"
        
        try:
            with open(self.agents_config_path, 'w', encoding='utf-8') as f:
                yaml.dump(agents_config, f, default_flow_style=False, sort_keys=False)
            print(f"✅ Updated {agent_name} to use model: {new_model}")
            return True
        except Exception as e:
            print(f"❌ Error updating agents.yaml: {e}")
            return False
    
    def generate_config_report(self) -> Dict[str, Any]:
        """Generate a comprehensive configuration report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "ollama_status": self.check_ollama_status(),
            "agents_config": self.load_agents_config(),
            "tasks_config": self.load_tasks_config(),
            "model_validation": self.validate_agent_models(),
            "available_models": self.list_ollama_models()
        }
        return report
    
    def list_models_summary(self):
        """Print a summary of available models"""
        models = self.list_ollama_models()
        if not models:
            print("❌ No models found or Ollama server not accessible")
            return
        
        print("\n📋 Available Ollama Models:")
        print("-" * 50)
        for model in models:
            name = model.get("name", "Unknown")
            size = model.get("size", 0)
            modified = model.get("modified_at", "Unknown")
            
            # Format size
            if size > 1e9:
                size_str = f"{size/1e9:.1f}GB"
            elif size > 1e6:
                size_str = f"{size/1e6:.1f}MB"
            else:
                size_str = f"{size}B"
            
            print(f"  • {name:<30} ({size_str})")
        print("-" * 50)
    
    def setup_recommended_model(self):
        """Setup recommended model for the LinkedIn crew"""
        recommended_model = "openhermes:v2.5"
        
        print(f"🎯 Setting up recommended model: {recommended_model}")
        
        if not self.check_model_exists(recommended_model):
            print(f"📥 Model {recommended_model} not found locally, pulling...")
            if not self.pull_model(recommended_model):
                print("❌ Failed to pull recommended model")
                return False
        
        # Update all agents to use this model
        agents_config = self.load_agents_config()
        for agent_name in agents_config.keys():
            self.update_agent_model(agent_name, recommended_model)
        
        print("✅ All agents updated to use recommended model")
        return True


def main():
    parser = argparse.ArgumentParser(description="CrewAI LinkedIn Project Configuration Helper")
    parser.add_argument("--status", action="store_true", help="Check Ollama and configuration status")
    parser.add_argument("--models", action="store_true", help="List available Ollama models")
    parser.add_argument("--validate", action="store_true", help="Validate agent model configurations")
    parser.add_argument("--report", action="store_true", help="Generate comprehensive configuration report")
    parser.add_argument("--setup", action="store_true", help="Setup recommended model configuration")
    parser.add_argument("--update-agent", nargs=2, metavar=("AGENT", "MODEL"), help="Update agent model")
    parser.add_argument("--pull", metavar="MODEL", help="Pull a specific model")
    parser.add_argument("--all", action="store_true", help="Run all checks and reports")
    
    args = parser.parse_args()
    
    # Initialize the configuration manager
    config_manager = OllamaConfigManager()
    
    # Handle --all flag
    if args.all:
        print("🔍 Running comprehensive configuration check...")
        print("=" * 60)
        
        # Status check
        print("\n1. 🚀 Ollama Status Check")
        if config_manager.check_ollama_status():
            print("✅ Ollama server is running")
        else:
            print("❌ Ollama server is not accessible")
            print("   Please start Ollama: 'ollama serve'")
        
        # List models
        print("\n2. 📋 Available Models")
        config_manager.list_models_summary()
        
        # Validate configurations
        print("\n3. ✅ Model Validation")
        config_manager.validate_agent_models()
        
        # Show configurations
        print("\n4. ⚙️  Current Configuration")
        agents_config = config_manager.load_agents_config()
        print("Agents configuration:")
        for agent_name, agent_config in agents_config.items():
            if isinstance(agent_config, dict) and "llm" in agent_config:
                print(f"  • {agent_name}: {agent_config['llm']}")
        
        print("\n✅ Configuration check complete!")
        return
    
    # Handle individual flags
    if args.status:
        print("🚀 Checking Ollama status...")
        if config_manager.check_ollama_status():
            print("✅ Ollama server is running")
        else:
            print("❌ Ollama server is not accessible")
    
    if args.models:
        config_manager.list_models_summary()
    
    if args.validate:
        print("✅ Validating agent model configurations...")
        config_manager.validate_agent_models()
    
    if args.report:
        report = config_manager.generate_config_report()
        print("📊 Configuration Report:")
        print(json.dumps(report, indent=2, default=str))
    
    if args.setup:
        config_manager.setup_recommended_model()
    
    if args.update_agent:
        agent_name, model_name = args.update_agent
        config_manager.update_agent_model(agent_name, model_name)
    
    if args.pull:
        config_manager.pull_model(args.pull)
    
    # If no arguments provided, show help
    if not any(vars(args).values()):
        parser.print_help()


if __name__ == "__main__":
    main()