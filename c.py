#!/bin/python
from openai import OpenAI
import json
import sys
import subprocess
import command_runner
import time

path_base = "/home/njensen/.tools/c_command/"

def oops():
    print("""
            c - make chat write the command

            prepend command with * to dry run
            
            settings: use one of these at a time to change the settings of the program
            -k <api_key>: set the api key or print the current one
            -m <model_name>: set the model or print the current one
            -n: print the notes
            -n <key>: delete note with key <key>
            -n <key> <value>: set note with key <key> to value <value>
          """)
    exit()


try:
    with open(path_base + "conf.json") as file:
        conf = json.load(file)
except FileNotFoundError:
    conf = {"api_key": "", "model_name": "gpt-4o-mini", "notes":{"shell": "bash", "system": "linux"}}


def ask_chat(request, sys):
    client = OpenAI(api_key=conf["api_key"])
    completion = client.chat.completions.create(
            model = conf["model_name"],
            messages = [
                {"role": "system", "content": f"Information about the user: {conf['notes']}"},
                {"role": "system", "content": sys},
                {"role": "user", "content": request}
            ]
        )
    content = completion.choices[0].message.content
    print(f"chat> {content}")
    return content

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

tool_dict = {
    "execute": "execute text as a command on the system.",
    "thought": "think about what you need to do. The user does not see this.",
    "ask": "ask the user a question. If you think you know what the user wants or can figure it out by looking around, do that instead.",
    "finish": "print text and terminate if you have completed the task or can make no more progress on it.",
}
tools = [text_function(k, v) for k, v in tool_dict.items()]

        

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
        "m": "model_name",
}

#normal settings
if len(a1) == 2 and a1[0] == "-" and a1[1] in main_settings.keys():
    if len(sys.argv) > 2:
        conf[main_settings[a1[1]]] = sys.argv[2]
    else:
        print(conf[main_settings[a1[1]]])

#notes
elif a1 == "-n":
    if len(sys.argv == 2):
        print(conf["notes"])
    elif len(sys.argv == 3):
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
    while action != "finish":
        print()
        completion = client.chat.completions.create(model=conf["model_name"], messages = messages, tools=tools, tool_choice="required")

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

