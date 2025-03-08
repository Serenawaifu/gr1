from captchatools import CaptchaClient  # <button class="citation-flag" data-index="7"><button class="citation-flag" data-index="8">

class CaptchaSolver:
    def __init__(self, api_key):
        self.client = CaptchaClient(api_key)  # Initialize with API key <button class="citation-flag" data-index="7">

    def solve(self, image_data):
        try:
            return self.client.solve_captcha(image_data)  # Use library method <button class="citation-flag" data-index="8">
        except Exception as e:
            raise RuntimeError("CAPTCHA solve failed") from e
