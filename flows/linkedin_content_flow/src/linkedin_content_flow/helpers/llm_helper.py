"""
LLM Helper for CrewAI
Provides utilities for configuring and managing LLM instances (Ollama, OpenAI, and GitHub Models)
"""
import yaml
import os
import logging
from pathlib import Path
from crewai import LLM
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Constants
DEFAULT_OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_GITHUB_MODELS_BASE_URL = "https://models.github.ai/inference"
DEFAULT_CONTEXT_LENGTH = 14746
DEFAULT_TEMPERATURE = 0.5
DEFAULT_MAX_TOKENS_OPENAI = 2000
DEFAULT_REQUEST_TIMEOUT = 10
CONNECTION_TIMEOUT = 5

# Model families for detection
OPENAI_MODEL_PREFIXES = ('gpt-', 'o1-')
OPENAI_MODEL_NAMES = ('gpt-4o', 'gpt-4o-mini')
GITHUB_MODEL_PREFIXES = ('github/',)


@dataclass
class MemoryOptimizationConfig:
    """Configuration for memory optimization settings"""
    auto_unload: bool = True
    max_context_length: int = DEFAULT_CONTEXT_LENGTH
    prefer_quantized: bool = True
    cpu_offload: bool = False


@dataclass
class ModelOptions:
    """Model configuration options for Ollama"""
    temperature: float = DEFAULT_TEMPERATURE
    top_p: float = 0.9
    top_k: int = 40
    repeat_penalty: float = 1.08
    think: bool = True
    num_ctx: int = DEFAULT_CONTEXT_LENGTH
    num_thread: int = 4
    use_mmap: bool = True
    use_mlock: bool = False
    numa: bool = False


class LLMHelper:
    """Helper class for managing LLM configurations (Ollama and OpenAI) with memory optimization"""

    def __init__(self, config_path: Optional[Union[str, Path]] = None):
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

        self.ollama_base_url = DEFAULT_OLLAMA_BASE_URL
        self.github_base_url = DEFAULT_GITHUB_MODELS_BASE_URL
        self._agents_config: Optional[Dict[str, Any]] = None
        self._llm_cache: Dict[str, LLM] = {}

        # Set API keys from environment
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.github_token = os.getenv('GITHUB_TOKEN')

        # Memory optimization settings for 12GB GPU
        self.memory_optimization = MemoryOptimizationConfig()
    
    def load_agents_config(self) -> Dict[str, Any]:
        """
        Load the agents configuration from YAML

        Returns:
            Dictionary containing the agents configuration

        Raises:
            FileNotFoundError: If the config file doesn't exist
            ValueError: If the YAML is malformed
            RuntimeError: If the config is empty or invalid
        """
        if self._agents_config is None:
            try:
                if not self.config_path.exists():
                    raise FileNotFoundError(f"Agents config file not found: {self.config_path}")

                with open(self.config_path, 'r', encoding='utf-8') as file:
                    config = yaml.safe_load(file)

                if not config:
                    raise RuntimeError(f"Config file is empty: {self.config_path}")

                if not isinstance(config, dict):
                    raise RuntimeError(f"Config file must contain a dictionary at root level: {self.config_path}")

                # Validate that config has expected structure
                self._validate_config_structure(config)

                self._agents_config = config
                logger.debug(f"Successfully loaded agents config from {self.config_path}")

            except yaml.YAMLError as e:
                raise ValueError(f"Error parsing agents.yaml: {e}")
            except Exception as e:
                raise RuntimeError(f"Unexpected error loading config: {e}")

        return self._agents_config

    def _validate_config_structure(self, config: Dict[str, Any]) -> None:
        """
        Validate the basic structure of the agents configuration

        Args:
            config: The configuration dictionary to validate

        Raises:
            ValueError: If the configuration structure is invalid
        """
        if not config:
            raise ValueError("Configuration is empty")

        # Check that we have at least one agent
        agent_names = [key for key in config.keys() if isinstance(config[key], dict)]
        if not agent_names:
            raise ValueError("No agent configurations found in config file")

        # Validate each agent has required fields
        for agent_name in agent_names:
            agent_config = config[agent_name]
            if not isinstance(agent_config, dict):
                raise ValueError(f"Agent '{agent_name}' configuration must be a dictionary")

            # Check for required fields
            if 'role' not in agent_config:
                logger.warning(f"Agent '{agent_name}' missing 'role' field")
            if 'llm' not in agent_config:
                raise ValueError(f"Agent '{agent_name}' missing required 'llm' field")
    
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

        Raises:
            ValueError: If agent configuration is invalid or missing
            RuntimeError: If LLM creation fails
        """
        # Check cache first
        if agent_name in self._llm_cache:
            logger.debug(f"Returning cached LLM instance for agent '{agent_name}'")
            return self._llm_cache[agent_name]

        try:
            model_name = self.get_llm_model_name(agent_name)
            thinking_enabled = self.get_thinking_parameter(agent_name)

            # Determine provider and create appropriate LLM instance
            if self._is_openai_model(model_name):
                llm_instance = self._create_openai_llm(model_name, agent_name)
            elif self._is_github_model(model_name):
                llm_instance = self._create_github_llm(model_name, agent_name)
            else:
                llm_instance = self._create_ollama_llm(model_name, agent_name, thinking_enabled)

            # Cache the instance
            self._llm_cache[agent_name] = llm_instance
            logger.info(f"Created and cached LLM instance for agent '{agent_name}': {model_name}")

            return llm_instance

        except Exception as e:
            logger.error(f"Failed to create LLM instance for agent '{agent_name}': {e}")
            raise RuntimeError(f"Failed to create LLM instance for agent '{agent_name}': {e}") from e

    def _is_openai_model(self, model_name: str) -> bool:
        """Check if the model is an OpenAI model"""
        return (model_name.startswith(OPENAI_MODEL_PREFIXES) or
                model_name in OPENAI_MODEL_NAMES)

    def _is_github_model(self, model_name: str) -> bool:
        """Check if the model is a GitHub Models model"""
        return model_name.startswith(GITHUB_MODEL_PREFIXES)

    def _create_openai_llm(self, model_name: str, agent_name: str) -> LLM:
        """Create an OpenAI LLM instance"""
        if not self.openai_api_key:
            raise ValueError(f"OpenAI API key not found in environment for agent '{agent_name}'. "
                           "Please set OPENAI_API_KEY environment variable.")

        llm_params = {
            "model": f"openai/{model_name}",
            "api_key": self.openai_api_key,
            "temperature": 0.7,
            "max_tokens": DEFAULT_MAX_TOKENS_OPENAI
        }

        return LLM(**llm_params)

    def _create_github_llm(self, model_name: str, agent_name: str) -> LLM:
        """Create a GitHub Models LLM instance"""
        if not self.github_token:
            raise ValueError(f"GitHub token not found in environment for agent '{agent_name}'. "
                           "Please set GITHUB_TOKEN environment variable with a personal access token "
                           "that has 'models: read' permission.")

        # GitHub Models uses OpenAI-compatible API format
        llm_params = {
            "model": f"openai/{model_name.replace('github/', '')}",  # Remove github/ prefix for API call
            "api_key": self.github_token,
            "base_url": self.github_base_url,
            "temperature": 0.7,
            "max_tokens": DEFAULT_MAX_TOKENS_OPENAI
        }

        return LLM(**llm_params)

    def _create_ollama_llm(self, model_name: str, agent_name: str, thinking_enabled: bool) -> LLM:
        """Create an Ollama LLM instance"""
        llm_params = {
            "model": f"ollama/{model_name}",
            "base_url": self.ollama_base_url,
        }

        # Configure model options
        model_options = ModelOptions(
            think=thinking_enabled,
            num_ctx=self.get_optimal_context_length(model_name),
            num_thread=self.get_optimal_thread_count()
        )

        # Convert to dictionary for CrewAI
        llm_params["model_kwargs"] = {"options": model_options.__dict__}

        return LLM(**llm_params)
    
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
        Optimized for memory-constrained systems

        Args:
            model_name: Name of the model

        Returns:
            Optimal context length
        """
        # Model-specific context optimizations for memory efficiency
        context_map = {
            # Small models (1.7B and below) - use smaller context to prevent OOM
            'qwen2.5:0.5b': 4096,
            'qwen2.5:1.5b': 4096,
            'qwen2.5:3b': 6144,
            'qwen3:1.7b': 4096,  # Reduced from 14746 to prevent OOM
            'phi3.5:3.8b': 4096,
            'llama3.2:1b': 4096,
            'gemma2:2b': 4096,
            # Medium models (7B range)
            'openhermes:v2.5': 6144,
            'mistral:7b': 6144,
            'llama3.2:3b': 6144,
            'llama3.1:7b': 6144,
            # Larger models - keep higher context but still reasonable
            'llama3.1:13b': 8192,
            'llama3.1:70b': 8192,
        }

        # Get context length for specific model, with fallback to safe default
        return context_map.get(model_name, 4096)

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
                timeout=DEFAULT_REQUEST_TIMEOUT
            )
            success = response.status_code == 200
            if success:
                logger.info(f"Successfully unloaded model: {model_name}")
            else:
                logger.warning(f"Failed to unload model {model_name}: HTTP {response.status_code}")
            return success
        except Exception as e:
            logger.warning(f"Could not unload model {model_name}: {e}")
            return False
    
    def get_loaded_models(self) -> List[str]:
        """
        Get list of currently loaded models in Ollama

        Returns:
            List of loaded model names
        """
        try:
            import requests
            response = requests.get(f"{self.ollama_base_url}/api/ps", timeout=CONNECTION_TIMEOUT)
            if response.status_code == 200:
                models_data = response.json()
                models = [model.get('name', '') for model in models_data.get('models', [])]
                logger.debug(f"Found {len(models)} loaded models: {models}")
                return models
        except Exception as e:
            logger.warning(f"Could not get loaded models: {e}")
        return []
    
    def cleanup_unused_models(self) -> None:
        """
        Unload models that are not currently in use
        """
        if not self.memory_optimization.auto_unload:
            logger.debug("Auto-unload disabled, skipping cleanup")
            return

        loaded_models = self.get_loaded_models()
        used_models = set(self.get_llm_model_name(agent) for agent in self._llm_cache.keys())

        unused_models = [model for model in loaded_models if model and model not in used_models]

        if unused_models:
            logger.info(f"Unloading {len(unused_models)} unused models: {unused_models}")
            for model in unused_models:
                logger.debug(f"Unloading unused model: {model}")
                self.unload_model(model)
        else:
            logger.debug("No unused models to clean up")
    
    def unload_all_models(self) -> Dict[str, bool]:
        """
        Unload all currently loaded models to free GPU memory

        Returns:
            Dictionary mapping model names to unload success status
        """
        loaded_models = self.get_loaded_models()
        results = {}

        if not loaded_models:
            logger.info("No models currently loaded")
            return results

        logger.info(f"Unloading all {len(loaded_models)} loaded models...")

        for model in loaded_models:
            if model:
                logger.debug(f"Unloading: {model}")
                success = self.unload_model(model)
                results[model] = success
                if success:
                    logger.debug(f"Successfully unloaded: {model}")
                else:
                    logger.warning(f"Failed to unload: {model}")

        # Clear LLM cache to force recreation next time
        self._llm_cache.clear()
        logger.debug("Cleared LLM cache")

        # Verify cleanup
        remaining_models = self.get_loaded_models()
        if remaining_models:
            logger.warning(f"{len(remaining_models)} models still loaded after cleanup: {remaining_models}")
        else:
            logger.info("All models successfully unloaded - GPU memory freed!")

        return results
    
    def force_cleanup_memory(self) -> bool:
        """
        Force cleanup of all models and cache - use after task completion

        Returns:
            True if cleanup was successful
        """
        try:
            logger.info("Starting comprehensive memory cleanup...")

            # Step 1: Unload all models
            unload_results = self.unload_all_models()

            # Step 2: Clear internal cache
            self._llm_cache.clear()

            # Step 3: Force garbage collection
            import gc
            collected = gc.collect()
            logger.debug(f"Garbage collector freed {collected} objects")

            # Step 4: Verify cleanup
            remaining_models = self.get_loaded_models()

            if not remaining_models:
                logger.info("Memory cleanup completed successfully!")
                return True
            else:
                logger.warning(f"Partial cleanup: {len(remaining_models)} models still loaded")
                return False

        except Exception as e:
            logger.error(f"Error during memory cleanup: {e}")
            return False
    
    def clear_cache(self) -> None:
        """
        Clear the LLM instance cache
        """
        cache_size = len(self._llm_cache)
        self._llm_cache.clear()
        logger.info(f"Cleared LLM cache ({cache_size} instances)")

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the current cache state

        Returns:
            Dictionary with cache statistics
        """
        return {
            'cached_instances': len(self._llm_cache),
            'cached_agents': list(self._llm_cache.keys()),
            'cache_enabled': True
        }

    def validate_connection(self) -> Dict[str, Any]:
        """
        Validate connections to Ollama and check API key status

        Returns:
            Dictionary with connection status information
        """
        return {
            'ollama_connected': self.validate_ollama_connection(),
            'openai_api_key_present': bool(self.openai_api_key),
            'github_token_present': bool(self.github_token),
            'config_file_exists': self.config_path.exists(),
            'config_loaded': self._agents_config is not None
        }


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