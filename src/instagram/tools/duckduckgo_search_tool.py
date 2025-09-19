from crewai.tools import BaseTool
from typing import Type, List, Dict, Any
from pydantic import BaseModel, Field
from ddgs import DDGS
import json


class DuckDuckGoSearchInput(BaseModel):
    """Input schema for DuckDuckGo Search Tool."""
    query: str = Field(..., description="The search query to search for on DuckDuckGo.")


class DuckDuckGoSearchTool(BaseTool):
    name: str = "DuckDuckGo Search"
    description: str = (
        "A search tool that uses DuckDuckGo to search the internet for information. "
        "Useful for finding current information, news, facts, and general web content. "
        "Input should be a search query string."
    )
    args_schema: Type[BaseModel] = DuckDuckGoSearchInput
    max_results: int = Field(default=5, description="Maximum number of search results to return")

    def _run(self, query: str) -> str:
        """
        Execute the DuckDuckGo search with the given query using the modern DDGS API.
        
        Args:
            query (str): The search query to execute
            
        Returns:
            str: The search results from DuckDuckGo formatted as text
        """
        try:
            # Initialize DDGS client
            with DDGS() as ddgs:
                # Perform text search with the updated API
                results = list(ddgs.text(
                    query=query,
                    max_results=self.max_results
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