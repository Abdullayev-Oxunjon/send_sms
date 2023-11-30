import random

import requests


def genereation_verification_code():
    return random.randint(100000, 999999)


BASE_URL = "https://mm9e9w.api.infobip.com"
API_KEY = "3f9ef9b62fdde9534784998d4d235b25-887ec63b-ce19-4433-879b-98d99e9a97fd"
RECIPIENT = "998906664274"


def send_sms(message, recipient):
    url = f"{BASE_URL}/sms/1/text/single"
    headers = {
        "Authorization": f"App {API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "from": "Oxunjon",  # Replace with your sender ID or phone number
        "to": recipient,
        "text": message,
    }

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        print("SMS sent successfully.")
    else:
        print(f"Failed to send SMS. Error: {response.text}")


if __name__ == "__main__":
    # Define your message and recipient's phone number
    message = f"{genereation_verification_code()}"
    recipient = RECIPIENT  # Replace with the recipient's phone number

    # Send the SMS using Infobip
    send_sms(message, recipient)
