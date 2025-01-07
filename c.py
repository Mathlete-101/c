#!/bin/python
from openai import OpenAI
import json
import os
from datetime import datetime
import sys
import subprocess
import time
from colorama import Fore, Back, Style

import functions
import forgetful_goose
import command_runner
from bing_search_tool import bing_search_tool

class colors:
    chat = Fore.CYAN
    user = Fore.WHITE
    output = Fore.MAGENTA
    file = Fore.RED

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
    print(f"{colors.chat}chat> {content}")
    return content

        
        

            

prompts = {
        "write_command": "The user will give you a task to complete in the terminal. Respond with only the command as it would be typed, no extra formatting. If you cannot complete this task, begin your response with a '/' and explain why if you believe it would be useful."
}



def file_function(name, description, *parameter):
    return multi_text_function(f"file-{name}", description, *((("filename", "the name of the target file"),) + parameter))
    

tool_dict = {
    "execute": "execute text as a command on the system.",
    "thought": "think about what you need to do. The user does not see this.",
    "finish": "print text if you think if you have completed the task or require user input to make further progress.",
}


tools = [functions.text_function(k, v) for k, v in tool_dict.items()]
if "bing_api_key" in conf.keys():
    tools.append(bing_search_tool.tool)
#tools += file_accessor.file_tools
tools.append(functions.multi_text_function("write_file", "writes the provided text to the provided file path.", ("path", "the location to write the text to"), ("text", "the text to write")))


        

def cmd_exec(command):
    print(colors.output)
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
elif a1 in ("-i", "-ii", "-c"):
            
    request = " ".join(sys.argv[2:])

    client = OpenAI(api_key=conf["api_key"])
    
    goose = forgetful_goose.forgetful_goose(client, conf["models"]["interactive"], messages = [
            {"role": "system", "content": """The user will give you task to complete in the command line. Use the provided tools to complete it."""},
            {"role": "system", "content": f"Information you may find useful about the user: {conf['notes']} "},
            {"role": 'user', "content": request}
    ], tools=tools)
    action = ""
    agent_loop = True

    tool_functions = {}
    if "bing_api_key" in conf:
        tool_functions['bing-search'] = bing_search_tool(conf["bing_api_key"])

    while agent_loop:
        print()
        goose.quack()

        message = goose.last
        for call in message.tool_calls:
            action = call.function.name.strip()
            text = json.loads(call.function.arguments)["text"]

            response = {"role": "tool", "tool_call_id": call.id, "content":""}

            print(f"{colors.chat}chat> {text}")
            
            if a1 == "-ii":
                if input("press enter to continue"):
                    break
            
            if action == "execute":
                response["content"] = cmd_exec(text)
                print(response["content"])

            if action in tool_functions.keys():
                response["content"] = tool_functions[action](json.loads(call.function.arguments))
                print(response["content"])

            goose(response)

            if action == "finish":
                userInput = input(f"{colors.user}user> ")
                if userInput == "":
                     agent_loop = False
                else:
                    goose({"role": "user", "content": userInput})

    corpse = goose.body()
    
    os.makedirs("graveyard", exist_ok=True)
    for f in ["latest", f"graveyard/{datetime.now().strftime('%Y%m%d_%H%M%S')}"]:
        with open(f, 'w') as file:
            json.dump(corpse, file)

    
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

