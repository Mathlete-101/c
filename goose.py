import json

def marshal(obj):
    """Recursively converts an object to a dictionary."""

    if isinstance(obj, dict):
        return {k: marshal(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [marshal(item) for item in obj]
    elif hasattr(obj, "__dict__"):
        return {k: marshal(v) for k, v in vars(obj).items() if not k.startswith("_")}
    else:
        return obj

class goose:
    def __init__(self, client, model, tools=[], messages=[], tool_choice="required"):
        self.client = client
        self.model = model
        self.soc = self.starting_messages() + messages
        self.log = [m for m in self.soc] 
        self.tools = tools
        self.tool_choice = tool_choice
        self.last = None
        self.last_quack=None
        self.post_init()

    def post_init(self):
        pass
    
    def starting_messages(self):
        return []

    def body(self):
        return {"soc": self.soc, "log": self.log}

    def vivisect(self):
        s = ""
        for t in self.soc:
            s += f"{t.role}> {t.message if len(t.message) < 16 else f'{t.message[0:13]}...'}"

    def quack(self):
        self.last_quack = self.client.chat.completions.create(model=self.model, tool_choice=self.tool_choice, messages=self.soc, tools=self.tools)
        self.last = self.last_quack.choices[0].message
        self(self.last)

    def __call__(self, *messages):
        for message in messages:
            m = marshal(message)
            self.log.append(m)
            self.soc.append(m)
