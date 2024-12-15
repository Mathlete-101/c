#!/bin/python3
# A chat client for accessing files, which in this case means large blocks of text that may or may not correspond to a file path in the system
import functions



class file_handler:
    def __init__(self, client, model, filename, source="", text=""):
        self.client = client
        self.model = model
        self.source = source
        self.text = text
        self.filename = filename
        self.is_new_file = False
        if text == "" and source != "":
            self.is_new_file = self.read()
        self.messages = [system("Your job is to understand the following file, respond to requests about its content and write it. The text is contained in the next system message."), system(self.text)]

    def read(self):
        try:
            with open(source, "r") as file:
                self.text = file.read()
        except FileNotFoundError:
            return False
        return True


    def write(self):
        try:
            with open(source, "w") as file:
                file.write(text)
        except FileNotFoundError:
            return False
        return True

    def query(self, query):
        messages.append(user(query)) 
        message = client.chat.completions.create(model = conf["models"]["command"], messages=messages).choices[0].message
        messages.append(message)
        return message.content


file_tools = [
        functions.text_function("file-open", "access a file on the system."),
        nilad("file-list_open", "get a list of all of the currently open files that you can query."),
        file_function("query", "request information about the file using natural language.", ("query", "the request query")),
        file_function("full_text", "request the full text of the file. Do not use this function unless absolutely nessecary."),
        file_function("set_contents", "set the contents of the file."),
        file_function("save", "save the file to the disk"),
        file_function("close", "close the file. It will not be saved."),
        file_function("change_path", "change the path of the file.", ("new_path", "the new path of the file")),
]

class filesystem:
    def __init__(self, client, model):
        self.client = client
        self.model = model
        files = {}

    """handles all of the tools specified in file_tools. returns the name of the file that was accessed in the form file <filename>, and the result of the tool"""
    def exec_function(self, function):
        name = function.name
        args = function.arguments
        if name[:5] != "file-":
            return "filesystem", f"{name} is not a filesystem function"
        name = name[5:]
        if name == "open":
            filename = args["text"].split("/")[-1]
            handler = file_handler(client, model, filename, args["text"])
            self.files[args["text"]] = handler
            
            if handler.is_new_file:
                handler.write()
                return "filesystem", f"New file '{args['text']}' created and opened"
            else:
                return "filesystem", f"File '{args['text']}' opened"
        elif name == "list_open":
            return "filesystem", f"Files open: {self.files.keys}"
        elif name == "query":
            return f"file {args['filename']}", self.files[args["filename"]].query(args["query"])
        elif name == "full_text":
            return f"file {args['filename']}", self.files[args["filename"]].text
        elif name == "save":
            return f"file {args['filename']}", self.files[args["filename"]].
            return f"file {args['filename']}", self.files[args["filename"]]
        else:
            return "filesystem", f"file-{name} is not a supported filesystem function"
