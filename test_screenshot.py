from PIL import ImageGrab

def take_screenshot():
    path = './data/screenshot.jpg'
    screenshot = ImageGrab.grab()
    rgb_screenshot = screenshot.convert('RGB')
    rgb_screenshot.save(path, quality=15)

take_screenshot()