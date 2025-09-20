"""
LLM Helper for CrewAI
Provides utilities for configuring and managing LLM instances (Ollama and OpenAI)
"""
import yaml
import os
from pathlib import Path
from crewai import LLM
from typing import Dict, Any, Optional


class LLMHelper:
    """Helper class for managing LLM configurations (Ollama and OpenAI) with memory optimization"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the LLM helper
        
        Args:
            config_path: Path to the agents.yaml config file
        """
        if config_path is None:
            # Default path relative to this file - go up, then to config
            self.config_path = Path(__file__).parent.parent / "config" / "agents.yaml"
        else:
            self.config_path = Path(config_path)
        
        self.ollama_base_url = "http://localhost:11434"
        self._agents_config = None
        self._llm_cache = {}
        
        # Set OpenAI API key from environment
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        
        # Memory optimization settings for 12GB GPU 
        self.memory_optimization = {
            'auto_unload': True,         # Automatically unload models when not needed
            'max_context_length': 14746, 
            'prefer_quantized': True,    # Prefer quantized models when available
            'cpu_offload': False         # Disable CPU offloading with 12GB GPU memory
        }
    
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
            agent_name: Name of the agent (e.g., 'coach', 'influencer', 'researcher')
            
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
        Create an LLM instance for a specific agent (supports both Ollama and OpenAI)
        
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
        
        # Determine if this is an OpenAI model or Ollama model
        if model_name.startswith('gpt-') or model_name.startswith('o1-') or model_name in ['gpt-4o', 'gpt-4o-mini']:
            # OpenAI model
            if not self.openai_api_key:
                raise ValueError(f"OpenAI API key not found in environment for agent '{agent_name}'. Please set OPENAI_API_KEY.")
            
            llm_params = {
                "model": f"openai/{model_name}",
                "api_key": self.openai_api_key,
                "temperature": 0.7,
                "max_tokens": 2000
            }
            
        else:
            # Ollama model
            llm_params = {
                "model": f"ollama/{model_name}",
                "base_url": self.ollama_base_url,
            }
            
            # Configure model options including thinking parameter and memory optimization
            model_options = {
                "temperature": 0.5,    # Balanced creativity 
                "top_p": 0.9,
                "top_k": 40,
                "repeat_penalty": 1.08,
                "think": thinking_enabled,  # Per-agent thinking configuration
                # Memory optimization settings
                "num_ctx": self.get_optimal_context_length(model_name),
                "num_thread": self.get_optimal_thread_count(),
                "use_mmap": True,      # Memory-map model files for better memory usage
                "use_mlock": False,    # Don't lock memory pages (allows swapping if needed)
                "numa": False          # Disable NUMA optimization for better compatibility
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
    
    def get_optimal_context_length(self, model_name: str) -> int:
        """
        Get optimal context length based on model size and available memory
        Optimized for 12GB GPU memory utilization
        
        Args:
            model_name: Name of the model
            
        Returns:
            Optimal context length
        """
        # Model size-based context optimization 
        context_map = {
            # Small models (1.7B and below) 
            'qwen2.5:0.5b': 14746,    
            'qwen2.5:1.5b': 14746,    
            'qwen2.5:3b': 14746,      
            'qwen3:1.7b': 14746,      
            # Medium models (7B range) 
            'openhermes:v2.5': 14746, 
            'llama3.2:3b': 14746,     
            'llama3.1:7b': 14746,     
            # Larger models 
            'llama3.1:13b': 14746,     
            'llama3.1:70b': 14746,    
        }
        
        # Get context length for specific model, with fallback to reduced default
        return context_map.get(model_name, 14746)  
    
    def get_optimal_thread_count(self) -> int:
        """
        Get optimal thread count based on CPU cores
        
        Returns:
            Optimal number of threads
        """
        try:
            import os
            # Use half the available CPU cores for better system responsiveness
            cpu_count = os.cpu_count() or 4
            return max(2, min(8, cpu_count // 2))
        except Exception:
            return 4  # Safe default
    
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
            response = requests.get(f"{self.ollama_base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def unload_model(self, model_name: str) -> bool:
        """
        Unload a specific model from memory to free up resources
        
        Args:
            model_name: Name of the model to unload
            
        Returns:
            True if successful, False otherwise
        """
        try:
            import requests
            payload = {
                "model": model_name,
                "keep_alive": 0  # Immediately unload
            }
            response = requests.post(
                f"{self.ollama_base_url}/api/generate",
                json=payload,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Warning: Could not unload model {model_name}: {e}")
            return False
    
    def get_loaded_models(self) -> list:
        """
        Get list of currently loaded models in Ollama
        
        Returns:
            List of loaded model names
        """
        try:
            import requests
            response = requests.get(f"{self.ollama_base_url}/api/ps", timeout=5)
            if response.status_code == 200:
                models_data = response.json()
                return [model.get('name', '') for model in models_data.get('models', [])]
        except Exception as e:
            print(f"Warning: Could not get loaded models: {e}")
        return []
    
    def cleanup_unused_models(self) -> None:
        """
        Unload models that are not currently in use
        """
        if not self.memory_optimization['auto_unload']:
            return
            
        loaded_models = self.get_loaded_models()
        used_models = set(self.get_llm_model_name(agent) for agent in self._llm_cache.keys())
        
        for model in loaded_models:
            if model and model not in used_models:
                print(f"🧹 Unloading unused model: {model}")
                self.unload_model(model)
    
    def unload_all_models(self) -> Dict[str, bool]:
        """
        Unload all currently loaded models to free GPU memory
        
        Returns:
            Dictionary mapping model names to unload success status
        """
        loaded_models = self.get_loaded_models()
        results = {}
        
        print(f"🧹 Unloading all {len(loaded_models)} loaded models...")
        
        for model in loaded_models:
            if model:
                print(f"  🗑️ Unloading: {model}")
                success = self.unload_model(model)
                results[model] = success
                if success:
                    print(f"    ✅ Successfully unloaded: {model}")
                else:
                    print(f"    ❌ Failed to unload: {model}")
        
        # Clear LLM cache to force recreation next time
        self._llm_cache.clear()
        
        # Verify cleanup
        remaining_models = self.get_loaded_models()
        if remaining_models:
            print(f"⚠️ Warning: {len(remaining_models)} models still loaded: {remaining_models}")
        else:
            print("✅ All models successfully unloaded - GPU memory freed!")
        
        return results
    
    def force_cleanup_memory(self) -> bool:
        """
        Force cleanup of all models and cache - use after task completion
        
        Returns:
            True if cleanup was successful
        """
        try:
            print("🔄 Starting comprehensive memory cleanup...")
            
            # Step 1: Unload all models
            unload_results = self.unload_all_models()
            
            # Step 2: Clear internal cache
            self._llm_cache.clear()
            
            # Step 3: Force garbage collection
            import gc
            gc.collect()
            
            # Step 4: Verify cleanup
            remaining_models = self.get_loaded_models()
            
            if not remaining_models:
                print("✅ Memory cleanup completed successfully!")
                return True
            else:
                print(f"⚠️ Partial cleanup: {len(remaining_models)} models still loaded")
                return False
                
        except Exception as e:
            print(f"❌ Error during memory cleanup: {e}")
            return False
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get memory usage statistics
        
        Returns:
            Dictionary with memory information
        """
        stats = {
            'loaded_models': self.get_loaded_models(),
            'cached_llms': list(self._llm_cache.keys()),
            'ollama_connected': self.validate_ollama_connection()
        }
        
        try:
            import psutil
            memory = psutil.virtual_memory()
            stats.update({
                'system_memory_total_gb': round(memory.total / (1024**3), 2),
                'system_memory_used_gb': round(memory.used / (1024**3), 2),
                'system_memory_percent': memory.percent
            })
        except ImportError:
            stats['memory_info'] = 'psutil not available - install with: pip install psutil'
        
        return stats


# Convenience function for quick LLM creation
def create_llm(agent_name: str, config_path: Optional[str] = None) -> LLM:
    """
    Convenience function to create an LLM instance (Ollama or OpenAI)
    
    Args:
        agent_name: Name of the agent
        config_path: Optional path to agents.yaml
        
    Returns:
        Configured LLM instance
    """
    helper = LLMHelper(config_path)
    return helper.create_llm_instance(agent_name)


# Maintain backward compatibility
OllamaHelper = LLMHelper
create_ollama_llm = create_llm


# Example usage
if __name__ == "__main__":
    helper = LLMHelper()
    
    print("🤖 Available LLM Models:")
    models = helper.list_available_models()
    for agent, model in models.items():
        thinking = helper.get_thinking_parameter(agent)
        provider = "OpenAI" if model.startswith('gpt-') or model.startswith('o1-') or model in ['gpt-4o', 'gpt-4o-mini'] else "Ollama"
        context_length = helper.get_optimal_context_length(model) if provider == "Ollama" else "API managed"
        print(f"  {agent}: {model} ({provider}) (thinking: {thinking}) (context: {context_length})")
    
    print(f"\n🔗 Ollama Connection: {'✅ Connected' if helper.validate_ollama_connection() else '❌ Not connected'}")
    print(f"🔑 OpenAI API Key: {'✅ Found' if helper.openai_api_key else '❌ Not found'}")
    
    # Show memory statistics
    print("\n💾 Memory Statistics:")
    stats = helper.get_memory_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Test creating an LLM instance
    try:
        coach_llm = helper.create_llm_instance('coach')
        print(f"\n✅ Successfully created LLM for coach: {coach_llm.model}")
        
        # Demonstrate memory management
        print(f"\n🧹 Loaded models before cleanup: {helper.get_loaded_models()}")
        helper.cleanup_unused_models()
        print(f"🧹 Loaded models after cleanup: {helper.get_loaded_models()}")
        
    except Exception as e:
        print(f"\n❌ Error creating LLM: {e}")