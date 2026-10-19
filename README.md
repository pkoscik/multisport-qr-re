# multisport-qr-re

Fetch your MultiSport visit QR from the app's backend and print it in the terminal.

Unofficial, not affiliated with Benefit Systems.

## Setup

```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt
```

## Usage

```bash
.venv/bin/python multisport.py          # print the online code and draw the QR
.venv/bin/python multisport.py --json   # full response (online + offline codes)
```

The first run opens the login page in your browser; paste the `code` from the
`com.multisport://app?code=...` redirect. After that the saved refresh token is
used. The card number is read from the token. Endpoints are in [API.md](API.md).

## License

[Apache 2.0](LICENSE)
