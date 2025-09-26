"""
LLM Helper for CrewAI - Experience Blog Flow
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

                self._agents_config = config
                logger.debug(f"Successfully loaded agents config from {self.config_path}")

            except yaml.YAMLError as e:
                raise ValueError(f"Error parsing agents.yaml: {e}")
            except Exception as e:
                raise RuntimeError(f"Unexpected error loading config: {e}")

        return self._agents_config
    
    def get_llm_model_name(self, agent_name: str) -> str:
        """
        Get the LLM model name for a specific agent
        
        Args:
            agent_name: Name of the agent (e.g., 'coach', 'researcher', 'writer')
            
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
        """
        context_map = {
            'qwen2.5:0.5b': 4096,
            'qwen2.5:1.5b': 4096,
            'qwen2.5:3b': 6144,
            'qwen3:1.7b': 4096,
            'phi3.5:3.8b': 4096,
            'llama3.2:1b': 4096,
            'gemma2:2b': 4096,
            'openhermes:v2.5': 6144,
            'mistral:7b': 6144,
            'llama3.2:3b': 6144,
            'llama3.1:7b': 6144,
            'llama3.1:13b': 8192,
            'llama3.1:70b': 8192,
        }

        return context_map.get(model_name, 4096)

    def get_optimal_thread_count(self) -> int:
        """Get optimal thread count based on CPU cores"""
        try:
            import os
            cpu_count = os.cpu_count() or 4
            return max(2, min(8, cpu_count // 2))
        except Exception:
            return 4


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