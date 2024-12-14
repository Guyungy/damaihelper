import pytesseract
from PIL import Image

def solve_captcha(image_path):
    # 使用OCR识别验证码
    image = Image.open(image_path)
    captcha_text = pytesseract.image_to_string(image)
    return captcha_text
