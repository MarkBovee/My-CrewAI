from crewai.tools import tool
from ddgs import DDGS
import json
from helpers.knowledge_helper import store_web_results


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
            return "No search results found for the query."
            
        # Store results as knowledge for future reference
        store_web_results(query, results)
        
        # Format results for better readability
        formatted_results = []
        for i, result in enumerate(results, 1):
            title = result.get('title', 'No Title')
            body = result.get('body', 'No Description')
            href = result.get('href', 'No URL')
            
            formatted_result = f"""
{i}. **{title}**
   {body}
   URL: {href}
"""
            formatted_results.append(formatted_result)
        
        final_output = f"""
# Search Results for: "{query}"

Found {len(results)} results:
{''.join(formatted_results)}

---
*Results stored in knowledge base for future reference*
"""
        
        return final_output.strip()
        
    except Exception as e:
        error_msg = f"Error performing search: {str(e)}"
        print(f"Search tool error: {error_msg}")
        return f"Search failed: {error_msg}"