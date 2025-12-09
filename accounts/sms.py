import os
import africastalking
# Define function send_sms with parameters:
# - msisdn: phone number in E.164 format (e.g., +255712345678)
def send_sms(msisdn, message):
    # Read SMS provider from environment variable, default to 'mock'
    provider = os.getenv('SMS_PROVIDER', 'mock')
    # If provider is set to 'mock' (development mode)
    if provider == 'mock':
        # Print simulated SMS to console for debugging
        print(f"[SMS MOCK] to {msisdn}: {message}")
        # Return True to indicate success
        return True

    # If provider is set to 'africastalking' (production mode)
    elif provider == 'africastalking':
        # Read Africa's Talking username from environment variables
        username = os.getenv('AT_USERNAME')
        # Read Africa's Talking API key from environment variables
        api_key = os.getenv('AT_API_KEY')

        # Initialize Africa's Talking SDK with credentials
        africastalking.initialize(username, api_key)
        # Get SMS service object from SDK
        sms = africastalking.SMS

        # Try sending SMS
        try:
            # Send SMS message to the given phone number
            response = sms.send(message, [msisdn])
            # Print confirmation and API response
            print("[SMS SENT]", response)
            # Return True to indicate success
            return True
        # If an error occurs during sending
        except Exception as e:
            # Print error message
            print("[SMS ERROR]", e)
            # Return False to indicate failure
            return False

    # If provider is neither 'mock' nor 'africastalking'
    else:
        # Raise error for unsupported provider
        raise ValueError("Unknown SMS provider")
