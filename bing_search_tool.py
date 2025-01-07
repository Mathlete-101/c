import functions
import requests
import json

ENDPOINT = 'https://api.bing.microsoft.com/v7.0/search'

def transform_searchResponse(search_result):
    results = []
    searchResponse = json.loads(search_result)
    for webPage in searchResponse['webPages']['value']:
        results.append({k: v for k, v in webPage.items() if k in ['url', 'snippet', 'name']})
    return json.dumps(results)
        
    

class bing_search_tool:
    tool = functions.text_function("bing-search", "perform a web search using bing")
    def __init__(self, key):
        self.key = key

    def __call__(self, args):
        params = {'q': args['text'], 'count': 5, 'offset': 0, 'mkt': 'en-US', 'safesearch': 'Moderate'}
        headers = {'Ocp-Apim-Subscription-Key': self.key}
        response = requests.get(ENDPOINT, headers=headers, params=params)
        return f"code: {response.status_code} text: {transform_searchResponse(response.text) if response.status_code == 200 else response.text}"
        
    
