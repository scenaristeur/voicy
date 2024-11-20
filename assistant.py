import os
from dotenv import load_dotenv
load_dotenv()

from groq import Groq
from PIL import ImageGrab 

groq_key=os.getenv("GROQ_API_KEY")

groq_client = Groq(api_key=groq_key)

def groq_prompt(prompt):
    messages = [{'role': 'user', 'content': prompt}]
    chat_completion = groq_client.chat.completions.create(model="llama3-70b-8192", messages=messages)
    response = chat_completion.choices[0].message
    return response.content



def function_call(prompt):
    sys_msg = (
        'You are an AI function calling model. You will determine whether extractiong the users clipboard content, '
        'taking a screenshot, capturing the webcam or calling no functions is best for a voice assistant to respond '
        'to the users prompt. The webcam can be assumed to be a normal laptop webcam facing the user. You will '
        'respond with only one selection freom this list: ["extract clipboard", "take screenshot", "capture webcam", "None"] \n'
        'Do not respond with anything but the most logical selection friom that list with no explanation. Formet the '
        'function call name exactly as I listed.'
    )

    function_messages = [{'role': 'system', 'content': sys_msg}, {'role': 'user', 'content': prompt}]
    chat_completion = groq_client.chat.completions.create(model="llama3-70b-8192", messages=function_messages)
    response = chat_completion.choices[0].message
    return response.content

def take_screenshot():
    path = 'screenshot.png'
    screenshot = ImageGrab.grab()
    rgb_screenshot = screenshot.convert('RGB')
    rgb_screenshot.save(path, quality=15)


def capture_webcam():

    pass

def extract_clipboard():
    pass



prompt = input('USER: ')
function_response = function_call(prompt)
print('FUNCTION CALL: ', function_response)
response = groq_prompt(prompt)
print('RESPONSE: ', response)