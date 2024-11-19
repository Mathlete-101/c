#!/bin/python
from openai import OpenAI
import json
import sys
import subprocess
import command_runner
import time

#path_base = "/mnt/adit/.tools/c/"
path_base = "/home/njensen/.tools/c_command/"

def message(role, text):
    return {"role": role, "content": text}
def system(text):
    return message("role", text)
def user(text):
    return message("user", text)



def oops():
    print("""
            c - make chat write the command

            prepend command with * to dry run
            
            settings: use one of these at a time to change the settings of the program
            -k <api_key>: set the api key or print the current one
            -m: print the current models being used
            -m <model name>: set the model or print the current one
            -m [command|interactive|file] <model name>: set the model for each use case
            -n: print the notes
            -n <key>: delete note with key <key>
            -n <key> <value>: set note with key <key> to value <value>
          """)
    exit()


try:
    with open(path_base + "conf.json") as file:
        conf = json.load(file)
except FileNotFoundError:
    conf = {"api_key": "", "models": {"command": "gpt-4o-mini", "interactive": "gpt-4o-mini", "file": "gpt-4o-mini"}, "notes":{"shell": "bash", "system": "linux"}}


def ask_chat(request, sys):
    client = OpenAI(api_key=conf["api_key"])
    completion = client.chat.completions.create(
            model = conf["models"]["command"],
            messages = [
                {"role": "system", "content": f"Information about the user: {conf['notes']}"},
                {"role": "system", "content": sys},
                {"role": "user", "content": request}
            ]
        )
    content = completion.choices[0].message.content
    print(f"chat> {content}")
    return content

class file_handler:
    def __init__(self, client, filename, source="", text=""):
        self.client = client
        self.source = source
        self.text = text
        self.filename = filename
        if text == "" and source != "":
            self.read()
        self.messages = [system("Your job is to understand the following file, respond to requests about its content and write it. The text is contained in the next system message."), system(self.text)]

    def read(self):
        try:
            with open(text, "r") as file:
                self.text = file.read()
        except FileNotFoundError:
            pass


    def write(self):
        try:
            with open(text, "w") as file:
                file.write(text)
        except FileNotFoundError:
            pass
            #if a file doesn't have a valid wource, just don't write it, it's fine


    def query(self, query):
        messages.append(user(query)) 
        message = client.chat.completions.create(model = conf["models"]["command"], messages=messages).choices[0].message
        print(f"file {filename}>t {message.content}")
        messages.append(message)
        return message.content
        
        

            

prompts = {
        "write_command": "The user will give you a task to complete in the terminal. Respond with only the command as it would be typed, no extra formatting. If you cannot complete this task, begin your response with a '/' and explain why if you believe it would be useful."
}


def text_function(name, description):
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
                            "descripion": "the input text"
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

def file_function(name, description, *parameter):
    return multi_text_function(f"file-{name}", desscription, *(["filename", "the name of the target file"] + parameter))
    

tool_dict = {
    "execute": "execute text as a command on the system.",
    "thought": "think about what you need to do. The user does not see this.",
    "ask": "ask the user a question. If you think you know what the user wants or can figure it out by looking around, do that instead.",
    "finish": "print text and terminate if you have completed the task or can make no more progress on it.",
    "file-open": "access a file on the system",
}
tools = [text_function(k, v) for k, v in tool_dict.items()]
#tools += [
#        file_function("query", "request information about the file using natural language.", ("query", "the request query")),
#        file_function("fulltext", "request the full text of the file. Do not use this function unless absolutely nessecary.")
#]
#tools += [
#        nilad("file-list_open")
#]


        

def cmd_exec(command):
    return command_runner.attempt_4(command)

#run the dry run command, if no other args were passed
if len(sys.argv) == 1:
    try:
        with open(path_base + "dry_run", "r") as file:
            cmd_exec(file.read())
            exit()
    except FileNotFoundError:
        print("No command to run found.")

a1 = sys.argv[1]
main_settings = {
        "k": "api_key",
}

#normal settings
if len(a1) == 2 and a1[0] == "-" and a1[1:] in main_settings.keys():
    if len(sys.argv) > 2:
        conf[main_settings[a1[1]]] = sys.argv[2]
    else:
        print(conf[main_settings[a1[1]]])

#models
elif a1 == "-m":
    if len(sys.argv) == 2:
        print(conf["models"])
    elif len(sys.argv) == 3:
        conf["models"] = {k: sys.argv[2] for k in conf["models"].keys()}
    elif len(sys.argv) == 4:
        conf["models"][sys.argv[2]] = sys.argv[3]

#notes
elif a1 == "-n":
    if len(sys.argv) == 2:
        print(conf["notes"])
    elif len(sys.argv) == 3:
        conf["notes"].pop(sys.argv[2])
    else:
        conf["notes"][sys.argv[2]] = sys.argv[3]

#help
elif a1 == "-h":
    oops()


#terrifying mode
elif a1 in ("-i", "-ii"):
    request = " ".join(sys.argv[2:])

    client = OpenAI(api_key=conf["api_key"])

    messages=[
            {"role": "system", "content": """The user will give you task to complete in the command line. Use the provided tools to complete it."""},
            {"role": "system", "content": f"Information you may find useful about the user: {conf['notes']} "},
            {"role": 'user', "content": request}
    ]
    action = ""
    while True:
        print()
        completion = client.chat.completions.create(model=conf["models"]["interactive"], messages = messages, tools=tools, tool_choice="required")

        message = completion.choices[0].message
        messages.append(message)
        for call in message.tool_calls:
            action = call.function.name.strip()
            text = json.loads(call.function.arguments)["text"]

            response = {"role": "tool", "tool_call_id": call.id, "content":""}

            print(f"chat> {text}")
            
            if action == "ask":
                response["content"] = input("user>")
            elif action == "say" or action == "thought" or action == "finish":
                pass # already printed
            
            if a1 == "-ii":
                if input("press enter to continue"):
                    exit()
            
            if action == "execute":
                response["content"] = cmd_exec(text)
                print(response["content"])

            messages.append(response)

            if action == "finish":
                userInput = input("user>")
                if userInput == "":
                    exit()
                else:
                    messages.append({"role": "user", "content": userInput})
    exit()
    

#completions
else:
    request = " ".join(sys.argv[1:])
    dry_run = a1[0] == "*"
    if dry_run:
        request = request[1:]
        
    response = ask_chat(request, prompts["write_command"])
    
    if response[0] != "/":
        if dry_run:
            with open(path_base + "dry_run", "w") as file:
                file.write(response)
        else:
            print(cmd_exec(response))

#write the config file
with open(path_base + "conf.json", "w") as file:
    json.dump(conf, file)

