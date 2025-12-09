# Import regular expressions module
import re

# Function to normalize raw phone numbers into E.164 format (+255...)
def normalize_msisdn(raw, default_country='+255'):
    # Remove all non-digit characters from input
    s = re.sub(r'\D', '', raw)

    # If number starts with 0 and default country is Tanzania (+255)
    if s.startswith('0') and default_country == '+255':
        # Replace leading 0 with country code 255
        s = f'255{s[1:]}'

    # If number already starts with 255 (Tanzania)
    if s.startswith('255'):
        # Return with + prefix
        return f'+{s}'

    # If raw input already had + sign
    if raw.startswith('+'):
        # Return normalized with + prefix
        return f'+{s}'

    # Fallback: return with + prefix
    return f'+{s}'


# Function to validate Tanzanian phone numbers
def is_valid_tz(msisdn):
    # Match +255 followed by 9 digits
    return bool(re.fullmatch(r'\+255\d{9}', msisdn))
