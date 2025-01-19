import ollama

class Conversational_Bot:
    def __init__(self, system=""):
        self.messages = [] # define history list
        
        if system:
            self.messages.append({"role": "system", "content": system})
            
    def generate(self, user_question, image=None):
    
        # append user query to history under "user" role
        if image:
            self.messages.append({"role": "user", "content":user_question, "images": [image]})
        else:
            self.messages.append({"role": "user", "content":user_question})
        
        # generate response from LLM
        response = ollama.chat(model='llama3.2-vision', messages=self.messages)
        
        # Add LLM's response to the history under "assistant" role
        self.messages.append({"role":"assistant", "content":response.message.content})
        
        print(f'History: {self.messages}')
        
        return response