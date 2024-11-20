import pyperclip

def extract_clipboard():
    clipboard_content = pyperclip.paste()
    if isinstance(clipboard_content, str):
        # print(type (clipboard_content)) # même les images sont str, test non pertinent
        return clipboard_content
    else: 
        print("No clipboard text to copy")
        return None
    
print(extract_clipboard())