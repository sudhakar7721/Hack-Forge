import secrets
from . import __name__ as _unused
# Development adapter only. Replace with a real SMS provider before production.
def issue_otp():
    return f"{secrets.randbelow(1_000_000):06d}"
def deliver_otp(destination: str, code: str, mode: str = "console"):
    if mode == "console":
        print(f"[DEV OTP] Destination={destination} Code={code}")
        return False
    raise RuntimeError("No SMS provider configured. OTP was not sent.")
