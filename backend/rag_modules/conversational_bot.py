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
    
    def get_history(self):
        return self.messages
    
    def set_history(self, history):
        print('Setting history')
        self.messages = history
        print(f'Set History: {self.messages}')
        
    def summarize_image(self, image):
        response = ollama.chat(
        model='llama3.2-vision',
        messages=[{
            'role': 'user',
            'content': 'Summarize the image:',
            'images': [image]
            }]
        )
        return response.message.content
    
    def summarize_table(self, table_html):
        response = ollama.chat(
        model='llama3.2:1b',
        messages=[{
            'role': 'user',
            'content': f'Summarize this table: {table_html}'
            }]
        )
        
        return response.message.content
    
if __name__ == '__main__':
    bot = Conversational_Bot("You are an expert in the field of AI Research and current AI Trends.")
    query = None
    while query != 'EXIT':
        query = input('You: ')
        if query == 'EXIT': break
        response = bot.generate(query)
        print(f'Bot: {response.message.content}')