"""
Knowledge Helper for CrewAI
Manages web search results storage and article memory tracking using CrewAI knowledge system
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional


class KnowledgeHelper:
    """Helper class for managing CrewAI knowledge sources - web results and article memory"""
    
    def __init__(self, project_root: Optional[str] = None):
        """
        Initialize the Knowledge helper
        
        Args:
            project_root: Root directory of the project (defaults to detected root)
        """
        if project_root is None:
            # Auto-detect project root - go up from helpers to project root
            self.project_root = Path(__file__).parent.parent.parent.parent.parent
        else:
            self.project_root = Path(project_root)
        
        self.knowledge_dir = self.project_root / "knowledge"
        self.output_dir = self.project_root / "output"
        
        # Ensure directories exist
        self.knowledge_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        (self.output_dir / "articles").mkdir(exist_ok=True)
        (self.output_dir / "posts").mkdir(exist_ok=True)
        
        # Knowledge files
        self.web_results_file = self.knowledge_dir / "web_search_results.json"
        self.article_memory_file = self.knowledge_dir / "article_memory.json"
        
        # Initialize files if they don't exist
        self._initialize_knowledge_files()
    
    def _initialize_knowledge_files(self):
        """Initialize knowledge files if they don't exist"""
        if not self.web_results_file.exists():
            self._save_json_file(self.web_results_file, {
                "searches": [],
                "last_updated": datetime.now().isoformat(),
                "description": "Web search results storage for CrewAI knowledge system"
            })
        
        if not self.article_memory_file.exists():
            self._save_json_file(self.article_memory_file, {
                "articles": [],
                "topics_covered": [],
                "last_updated": datetime.now().isoformat(),
                "description": "Article memory tracking to prevent topic repetition"
            })
    
    def _save_json_file(self, file_path: Path, data: Dict[str, Any]):
        """Save data to JSON file safely"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving {file_path}: {e}")
    
    def _load_json_file(self, file_path: Path) -> Dict[str, Any]:
        """Load data from JSON file safely"""
        try:
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
        return {}
    
    def store_web_search_results(self, search_query: str, results: List[Dict[str, Any]], 
                                task_topic: str = "") -> bool:
        """
        Store web search results as knowledge for future reference
        
        Args:
            search_query: The search query used
            results: List of search results (title, link, snippet)
            task_topic: Topic being researched for context
            
        Returns:
            True if stored successfully
        """
        try:
            # Load existing data
            data = self._load_json_file(self.web_results_file)
            
            # Create new search entry
            search_entry = {
                "timestamp": datetime.now().isoformat(),
                "query": search_query,
                "topic": task_topic,
                "results_count": len(results),
                "results": results
            }
            
            # Add to searches list
            if "searches" not in data:
                data["searches"] = []
            
            data["searches"].append(search_entry)
            data["last_updated"] = datetime.now().isoformat()
            
            # Keep only last 50 searches to prevent file bloat
            if len(data["searches"]) > 50:
                data["searches"] = data["searches"][-50:]
            
            # Save updated data
            self._save_json_file(self.web_results_file, data)
            
            print(f"📚 Stored web search results: '{search_query}' ({len(results)} results)")
            return True
            
        except Exception as e:
            print(f"❌ Error storing web search results: {e}")
            return False


# Convenience function for use by tools
def store_web_results(search_query: str, results: List[Dict[str, Any]], task_topic: str = "") -> bool:
    """
    Convenience function to store web search results
    
    Args:
        search_query: The search query used
        results: List of search results
        task_topic: Topic being researched
        
    Returns:
        True if stored successfully
    """
    helper = KnowledgeHelper()
    return helper.store_web_search_results(search_query, results, task_topic)