import os
import africastalking

def send_sms(msidn, message):
    provider = os.getenv('SMS_PROVIDER', 'mock')

    if provider == 'mock':
        print(f"[SMS MOCK] to {msisdn}:{message}")
        return True
    
    elif provider == 'africastalking':
        username = os.getenv('AT_USERNAME')
        api_key = os.getenv('AT_API_KEY')


        africastalking.initialize(username, api_key)
        sms = africastalking.SMS

        try:
            response = sms.send(message, [msisdn])
            print("[SMS SENT], response")
            return True
        except Exception as e:
            print(f"[SMS ERROR]", e)
            return False
        else:
            raise ValueError("Uknown SMS provider")