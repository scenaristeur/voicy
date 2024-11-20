import google.generativeai as genai
from groq import Groq
import cv2
import pyperclip
from PIL import ImageGrab, Image
import os
from dotenv import load_dotenv
load_dotenv()


web_cam = cv2.VideoCapture(0)

groq_api_key = os.getenv("GROQ_API_KEY")
google_gemini_api_key = os.getenv("GOOGLE_GEMINI_API_KEY")

groq_client = Groq(api_key=groq_api_key)

sys_msg = (
    'You are a multi-modal AI voice assistant. Your user may or may not have attached photo for context '
    '(either a screenshot or a webcam capture). Any photo has already been processed into a highly detailed '
    'text prompt that will be attached to their transcribed voice prompt. Generate the most useful and '
    'factual response possible, carefully considering all previous generated text in your response before '
    'adding new tokens to the response. Do not expect or request images, just use the context if added. '
    'Use all of the context of this conversation so your response is relevant to the conversation. Make '
    'your response clear and concise, avoiding any verbosity.'
)


messages = [{'role': 'system', 'content': sys_msg}]


generation_config = {
    'temperature': 0.7,
    'top_p': 1,
    'top_k': 1,
    'max_output_tokens': 2048
}

safety_settings = [
    {
        'category': 'HARM_CATEGORY_HARASSMENT',
        'threshold': 'BLOCK_NONE'
    },
    {
        'category': 'HARM_CATEGORY_HATE_SPEECH',
        'threshold': 'BLOCK_NONE'
    },
    {
        'category': 'HARM_CATEGORY_SEXUALLY_EXPLICIT',
        'threshold': 'BLOCK_NONE'
    },
    {
        'category': 'HARM_CATEGORY_DANGEROUS_CONTENT',
        'threshold': 'BLOCK_NONE'
    }
]

model = genai.GenerativeModel('gemini-1.5-flash-latest',
                              generation_config=generation_config,
                              safety_settings=safety_settings)


def groq_prompt(prompt, img_context):
    if img_context:
        prompt = f'USER PROMPT: {prompt}\n\n\tIMAGE CONTEXT: {img_context}'
    messages.append({'role': 'user', 'content': prompt})
    chat_completion = groq_client.chat.completions.create(
        model="llama3-70b-8192", messages=messages)
    response = chat_completion.choices[0].message
    messages.append(response)
    return response.content


def function_call(prompt):
    function_sys_msg = (
        'You are an AI function calling model. You will determine whether extractiong the users clipboard content, '
        'taking a screenshot, capturing the webcam or calling no functions is best for a voice assistant to respond '
        'to the users prompt. The webcam can be assumed to be a normal laptop webcam facing the user. You will '
        'respond with only one selection freom this list: ["extract clipboard", "take screenshot", "capture webcam", "None"] \n'
        'Do not respond with anything but the most logical selection friom that list with no explanation. Formet the '
        'function call name exactly as I listed.'
    )

    function_messages = [{'role': 'system', 'content': function_sys_msg}, {
        'role': 'user', 'content': prompt}]
    chat_completion = groq_client.chat.completions.create(
        model="llama3-70b-8192", messages=function_messages)
    response = chat_completion.choices[0].message
    return response.content


def take_screenshot():
    path = './data/screenshot.jpg'
    screenshot = ImageGrab.grab()
    rgb_screenshot = screenshot.convert('RGB')
    rgb_screenshot.save(path, quality=15)


def capture_webcam():
    # def web_cam_capture():
    if not web_cam.isOpened():
        print("Erreur : La webcam n'est pas correctement ouverte")
        exit()

    path = './data/webcam.jpg'
    ret, frame = web_cam.read()
    cv2.imwrite(path, frame)


def extract_clipboard():
    clipboard_content = pyperclip.paste()
    if isinstance(clipboard_content, str) and len(clipboard_content) > 0:
        # print(type (clipboard_content)) # même les images sont str, test non pertinent
        return clipboard_content
    else:
        print("No clipboard text to copy")
        return None


def vision_prompt(prompt, photo_path):
    img = Image.open(photo_path)
    prompt = (
        'You are the vision analysis AI that provides semantic meaning from images to provide context '
        'to send to another AI that will create a response to the user. Do not respond as the AI assistant '
        'to the user. Instead take the user prompt input and try to extract all meaning from the photo '
        'relevant to the user prompt. Then generate as much objective data about the image for the AI '
        f'assistant who will respond to the user. \nUSER PROMPT: {prompt}'
    )
    # response = model.generate_content([prompt, img])
    client = Groq()

    response = client.chat.completions.create(

        model="llama-3.2-11b-vision-preview",

        messages=[

            {

                "role": "user",

                "content": [

                    {

                        "type": "text",

                        "text": prompt

                    },

                    {

                        "type": "image",

                        "image": img

                    }

                ]

            }

        ],

        temperature=1,

        max_tokens=1024,

        top_p=1,

        stream=False,

        stop=None,

    )

    return response.text


#
# function_response = function_call(prompt)
# print('FUNCTION CALL: ', function_response)
# response = groq_prompt(prompt)
# print('RESPONSE: ', response)
while True:
    prompt = input('USER: ')
    call = function_call(prompt)

    if 'take_screenshot' in call:
        print('Taking screenshot')
        take_screenshot()
        visual_context = vision_prompt(
            prompt=prompt, photo_path='./data/screenshot.jpg')
    elif 'capture webcam' in call:
        print('Capturing webcam')
        capture_webcam()
        visual_context = vision_prompt(
            prompt=prompt, photo_path='./data/webcam.jpg')
    elif 'extract clipboard' in call:
        print('Extracting clipboard')
        paste = extract_clipboard()
        prompt = f'{prompt}\n\n CLIPBOARD CONTENT: {paste}'
        visual_context = None
    else:
        visual_context = None

    response = groq_prompt(prompt=prompt, img_context=visual_context)
    print(response)
