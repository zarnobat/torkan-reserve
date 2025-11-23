
import requests
from environs import Env

# This is for loading environment variables from a .env file
env = Env()
env.read_env()


def send_code(phone_number, token):
    api_key = env("API_KEY")
    url = f"https://api.kavenegar.com/v1/{api_key}/verify/lookup.json"

    params = {
        "receptor": phone_number,
        "token": token,
        "template": "otp"
    }
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to send verification code: {response.text}"}
    except Exception as e:
        return {"error": f"Exception occurred: {str(e)}"}


def customer_ticket(sender ,created_at, phone):
    api_key = env("API_KEY")
    url = f"https://api.kavenegar.com/v1/{api_key}/verify/lookup.json"

    
    params = {
        "receptor":phone,
        "template": "customer-ticket",
        "token10": sender,
        "token": created_at,
    }

    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to send request reserve sms: {response.text}"}
    except Exception as e:
        return {"error": f"Exception occurred: {str(e)}"}
    


def employee_ticket(employee ,ticket_type, phone):
    api_key = env("API_KEY")
    url = f"https://api.kavenegar.com/v1/{api_key}/verify/lookup.json"

    
    params = {
        "receptor":phone,
        "template": "employee-ticket",
        "token10": employee,
        "token": ticket_type,
    }

    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to send request reserve sms: {response.text}"}
    except Exception as e:
        return {"error": f"Exception occurred: {str(e)}"}
    


def answer_customer(sender ,created_at, phone):
    api_key = env("API_KEY")
    url = f"https://api.kavenegar.com/v1/{api_key}/verify/lookup.json"

    
    params = {
        "receptor":phone,
        "template": "answer",
        "token10": sender,
        "token": created_at,
    }

    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to send request reserve sms: {response.text}"}
    except Exception as e:
        return {"error": f"Exception occurred: {str(e)}"}
    


def answer_employee(employee ,created_at, ticket_type, status, phone):
    api_key = env("API_KEY")
    url = f"https://api.kavenegar.com/v1/{api_key}/verify/lookup.json"

    
    params = {
        "receptor":phone,
        "template": "answer-employee",
        "token10": employee,
        "token": created_at,
        "token2": ticket_type,
        "token20": status,
    }

    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to send request reserve sms: {response.text}"}
    except Exception as e:
        return {"error": f"Exception occurred: {str(e)}"}
    


def invoice_customer(customer ,created_at, phone):
    api_key = env("API_KEY")
    url = f"https://api.kavenegar.com/v1/{api_key}/verify/lookup.json"

    params = {
        "receptor":phone,
        "template": "invoice",
        "token10": customer,
        "token": created_at,
    }

    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to send request reserve sms: {response.text}"}
    except Exception as e:
        return {"error": f"Exception occurred: {str(e)}"}
    

def payslip_employee(employee ,created_at, phone):
    api_key = env("API_KEY")
    url = f"https://api.kavenegar.com/v1/{api_key}/verify/lookup.json"

    params = {
        "receptor":phone,
        "template": "payslip",
        "token10": employee,
        "token": created_at,
    }

    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to send request reserve sms: {response.text}"}
    except Exception as e:
        return {"error": f"Exception occurred: {str(e)}"}
    

def welcome_sms(name ,date_joined, phone):
    api_key = env("API_KEY")
    url = f"https://api.kavenegar.com/v1/{api_key}/verify/lookup.json"

    params = {
        "receptor":phone,
        "template": "welcome",
        "token10": name,
        "token": date_joined,
    }

    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to send request reserve sms: {response.text}"}
    except Exception as e:
        return {"error": f"Exception occurred: {str(e)}"}
    