import requests
import functions
import json 

name = 'web-request'
tool = functions.multi_text_function('web-request', 'submit a call to the python requests libary', ('method', 'http method'), ('url', 'url to request to'), ('headers', 'json formatted string containing http headers'), ('json', 'json formatted string containing request body. if none, set this to empty string'))

def function(args):
    return json.dumps(requests.request(args['method'], args['url'], headers=json.loads(args['headers']), json=json.loads(args['json'])))
    
    
