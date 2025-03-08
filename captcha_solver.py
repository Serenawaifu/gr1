from captchatools import CaptchaSolver

class CaptchaSolver:
    def __init__(self):
        self.api = CaptchaSolver("YOUR_CAPTCHA_API_KEY")  # <button class="citation-flag" data-index="6">

    def solve(self, image_data):
        try:
            return self.api.solve_captcha(image_data)
        except Exception as e:
            raise RuntimeError("CAPTCHA solve failed") from e
