import requests

class SMSModule:
    def __init__(self, api_key):
        self.api_key = api_key

    def send(self, recipient, message):
        try:
            response = requests.post(
                "https://api.sms-service.com/send",
                data={
                    "api_key": self.api_key,
                    "recipient": recipient,
                    "message": message
                }
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Error sending SMS: {e}")
            return False
