import requests
import time


class TelegramService:

    def __init__(self, token):
        self.base = f"https://api.telegram.org/bot{token}"

    def send_message(self, chat_id, text):
        url = f"{self.base}/sendMessage"
        r = requests.post(url, data={
            "chat_id": chat_id,
            "text": text
        })

        result = r.json()

        if not result.get("ok"):
            if r.status_code == 429:
                retry = result.get("parameters", {}).get("retry_after", 1)
                time.sleep(retry)
                return self.send_message(chat_id, text)
            return False, result.get("description")

        return True, None