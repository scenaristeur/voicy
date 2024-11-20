import os
from dotenv import load_dotenv
load_dotenv()

from groq import Groq

groq_key=os.getenv("GROQ_API_KEY")

groq_client = Groq(api_key=groq_key)

def groq_prompt(prompt):
    messages = [{'role': 'user', 'content': prompt}]
    chat_completion = groq_client.chat.completions.create(model="llama3-70b-8192", messages=messages)
    response = chat_completion.choices[0].message
    return response.content

prompt = input('USER: ')
response = groq_prompt(prompt)
print('RESPONSE: ', response)