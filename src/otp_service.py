import random

def send_otp():
    otp = random.randint(100000, 999999)
    print(f"[OTP SENT] Your OTP is: {otp}")
    return otp

def verify_otp(sent_otp):
    try:
        user_input = int(input("Enter OTP: "))
        return user_input == sent_otp
    except ValueError:
        return False
