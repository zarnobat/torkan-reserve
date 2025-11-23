import requests
from environs import Env

env = Env()
env.read_env()


def laboratory(name , sn, phone):
    api_key = env("API_KEY")
    url = f"https://api.kavenegar.com/v1/{api_key}/verify/lookup.json"

    params = {
        "receptor":phone,
        "template": "laboratory",
        "token10": name,
        "token": sn,
    }

    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to send request reserve sms: {response.text}"}
    except Exception as e:
        return {"error": f"Exception occurred: {str(e)}"}