#!/usr/bin/python3
import random
import phonenumbers
import requests
from phonenumbers import geocoder, carrier, NumberParseException
import time

# ============ CONFIGURATION ============

number_of_phone_num = 950000
num_adjust_last_min = 1000000
num_adjust_last_max = 9999999
proxy = "socks5://127.0.0.1:9050"

CONFIG = {
    'use_numverify': True,
    'use_abstract': False,
    'use_veriphone': False,

    'numverify_key': 'e618c7644af6e982ea5fdf523fed1c50',
    'abstract_key': 'your_abstractapi_key',
    'veriphone_key': 'your_veriphone_key',
}

def local_lookup(phone_number):
    try:
        parsed = phonenumbers.parse(phone_number)
        is_valid = phonenumbers.is_valid_number(parsed)
        location = geocoder.description_for_number(parsed, "en")
        carrier_name = carrier.name_for_number(parsed, "en") if is_valid else "Unknown"
        return f"Local: {phone_number}, Valid: {is_valid}, Location: {location}, Carrier: {carrier_name}"
    except NumberParseException:
        return f"Local: {phone_number}, Invalid format"

def numverify_lookup(phone_number, proxies=None):
    try:
        url = f"http://apilayer.net/api/validate?access_key={CONFIG['numverify_key']}&number={phone_number}"
        res = requests.get(url, proxies=proxies).json()
        return f"NumVerify: Valid: {res.get('valid')}, Carrier: {res.get('carrier')}, Line type: {res.get('line_type')}"
    except Exception as e:
        return f"NumVerify: Failed - {e}"

def abstract_lookup(phone_number, proxies=None):
    try:
        url = f"https://phonevalidation.abstractapi.com/v1/?api_key={CONFIG['abstract_key']}&phone={phone_number}"
        res = requests.get(url, proxies=proxies).json()
        return f"AbstractAPI: Valid: {res.get('valid')}, Carrier: {res.get('carrier')}, Type: {res.get('line_type')}"
    except Exception as e:
        return f"AbstractAPI: Failed - {e}"

def veriphone_lookup(phone_number, proxies=None):
    try:
        url = f"https://api.veriphone.io/v2/verify?phone={phone_number}&key={CONFIG['veriphone_key']}"
        res = requests.get(url, proxies=proxies).json()
        return f"Veriphone: Valid: {res.get('phone_valid')}, Carrier: {res.get('carrier')}, Type: {res.get('phone_type')}"
    except Exception as e:
        return f"Veriphone: Failed - {e}"

# ============ USER INPUT AND NUMBER GENERATION ============

def get_user_input():
    """Prompt user for phone number components."""
    country_code = input("Enter country code (e.g., +1): ").strip()
    if not country_code.startswith('+'):
        country_code = '+' + country_code

    area_code = input("Enter area code (first 3 digits, e.g., 212): ").strip()
    exchange_code = input("Enter exchange code (next 3 digits, e.g., 555): ").strip()

    return country_code, area_code, exchange_code

def generate_phone_number(country_code, area_code, exchange_code, proxies=None):
    """Generate a random phone number with fixed area and exchange code."""
    last_four = random.randint(num_adjust_last_min, num_adjust_last_max)
    return f"{country_code}{area_code}{exchange_code}{last_four}"

# ============ MAIN EXECUTION exchange_code============

def main():
    try:
        proxies = {"http": proxy, "https": proxy, "socks5": proxy} if proxy else None
        country_code, area_code, exchange_code = get_user_input()

        results = []
        for _ in range(number_of_phone_num):
            phone_number = generate_phone_number(country_code, area_code, exchange_code)
            result = [f"\n📞 Checking: {phone_number}"]

            # Local check
            result.append(local_lookup(phone_number))

            # NumVerify
            if CONFIG['use_numverify']:
                result.append(numverify_lookup(phone_number))

            # AbstractAPI
            if CONFIG['use_abstract']:
                result.append(abstract_lookup(phone_number))

            # Veriphone
            if CONFIG['use_veriphone']:
                result.append(veriphone_lookup(phone_number))

            final = '\n'.join(result)
            print(final)
            results.append(final + "\n")
    except KeyboardInterrupt:
        print("Saving output...")
        with open('multi_api_phone_results.txt', 'w') as f:
            f.writelines(results)

if __name__ == "__main__":
    main()
