"""
Knowledge Helper for CrewAI
Manages web search results storage and article memory tracking using CrewAI knowledge system
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource
from crewai.knowledge.source.json_knowledge_source import JSONKnowledgeSource


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
            self.project_root = Path(__file__).parent.parent.parent.parent
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
    
    def get_web_results_knowledge_source(self) -> StringKnowledgeSource:
        """
        Create a StringKnowledgeSource from stored web search results
        
        Returns:
            StringKnowledgeSource for web search results
        """
        try:
            # Load and format web search results as string
            data = self._load_json_file(self.web_results_file)
            
            content_parts = ["# Web Search Results Knowledge Base\n"]
            
            for search in data.get('searches', []):
                content_parts.append(f"## Search: {search.get('query', 'Unknown')}")
                content_parts.append(f"Date: {search.get('timestamp', 'Unknown')}")
                content_parts.append(f"Results Count: {search.get('results_count', 0)}\n")
                
                for i, result in enumerate(search.get('results', []), 1):
                    content_parts.append(f"### Result {i}: {result.get('title', 'Untitled')}")
                    content_parts.append(f"URL: {result.get('link', 'No URL')}")
                    content_parts.append(f"Content: {result.get('snippet', 'No content')}\n")
            
            content = "\n".join(content_parts)
            
            return StringKnowledgeSource(
                content=content,
                metadata={"source": "web_search_results", "type": "search_data"}
            )
        except Exception as e:
            # Return empty knowledge source if file doesn't exist or has issues
            return StringKnowledgeSource(
                content="# Web Search Results\n\nNo web search data available.",
                metadata={"source": "web_search_results", "type": "search_data", "error": str(e)}
            )
    
    def store_article_memory(self, topic: str, article_path: str, post_path: str = "") -> bool:
        """
        Store information about a completed article to prevent topic repetition
        
        Args:
            topic: Main topic/subject of the article
            article_path: Path to the generated article file
            post_path: Path to the generated post file (optional)
            
        Returns:
            True if stored successfully
        """
        try:
            # Load existing data
            data = self._load_json_file(self.article_memory_file)
            
            # Create new article entry
            article_entry = {
                "timestamp": datetime.now().isoformat(),
                "topic": topic,
                "topic_keywords": self._extract_keywords(topic),
                "article_path": article_path,
                "post_path": post_path,
                "status": "completed"
            }
            
            # Add to articles list
            if "articles" not in data:
                data["articles"] = []
            if "topics_covered" not in data:
                data["topics_covered"] = []
            
            data["articles"].append(article_entry)
            
            # Add topic to covered topics (for quick lookup)
            topic_lower = topic.lower().strip()
            if topic_lower not in [t.lower() for t in data["topics_covered"]]:
                data["topics_covered"].append(topic_lower)
            
            data["last_updated"] = datetime.now().isoformat()
            
            # Save updated data
            self._save_json_file(self.article_memory_file, data)
            
            print(f"📖 Stored article memory: '{topic}'")
            return True
            
        except Exception as e:
            print(f"❌ Error storing article memory: {e}")
            return False
    
    def _extract_keywords(self, topic: str) -> List[str]:
        """Extract keywords from topic for better matching"""
        # Simple keyword extraction - split and clean
        import re
        
        # Remove common stop words and clean text
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'how', 'what', 'when', 'where', 'why'}
        
        # Extract words, convert to lowercase, remove short words
        words = re.findall(r'\b[a-zA-Z]+\b', topic.lower())
        keywords = [word for word in words if len(word) > 2 and word not in stop_words]
        
        return keywords[:10]  # Limit to 10 keywords
    
    def check_topic_covered(self, topic: str, similarity_threshold: float = 0.7) -> Dict[str, Any]:
        """
        Check if a topic has been covered before
        
        Args:
            topic: Topic to check
            similarity_threshold: Threshold for considering topics similar (0.0-1.0)
            
        Returns:
            Dictionary with coverage info: {'covered': bool, 'similar_articles': List, 'recommendation': str}
        """
        try:
            data = self._load_json_file(self.article_memory_file)
            
            if not data.get("articles"):
                return {
                    'covered': False,
                    'similar_articles': [],
                    'recommendation': 'No previous articles found - topic is fresh!'
                }
            
            topic_keywords = set(self._extract_keywords(topic))
            similar_articles = []
            
            for article in data["articles"]:
                article_keywords = set(article.get("topic_keywords", []))
                
                # Calculate similarity based on keyword overlap
                if topic_keywords and article_keywords:
                    overlap = len(topic_keywords & article_keywords)
                    similarity = overlap / len(topic_keywords | article_keywords)
                    
                    if similarity >= similarity_threshold:
                        similar_articles.append({
                            'topic': article['topic'],
                            'similarity': round(similarity, 2),
                            'timestamp': article['timestamp'],
                            'article_path': article['article_path']
                        })
            
            # Sort by similarity
            similar_articles.sort(key=lambda x: x['similarity'], reverse=True)
            
            covered = len(similar_articles) > 0
            
            if covered:
                recommendation = f"Topic may be too similar to {len(similar_articles)} previous article(s). Consider a different angle or more specific focus."
            else:
                recommendation = "Topic appears fresh and unique - good to proceed!"
            
            return {
                'covered': covered,
                'similar_articles': similar_articles[:3],  # Top 3 most similar
                'recommendation': recommendation
            }
            
        except Exception as e:
            print(f"❌ Error checking topic coverage: {e}")
            return {
                'covered': False,
                'similar_articles': [],
                'recommendation': 'Error checking coverage - proceeding with caution'
            }
    
    def get_article_memory_knowledge_source(self) -> StringKnowledgeSource:
        """
        Create a StringKnowledgeSource from article memory
        
        Returns:
            StringKnowledgeSource for article memory
        """
        try:
            # Load and format article memory as string
            data = self._load_json_file(self.article_memory_file)
            
            content_parts = ["# Article Memory Knowledge Base\n"]
            content_parts.append(f"Last Updated: {data.get('last_updated', 'Unknown')}")
            content_parts.append(f"Total Articles: {len(data.get('articles', []))}")
            content_parts.append(f"Topics Covered: {len(data.get('topics_covered', []))}\n")
            
            # Add covered topics
            if data.get('topics_covered'):
                content_parts.append("## Previously Covered Topics:")
                for topic in data.get('topics_covered', []):
                    content_parts.append(f"- {topic}")
                content_parts.append("")
            
            # Add article details
            if data.get('articles'):
                content_parts.append("## Article History:")
                for i, article in enumerate(data.get('articles', []), 1):
                    content_parts.append(f"### Article {i}: {article.get('topic', 'Unknown Topic')}")
                    content_parts.append(f"Date: {article.get('timestamp', 'Unknown')}")
                    content_parts.append(f"Status: {article.get('status', 'Unknown')}")
                    content_parts.append(f"Keywords: {', '.join(article.get('topic_keywords', []))}")
                    content_parts.append("")
            
            content = "\n".join(content_parts)
            
            return StringKnowledgeSource(
                content=content,
                metadata={"source": "article_memory", "type": "article_history"}
            )
        except Exception as e:
            # Return empty knowledge source if file doesn't exist or has issues
            return StringKnowledgeSource(
                content="# Article Memory\n\nNo article history available.",
                metadata={"source": "article_memory", "type": "article_history", "error": str(e)}
            )
    
    def create_search_results_string_knowledge(self, search_query: str, results: List[Dict[str, Any]], 
                                             task_topic: str = "") -> StringKnowledgeSource:
        """
        Create a StringKnowledgeSource from current search results for immediate use
        
        Args:
            search_query: The search query used
            results: List of search results
            task_topic: Topic being researched
            
        Returns:
            StringKnowledgeSource with formatted search results
        """
        # Format search results as readable text
        content = f"Search Results for: {search_query}\n"
        content += f"Topic: {task_topic}\n"
        content += f"Timestamp: {datetime.now().isoformat()}\n"
        content += f"Results Count: {len(results)}\n\n"
        
        for i, result in enumerate(results, 1):
            content += f"Result {i}:\n"
            content += f"Title: {result.get('title', 'No title')}\n"
            content += f"Link: {result.get('link', 'No link')}\n"
            content += f"Snippet: {result.get('snippet', 'No snippet')}\n"
            content += "-" * 50 + "\n\n"
        
        return StringKnowledgeSource(content=content)
    
    def get_knowledge_stats(self) -> Dict[str, Any]:
        """
        Get statistics about stored knowledge
        
        Returns:
            Dictionary with knowledge statistics
        """
        try:
            web_data = self._load_json_file(self.web_results_file)
            article_data = self._load_json_file(self.article_memory_file)
            
            stats = {
                'web_searches_stored': len(web_data.get('searches', [])),
                'articles_completed': len(article_data.get('articles', [])),
                'topics_covered': len(article_data.get('topics_covered', [])),
                'knowledge_files_exist': {
                    'web_results': self.web_results_file.exists(),
                    'article_memory': self.article_memory_file.exists()
                },
                'last_web_search': web_data.get('last_updated', 'Never'),
                'last_article': article_data.get('last_updated', 'Never')
            }
            
            return stats
            
        except Exception as e:
            return {'error': str(e)}
    
    def reset_article_memory(self) -> bool:
        """
        Reset article memory to start fresh with topic checking
        
        Returns:
            True if reset successful
        """
        try:
            print("🔄 Resetting article memory...")
            self._save_json_file(self.article_memory_file, {
                "articles": [],
                "topics_covered": [],
                "last_updated": datetime.now().isoformat(),
                "description": "Article memory tracking to prevent topic repetition"
            })
            print("✅ Article memory reset successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error resetting article memory: {e}")
            return False
    
    def reset_web_search_results(self) -> bool:
        """
        Reset web search results storage
        
        Returns:
            True if reset successful
        """
        try:
            print("🔄 Resetting web search results...")
            self._save_json_file(self.web_results_file, {
                "searches": [],
                "last_updated": datetime.now().isoformat(),
                "description": "Web search results storage for CrewAI knowledge system"
            })
            print("✅ Web search results reset successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error resetting web search results: {e}")
            return False
    
    def reset_all_knowledge(self) -> bool:
        """
        Reset all knowledge data (article memory and web search results)
        
        Returns:
            True if all resets successful
        """
        print("🔄 Resetting ALL knowledge data...")
        article_reset = self.reset_article_memory()
        web_reset = self.reset_web_search_results()
        
        if article_reset and web_reset:
            print("✅ All knowledge data reset successfully!")
            return True
        else:
            print("⚠️ Some reset operations failed")
            return False


# Convenience functions
def store_web_results(search_query: str, results: List[Dict[str, Any]], task_topic: str = "") -> bool:
    """Convenience function to store web search results"""
    helper = KnowledgeHelper()
    return helper.store_web_search_results(search_query, results, task_topic)


def store_article_completion(topic: str, article_path: str, post_path: str = "") -> bool:
    """Convenience function to store article completion"""
    helper = KnowledgeHelper()
    return helper.store_article_memory(topic, article_path, post_path)


def check_topic_similarity(topic: str) -> Dict[str, Any]:
    """Convenience function to check topic similarity"""
    helper = KnowledgeHelper()
    return helper.check_topic_covered(topic)


def reset_topic_check() -> bool:
    """Convenience function to reset article memory (topic checking)"""
    helper = KnowledgeHelper()
    return helper.reset_article_memory()


def reset_web_knowledge() -> bool:
    """Convenience function to reset web search results"""
    helper = KnowledgeHelper()
    return helper.reset_web_search_results()


def reset_all_knowledge() -> bool:
    """Convenience function to reset all knowledge data"""
    helper = KnowledgeHelper()
    return helper.reset_all_knowledge()


# Example usage
if __name__ == "__main__":
    helper = KnowledgeHelper()
    
    print("📚 Knowledge Helper Statistics:")
    stats = helper.get_knowledge_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Example: Check if a topic has been covered
    test_topic = "AI and Machine Learning in Healthcare"
    coverage = helper.check_topic_covered(test_topic)
    print(f"\n🔍 Coverage check for '{test_topic}':")
    print(f"  Covered: {coverage['covered']}")
    print(f"  Recommendation: {coverage['recommendation']}")
    
    if coverage['similar_articles']:
        print("  Similar articles:")
        for article in coverage['similar_articles']:
            print(f"    - {article['topic']} (similarity: {article['similarity']})")