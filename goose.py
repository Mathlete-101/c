class goose:
    def __init__(self, client, model, tools=[], messages=[], tool_choice="required"):
        self.client = client
        self.model = model
        self.messages = self.starting_messages() + messages
        self.tools = tools
        self.tool_choice = tool_choice
        self.last = None
        self.post_init()

    def post_init(self):
        pass
    
    def starting_messages(self):
        return []
        
    def complete(self):
        self.last_completion = self.client.chat.completions.create(model=self.model, tool_choice=self.tool_choice, messages=self.messages, tools=self.tools)
        self.last = self.last_completion.choices[0].message
        self.messages.append(self.last)

    def __call__(self, *messages):
        self.messages += messages
