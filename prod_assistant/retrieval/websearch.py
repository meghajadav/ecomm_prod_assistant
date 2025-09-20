from tavily import TavilyClient
from dotenv import load_dotenv
import os

class WebSearch:
    def __init__(self):
        self._load_env_variables()
        # self.client = TavilyClient()

    def _load_env_variables(self):
        load_dotenv()
        required_variables=['TAVILY_API_KEY']
        missing_var = [var for var in required_variables if os.getenv(var) is None]

        if missing_var:
           raise EnvironmentError(f"environment variable missing: {missing_var}")
        self.client = TavilyClient(os.getenv('TAVILY_API_KEY') )

    def search(self, query:str, max_results:int=3):
        results = self.client.search(query, max_results=max_results)
        if not results or 'results' not in results:
            return 'No relevant web results found.'
        
        formatted_chunks =[]
        for r in results['results']:
            formatted = (
                f"Title: {r.get('title','N/A')}\n",
                f"URL: {r.get('url','N/A')}\n",
                f"Content: {r.get('content','N/A')}\n"
            )
            formatted_chunks.append(formatted)
        return '\n\n-------------\n\n'.join(formatted_chunks)