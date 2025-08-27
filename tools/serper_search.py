import requests
import os
import time
from typing import List, Dict, Optional

def search_google(query: str, max_results: int = 5) -> List[Dict]:
    """
    Search Google using Serper API
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return
        
    Returns:
        List of search result dictionaries with keys: title, url, snippet
    """
    serper_api_key = os.getenv('SERPER_API_KEY')
    
    if not serper_api_key:
        print("  No Serper API key found - returning empty results")
        return []
    
    try:
        print(f"  Searching: {query}")
        
        # Serper API request
        response = requests.post(
            'https://google.serper.dev/search',
            headers={
                'X-API-KEY': serper_api_key,
                'Content-Type': 'application/json'
            },
            json={'q': query, 'num': max_results}
        )
        
        if response.status_code == 200:
            data = response.json()
            results = []
            
            # Process organic results
            for result in data.get('organic', [])[:max_results]:
                search_result = {
                    'title': result.get('title', ''),
                    'url': result.get('link', ''),
                    'snippet': result.get('snippet', '')
                }
                results.append(search_result)
            
            # Small delay to be respectful to API
            time.sleep(1)
            return results
            
        else:
            print(f"  Serper API error: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"  Error searching '{query}': {e}")
        return []