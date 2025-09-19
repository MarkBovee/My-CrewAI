from crewai.tools import tool
from ddgs import DDGS
import json


@tool("DuckDuckGo Search")
def search_tool(query: str) -> str:
    """
    A search tool that uses DuckDuckGo to search the internet for information.
    Useful for finding current information, news, facts, and general web content.
    
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