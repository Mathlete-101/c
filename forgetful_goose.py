import goose

def sizeof_message(message):
    role = message['role']
    total = len(message['content']) if message['content'] is not None else 0
    if role == 'assistant':
        for call in message['tool_calls']: 
            total += len(call['function']['arguments'])
    return total

class forgetful_goose(goose.goose):
    def post_init(self):
        self.keep = 0
        self.memory_used = 0
        self.memory_limit = 20000

    def __call__(self, *messages):
        super().__call__(*messages)
        for message in messages:
            m = goose.marshal(message)
            self.memory_used += sizeof_message(m)

    def body(self):
        return super().body() | {"forgetfulness": {"memory_limit": self.memory_limit, "memory_used": self.memory_used, "keep": self.keep}}

    def quack(self):
        super().quack()
        while self.memory_used > self.memory_limit and self.soc[self.keep]['role'] in ['user', 'assistant']:
            self.memory_used -= len(self.soc[self.keep]['content'])
            self.soc.pop(self.keep)
        if "content" in dir(self.last) and self.last.content is not None:
            self.memory_used += len(self.last.content)
        else:
            pass
            #print(f"----> {dir(self.last)}")
                 
            
                 
    
