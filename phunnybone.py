import random
import phonenumbers
from phonenumbers import geocoder, carrier, NumberParseException
from twilio.rest import Client
from twilio.http.http_client import TwilioHttpClient

def get_twilio_client():
    """Set up the Twilio client with a SOCKS5 proxy."""
    # Twilio credentials
    account_sid = 'your_account_sid_here'
    auth_token = 'your_auth_token_here'
    
    # SOCKS5 proxy configuration (requires PySocks: pip install pysocks)
    proxy_client = TwilioHttpClient()
    proxy_client.session.proxies = {
        'https': 'socks5://username:password@proxyserver:port'
    }

    # Return Twilio client with proxy
    return Client(account_sid, auth_token, http_client=proxy_client)

def get_user_input():
    """Prompt user for country code and area code."""
    country_code = input("Enter the country code (e.g., +1, +44, +91): ")
    area_code = input("Enter the area code (e.g., for USA 212, for UK 20): ")

    # Ensure country code starts with '+'
    if not country_code.startswith('+'):
        country_code = '+' + country_code

    return country_code, area_code

def generate_phone_number(country_code, area_code):
    """Generate a random phone number for the given area code."""
    number = random.randint(1000000, 9999999)
    return f"{country_code}{area_code}{number}"

def validate_phone_number(phone_number, client):
    """Validate phone number using phonenumbers and Twilio Lookup API."""
    try:
        # Local validation
        number = phonenumbers.parse(phone_number)
        is_valid = phonenumbers.is_valid_number(number)
        country = geocoder.description_for_number(number, "en")
        local_carrier = carrier.name_for_number(number, "en") if is_valid else "Local carrier info not available"

        # Remote Twilio lookup (v1 API)
        twilio_lookup = client.lookups.v1.phone_numbers(phone_number).fetch(type=['carrier'])
        twilio_carrier = twilio_lookup.carrier['name'] if twilio_lookup.carrier else "Twilio carrier info not available"

        validation_result = "Valid" if is_valid else "Invalid"
        return f"{phone_number}, {validation_result}, Country: {country}, Local Carrier: {local_carrier}, Twilio Carrier: {twilio_carrier}\n"

    except NumberParseException:
        return f"{phone_number}, Invalid, Error: Not in a valid format\n"
    except Exception as e:
        return f"{phone_number}, Twilio Lookup Failed, Error: {str(e)}\n"

def main():
    client = get_twilio_client()
    country_code, area_code = get_user_input()
    results = []

    for _ in range(10):  # Generate 10 phone numbers
        phone_number = generate_phone_number(country_code, area_code)
        result = validate_phone_number(phone_number, client)
        results.append(result)
        print(result.strip())  # Optional: show output in terminal

    # Write results to file
    with open('phone_numbers_validation_results.txt', 'w') as file:
        file.writelines(results)

if __name__ == "__main__":
    main()
