#a file for holding things related to chat functions

def text_function(name, description, tdescrip="the input text"):
    return {
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "descripion": tdescrip
                        }
                    }
                }
            }
        }

def nilad(name, description):
    return {
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": {
                    "type": "object",
                    "properties": {
                    }
                }
            }
        }
        
        


def multi_text_function(name, description, *parameter):
    return {
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        p_name: {
                            "type": "string",
                            "descripion": p_desc
                        }
                        for p_name, p_desc in parameter 
                    }
                }
            }
        }
