# Auth & Guest Session Contract v1

**Status:** ACCEPTED — shared REST contract for web, iOS, Android.  
**Role:** Source of truth for login/session/guest profile bind.  
**Related:** [PRODUCT_DATA_INTAKE.md](./PRODUCT_DATA_INTAKE.md) · [audits/FULL_USER_PATH_CANON_V1.md](./audits/FULL_USER_PATH_CANON_V1.md)

**Rule:** Auth is **Bearer tokens only** (Authorization header). Do not rely on HttpOnly cookies as the sole session channel — native apps use Keychain / EncryptedSharedPreferences.

---

## 1. Token pair

### Response shape (login · signup · magic-login · OAuth · refresh)

```json
{
  "user_id": 123,
  "email": "user@example.com",
  "access_token": "<jwt>",
  "refresh_token": "<opaque>",
  "expires_in": 3600,
  "token_type": "bearer",
  "token": "<jwt>"
}
```

| Field | Notes |
|-------|--------|
| `access_token` | JWT, short TTL (default **60 min**) |
| `refresh_token` | Opaque, stored hashed server-side; default TTL **90 days** (sliding on refresh) |
| `expires_in` | Access TTL in seconds |
| `token` | **Alias** of `access_token` for legacy clients |

### Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/auth/login` | Email + password → token pair |
| `POST` | `/auth/email-signup` | Magic signup (may omit tokens until magic) |
| `POST` | `/auth/magic-login` | Magic link → token pair |
| `POST` | `/oauth/google` · `/oauth/apple` · … | OAuth → token pair |
| `POST` | `/auth/refresh` | Body `{ "refresh_token" }` → new pair (rotation) |
| `POST` | `/auth/logout` | Body `{ "refresh_token" }` → revoke one |
| `POST` | `/auth/logout-all` | Bearer access → revoke all refresh for user |
| `GET` | `/auth/me` | Bearer access → profile |

### `stay_logged_in`

From `UserSettings.stay_logged_in` (default `true`):

- `true` → refresh TTL 90 days, sliding.
- `false` → refresh TTL **1 day**, no slide beyond that window.

Password change / reset → revoke **all** refresh tokens for the user.

### Client storage

| Platform | Access | Refresh |
|----------|--------|---------|
| Web | `localStorage` (`todayflow_token`) | `localStorage` (`todayflow_refresh_token`) |
| iOS | Keychain | Keychain |
| Android | EncryptedSharedPreferences | EncryptedSharedPreferences |

On **401** from a protected API: attempt **one** `/auth/refresh`; retry original request; if refresh fails → clear credentials and treat as logged out. Do **not** clear guest drafts on access-token expiry alone.

---

## 2. Guest identity

Already shipped:

- `guest_session_id` + `session_secret` (hashed at rest)
- Progress sync + claim token under `/today/guest/*`

Same IDs work on web and apps. Persist `guest_session_id` + `session_secret` across magic-link navigation (new tab / deep link).

---

## 3. GuestProfile DTO (pre-account)

Durable rows in Postgres (`guest_profiles`). Client localStorage is cache/offline buffer only.

```json
{
  "local_key": "self",
  "display_name": "Анна",
  "birth_date": "1990-05-12",
  "birth_time": "14:30:00",
  "birth_time_known": true,
  "location_name": "Москва",
  "latitude": 55.75,
  "longitude": 37.62,
  "timezone_name": "Europe/Moscow",
  "relation": "self",
  "is_owner_candidate": true,
  "natal_facts": null
}
```

`local_key`: `self` | `person_a` | `person_b` (1A pair).

### Endpoints

| Method | Path | Auth |
|--------|------|------|
| `POST` | `/guest/profiles` | guest_session_id + session_secret |
| `GET` | `/guest/profiles` | guest_session_id + session_secret |
| `POST` | `/guest/profiles/compat-pair` | guest_session_id + session_secret |

### Claim

| Method | Path | Auth |
|--------|------|------|
| `POST` | `/today/guest/claim` (existing) + profile bind | Bearer user + claim_token |

Claim reads **server** `guest_profiles` → creates `AstroProfile`(s) → persists natal_facts → seals guest session. Idempotent via `GuestClaimRecord`. On partial failure: **do not** delete server drafts; return retryable error.

---

## 4. Mobile checklist

- [ ] Login / magic / OAuth store access + refresh
- [ ] 401 → refresh → retry
- [ ] Guest session secret survives app restart
- [ ] Upsert guest profiles before email save
- [ ] Claim after magic uses server profiles, not device-only drafts
- [ ] Core profile cache keyed by `profile_hash` / user id

---

## Changelog

| Date | Change |
|------|--------|
| 2026-07-23 | v1 — access+refresh, guest_profiles, Bearer-only rule |
