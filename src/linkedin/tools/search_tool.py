from crewai.tools import tool
from ddgs import DDGS
import json
from ..helpers.knowledge_helper import store_web_results


@tool("DuckDuckGo Search")
def search_tool(query: str) -> str:
    """
    A search tool that uses DuckDuckGo to search the internet for information.
    Useful for finding current information, news, facts, and general web content.
    Also stores search results as knowledge for future reference.
    
    Args:
        query (str): The search query to search for on DuckDuckGo
        
    Returns:
        str: The search results from DuckDuckGo formatted as text
    """
    max_results = 5
    
    try:
        # Initialize DDGS client
        with DDGS() as ddgs:
            # Perform text search with the updated API
            results = list(ddgs.text(
                query=query,
                max_results=max_results
            ))
            
            if not results:
                return f"No search results found for query: {query}"
            
            # Store results as knowledge for future reference
            try:
                # Convert results to standardized format for knowledge storage
                knowledge_results = []
                for result in results:
                    knowledge_results.append({
                        'title': result.get('title', 'No title'),
                        'snippet': result.get('body', 'No description'),
                        'link': result.get('href', 'No URL')
                    })
                
                # Store with knowledge helper
                store_web_results(query, knowledge_results, task_topic=query)
                print(f"📚 Stored {len(knowledge_results)} search results in knowledge base")
                
            except Exception as e:
                print(f"⚠️ Warning: Could not store search results as knowledge: {e}")
            
            # Format results as readable text
            formatted_results = []
            for i, result in enumerate(results, 1):
                title = result.get('title', 'No title')
                body = result.get('body', 'No description')
                url = result.get('href', 'No URL')
                
                formatted_result = f"{i}. {title}\n{body}\nURL: {url}\n"
                formatted_results.append(formatted_result)
            
            return "\n".join(formatted_results)
            
    except Exception as e:
        return f"Error performing search: {str(e)}. Please try again with a different query."