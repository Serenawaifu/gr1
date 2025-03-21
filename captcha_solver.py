from twocaptcha import TwoCaptcha  # Correct import

class CaptchaSolver:
    def __init__(self, api_key):
        self.client = TwoCaptcha(api_key)

    def solve(self, image_data):
        try:
            result = self.client.normal(image_data)
            return result["code"]
        except Exception as e:
            raise RuntimeError("CAPTCHA solve failed") from e
