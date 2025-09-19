"""
Ollama LLM Helper for CrewAI
Provides utilities for configuring and managing Ollama LLM instances
"""
import yaml
import os
from pathlib import Path
from crewai import LLM
from typing import Dict, Any, Optional


class OllamaHelper:
    """Helper class for managing Ollama LLM configurations"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the Ollama helper
        
        Args:
            config_path: Path to the agents.yaml config file
        """
        if config_path is None:
            # Default path relative to this file - go up, then to config
            self.config_path = Path(__file__).parent.parent / "config" / "agents.yaml"
        else:
            self.config_path = Path(config_path)
        
        self.base_url = "http://localhost:11434"
        self._agents_config = None
        self._llm_cache = {}
    
    def load_agents_config(self) -> Dict[str, Any]:
        """Load the agents configuration from YAML"""
        if self._agents_config is None:
            try:
                with open(self.config_path, 'r', encoding='utf-8') as file:
                    self._agents_config = yaml.safe_load(file)
            except FileNotFoundError:
                raise FileNotFoundError(f"Agents config file not found: {self.config_path}")
            except yaml.YAMLError as e:
                raise ValueError(f"Error parsing agents.yaml: {e}")
        
        return self._agents_config
    
    def get_llm_model_name(self, agent_name: str) -> str:
        """
        Get the LLM model name for a specific agent
        
        Args:
            agent_name: Name of the agent (e.g., 'coach', 'influencer', 'critic')
            
        Returns:
            LLM model name specified in the agent configuration
        """
        config = self.load_agents_config()
        
        if agent_name not in config:
            raise ValueError(f"Agent '{agent_name}' not found in configuration")
        
        agent_config = config[agent_name]
        if 'llm' not in agent_config:
            raise ValueError(f"No LLM specified for agent '{agent_name}'")
        
        return agent_config['llm']
    
    def create_llm_instance(self, agent_name: str) -> LLM:
        """
        Create an LLM instance for a specific agent
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            Configured LLM instance
        """
        # Check cache first
        if agent_name in self._llm_cache:
            return self._llm_cache[agent_name]
        
        model_name = self.get_llm_model_name(agent_name)
        thinking_enabled = self.get_thinking_parameter(agent_name)
        
        # Create LLM instance with proper Ollama provider prefix and thinking parameter
        # Based on previous implementation - use model_kwargs with options for Ollama parameters
        llm_params = {
            "model": f"ollama/{model_name}",
            "base_url": self.base_url,
        }
        
        # Configure model options including thinking parameter
        model_options = {
            "temperature": 0.7,    # Balanced creativity 
            "top_p": 0.9,
            "top_k": 40,
            "repeat_penalty": 1.08,
            "think": thinking_enabled  # Per-agent thinking configuration
        }
        
        # Pass options through model_kwargs as in your previous implementation
        llm_params["model_kwargs"] = {"options": model_options}
        
        llm_instance = LLM(**llm_params)
        
        # Cache the instance
        self._llm_cache[agent_name] = llm_instance
        
        return llm_instance
    
    def get_thinking_parameter(self, agent_name: str) -> bool:
        """
        Get the thinking parameter for a specific agent
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            Boolean value for the thinking parameter
        """
        config = self.load_agents_config()
        
        if agent_name not in config:
            raise ValueError(f"Agent '{agent_name}' not found in configuration")
        
        agent_config = config[agent_name]
        return agent_config.get('thinking', True)  # Default to True if not specified
    
    def list_available_models(self) -> Dict[str, str]:
        """
        Get all LLM models specified in the agents configuration
        
        Returns:
            Dictionary mapping agent names to their LLM models
        """
        config = self.load_agents_config()
        models = {}
        
        for agent_name, agent_config in config.items():
            if 'llm' in agent_config:
                models[agent_name] = agent_config['llm']
        
        return models
    
    def validate_ollama_connection(self) -> bool:
        """
        Validate that Ollama is running and accessible
        
        Returns:
            True if Ollama is accessible, False otherwise
        """
        try:
            import requests
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False


# Convenience function for quick LLM creation
def create_ollama_llm(agent_name: str, config_path: Optional[str] = None) -> LLM:
    """
    Convenience function to create an Ollama LLM instance
    
    Args:
        agent_name: Name of the agent
        config_path: Optional path to agents.yaml
        
    Returns:
        Configured LLM instance
    """
    helper = OllamaHelper(config_path)
    return helper.create_llm_instance(agent_name)


# Example usage
if __name__ == "__main__":
    helper = OllamaHelper()
    
    print("🤖 Available LLM Models:")
    models = helper.list_available_models()
    for agent, model in models.items():
        thinking = helper.get_thinking_parameter(agent)
        print(f"  {agent}: {model} (thinking: {thinking})")
    
    print(f"\n🔗 Ollama Connection: {'✅ Connected' if helper.validate_ollama_connection() else '❌ Not connected'}")
    
    # Test creating an LLM instance
    try:
        coach_llm = helper.create_llm_instance('coach')
        print(f"\n✅ Successfully created LLM for coach: {coach_llm.model}")
    except Exception as e:
        print(f"\n❌ Error creating LLM: {e}")