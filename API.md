# API

Taken from the MultiSport Android app (`com.multisport` 1.53.3).

## Login (Keycloak)

| | |
|---|---|
| issuer | `https://login.emultisport.pl/realms/sso` |
| client_id | `mobile-app` |
| redirect_uri | `com.multisport://app` |
| scope | `openid` |
| flow | authorization code + PKCE (S256) |

`mobile-app` is a public client (no secret). The password grant is disabled, so the first login needs a browser:

```
GET {issuer}/protocol/openid-connect/auth
    ?client_id=mobile-app&response_type=code&scope=openid&state=...
    &code_challenge=...&code_challenge_method=S256
    &redirect_uri=com.multisport%3A%2F%2Fapp
```

After logging in, take `code` from the `com.multisport://app?code=...` redirect
and exchange it at `POST {issuer}/protocol/openid-connect/token`
(form-urlencoded):

| grant | fields |
|---|---|
| `authorization_code` | `client_id`, `redirect_uri`, `code`, `code_verifier` |
| `refresh_token` | `client_id`, `refresh_token` |

The access token (~7 days; refresh token ~270 days) is used directly as the
API bearer.

## Visit QR

```
GET https://bam.benefitsystems.online/bam/core/v1/authorized/products/{cardNumber}/codes/visit
```

`cardNumber` is the 12-digit card number from the access token's `ms_products`
claim.

| header | value |
|---|---|
| `Authorization` | `Bearer <access_token>` |
| `x-device-id` | any string |
| `x-device-model` | any string |
| `x-device-system` | any string, e.g. `android: 13` |
| `x-device-app-version` | `1.53.3` (the server enforces a minimum) |

All four `x-device-*` headers must be present, otherwise `400 Missing required headers`.

Response:

```json
[
  { "type": "offline", "code": "1.3.0~...", "token": "...", "expirationDate": "..." },
  { "type": "online",  "code": "1.3.0~...", "token": "...", "expirationDate": "..." }
]
```

Encode `code` as the QR. `online` expires after about a minute; `offline`
lasts about two weeks and is meant for use without network.

`code` is ~252 characters: `1.3.0~<serial>~<seq>;~<k=v|k=v|...>~<hex signature>`.
In the key-value part, field 9 is the card number, 6 a date and 15 the
generation timestamp. The server signs it; the client only renders it.

## Other endpoints

Under the same `products/{cardNumber}` path: `codes/identity`, `history`,
`limits`, `relations`. Other modules: `bam/{users,user-profile,identities,relations,search}`.
