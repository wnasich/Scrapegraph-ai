"""
Research_web module
"""
import re
from typing import List
from langchain_community.tools import DuckDuckGoSearchResults
from googlesearch import search as google_search
import requests
from bs4 import BeautifulSoup

def search_on_web(query: str, search_engine: str = "Google", 
                  max_results: int = 10, port: int = 8080) -> List[str]:
    """
    Searches the web for a given query using specified search engine options.

    Args:
        query (str): The search query to find on the internet.
        search_engine (str, optional): Specifies the search engine to use, 
        options include 'Google', 'DuckDuckGo', 'Bing', or 'SearXNG'. Default is 'Google'.
        max_results (int, optional): The maximum number of search results to return.
        port (int, optional): The port number to use when searching with 'SearXNG'. Default is 8080.

    Returns:
        List[str]: A list of URLs as strings that are the search results.

    Raises:
        ValueError: If the search engine specified is not supported.

    Example:
        >>> search_on_web("example query", search_engine="Google", max_results=5)
        ['http://example.com', 'http://example.org', ...]
    """

    if search_engine.lower() == "google":
        res = []
        for url in google_search(query, stop=max_results):
            res.append(url)
        return res

    elif search_engine.lower() == "duckduckgo":
        research = DuckDuckGoSearchResults(max_results=max_results)
        res = research.run(query)
        links = re.findall(r'https?://[^\s,\]]+', res)
        return links

    elif search_engine.lower() == "bing":
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        search_url = f"https://www.bing.com/search?q={query}"
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        search_results = []
        for result in soup.find_all('li', class_='b_algo', limit=max_results):
            link = result.find('a')['href']
            search_results.append(link)
        return search_results

    elif search_engine.lower() == "bing-api":

        azureBingSearchKey='???????????????????????'
        headers = {
            "Ocp-Apim-Subscription-Key": azureBingSearchKey
        }

        params = {
            'mkt': 'en-CA',
            'setLang': 'en-CA',
            'responseFilter': 'Webpages',
            'count': max_results,
            'q': query,
        }

        response = requests.get('https://api.bing.microsoft.com/v7.0/search', headers=headers, params=params)
        response.raise_for_status()
        search_results = response.json()

        urls = []
        if 'webPages' in search_results:
            actualUrls = []
            for value in search_results['webPages']['value']:
                if 'url' in value:
                    urls.append(value['url'])

                if 'cachedPageUrl' in value:
                    urls.append(value['cachedPageUrl'])

                actualUrls.append(value['url'])

            print(actualUrls)

        return urls

    elif search_engine.lower() == "searxng":
        url = f"http://localhost:{port}"
        params = {"q": query, "format": "json"}

        response = requests.get(url, params=params)

        data = response.json()
        limited_results = data["results"][:max_results]
        return limited_results

    else:
        raise ValueError("""The only search engines available are 
                         DuckDuckGo, Google, Bing, or SearXNG""")
