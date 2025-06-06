import random
import phonenumbers
import requests
from phonenumbers import geocoder, carrier, NumberParseException
from twilio.rest import Client
from twilio.http.http_client import TwilioHttpClient

# ============ CONFIGURATION ============

CONFIG = {
    'use_twilio': True,
    'use_numverify': True,
    'use_abstract': True,
    'use_veriphone': True,

    'twilio_sid': 'your_twilio_sid',
    'twilio_token': 'your_twilio_token',
    'twilio_proxy': 'socks5://username:password@proxyhost:port',  # e.g., 'socks5://user:pass@127.0.0.1:9050'

    'numverify_key': 'your_numverify_api_key',
    'abstract_key': 'your_abstractapi_key',
    'veriphone_key': 'your_veriphone_key',
}

# ============ SETUP ============

def get_twilio_client():
    proxy_client = TwilioHttpClient()
    if CONFIG['twilio_proxy']:
        proxy_client.session.proxies = {'https': CONFIG['twilio_proxy']}
    return Client(CONFIG['twilio_sid'], CONFIG['twilio_token'], http_client=proxy_client)

# ============ LOOKUP FUNCTIONS ============

def local_lookup(phone_number):
    try:
        parsed = phonenumbers.parse(phone_number)
        is_valid = phonenumbers.is_valid_number(parsed)
        location = geocoder.description_for_number(parsed, "en")
        carrier_name = carrier.name_for_number(parsed, "en") if is_valid else "Unknown"
        return f"Local: {phone_number}, Valid: {is_valid}, Location: {location}, Carrier: {carrier_name}"
    except NumberParseException:
        return f"Local: {phone_number}, Invalid format"

def twilio_lookup(client, phone_number):
    try:
        lookup = client.lookups.v1.phone_numbers(phone_number).fetch(type=['carrier'])
        carrier_name = lookup.carrier['name'] if lookup.carrier else "Unknown"
        return f"Twilio: Carrier: {carrier_name}"
    except Exception as e:
        return f"Twilio: Lookup failed - {e}"

def numverify_lookup(phone_number):
    try:
        url = f"http://apilayer.net/api/validate?access_key={CONFIG['numverify_key']}&number={phone_number}"
        res = requests.get(url).json()
        return f"NumVerify: Valid: {res.get('valid')}, Carrier: {res.get('carrier')}, Line type: {res.get('line_type')}"
    except Exception as e:
        return f"NumVerify: Failed - {e}"

def abstract_lookup(phone_number):
    try:
        url = f"https://phonevalidation.abstractapi.com/v1/?api_key={CONFIG['abstract_key']}&phone={phone_number}"
        res = requests.get(url).json()
        return f"AbstractAPI: Valid: {res.get('valid')}, Carrier: {res.get('carrier')}, Type: {res.get('line_type')}"
    except Exception as e:
        return f"AbstractAPI: Failed - {e}"

def veriphone_lookup(phone_number):
    try:
        url = f"https://api.veriphone.io/v2/verify?phone={phone_number}&key={CONFIG['veriphone_key']}"
        res = requests.get(url).json()
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

def generate_phone_number(country_code, area_code, exchange_code):
    """Generate a random phone number with fixed area and exchange code."""
    last_four = random.randint(1000, 9999)
    return f"{country_code}{area_code}{exchange_code}{last_four}"

# ============ MAIN EXECUTION ============

def main():
    country_code, area_code, exchange_code = get_user_input()
    client = get_twilio_client() if CONFIG['use_twilio'] else None

    results = []
    for _ in range(10):
        phone_number = generate_phone_number(country_code, area_code, exchange_code)
        result = [f"\n📞 Checking: {phone_number}"]

        # Local check
        result.append(local_lookup(phone_number))

        # Twilio
        if CONFIG['use_twilio'] and client:
            result.append(twilio_lookup(client, phone_number))

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

    with open('multi_api_phone_results.txt', 'w') as f:
        f.writelines(results)

if __name__ == "__main__":
    main()
