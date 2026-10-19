#!/usr/bin/env python3
import base64, hashlib, json, secrets, sys, urllib.parse, webbrowser
from pathlib import Path
import requests, qrcode

TOKEN_FILE = Path(__file__).resolve().parent / ".token.json"

BAM = "https://bam.benefitsystems.online/bam/core"
APP_VERSION = "1.53.3"

KC = "https://login.emultisport.pl/realms/sso/protocol/openid-connect"
KC_CLIENT = "mobile-app"
KC_REDIRECT = "com.multisport://app"


def b64url(b):
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()


def card_number(access_token):
    payload = access_token.split(".")[1]
    payload += "=" * (-len(payload) % 4)
    return json.loads(base64.urlsafe_b64decode(payload))["ms_products"][0]


def get_token(**data):
    """POST to the Keycloak token endpoint; save and return True on success."""
    resp = requests.post(f"{KC}/token", data={"client_id": KC_CLIENT, **data}, timeout=15).json()
    if "access_token" not in resp:
        print(f"token request failed: {resp}", file=sys.stderr)
        return False
    TOKEN_FILE.write_text(json.dumps(resp))
    return True


def login():
    verifier = b64url(secrets.token_bytes(32))
    challenge = b64url(hashlib.sha256(verifier.encode()).digest())
    url = f"{KC}/auth?" + urllib.parse.urlencode({
        "client_id": KC_CLIENT, "response_type": "code", "scope": "openid",
        "state": secrets.token_hex(8), "code_challenge": challenge,
        "code_challenge_method": "S256", "redirect_uri": KC_REDIRECT,
    })
    print(f"log in, then paste the code from the redirect:\n\n{url}\n", file=sys.stderr)
    webbrowser.open(url)
    code = input("code: ").strip()
    if not get_token(grant_type="authorization_code", redirect_uri=KC_REDIRECT,
                     code_verifier=verifier, code=code):
        sys.exit("login failed")


def fetch():
    access_token = json.loads(TOKEN_FILE.read_text())["access_token"]
    headers = {
        "Authorization": "Bearer " + access_token,
        "x-device-id": "b7f4a921373d24f5",
        "x-device-model": "SM-S911B",
        "x-device-system": "android: 14",
        "x-device-app-version": APP_VERSION,
    }
    url = f"{BAM}/v1/authorized/products/{card_number(access_token)}/codes/visit"
    return requests.get(url, headers=headers, timeout=15)


def main():
    if not TOKEN_FILE.exists():
        login()

    r = fetch()
    if r.status_code == 401:
        rt = json.loads(TOKEN_FILE.read_text())["refresh_token"]
        if not get_token(grant_type="refresh_token", refresh_token=rt):
            login()
        r = fetch()
    if r.status_code != 200:
        sys.exit(f"fetch failed ({r.status_code}): {r.text}")

    codes = r.json()
    if "--json" in sys.argv[1:]:
        print(json.dumps(codes, indent=2))
        return

    online = next(c for c in codes if c["type"] == "online")
    print(online["code"])
    print("expires " + online["expirationDate"], file=sys.stderr)
    qr = qrcode.QRCode(border=2)
    qr.add_data(online["code"])
    qr.print_ascii(out=sys.stderr, invert=True)


if __name__ == "__main__":
    main()
