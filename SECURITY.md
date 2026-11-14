# Security Policy

## Supported versions

| Version | Supported |
| --- | --- |
| 4.1.x | ✅ |
| ≤ 4.0 | ❌ (unsalted password hashes, plaintext SMTP password) |

## Reporting a vulnerability

Open a private security advisory on this repository
(**Security → Report a vulnerability**) or email the maintainer listed on the
GitHub profile. Please do not open a public issue for anything exploitable.

Include:

- affected version and Windows build
- reproduction steps
- impact
- a suggested fix if you have one

Expect an acknowledgement within a few days. This is a personal project, so
there is no paid bounty.

---

## Threat model

### What SENTINEL defends against

| Adversary | Covered? | How |
| --- | --- | --- |
| Someone who walks up to an unlocked machine | ✅ | Full-screen auth gate, progressive lockout |
| Shoulder-surfing the password field | ✅ | Masked input by default, optional reveal |
| Password reuse / dump from `config.json` | ✅ | PBKDF2-SHA256, per-user salt, 310k iterations |
| Reading the SMTP password from `config.json` | ✅ | Windows DPAPI, bound to the Windows account |
| Not knowing who tried to log in | ✅ | Webcam capture on each lockout |
| Missing the event until later | ✅ | SMTP alert with attached frame |

### What it does **not** defend against

| Adversary | Status | Why |
| --- | --- | --- |
| Local administrator | ❌ | Can terminate the process, edit the registry, or read memory |
| Offline / Safe Mode boot | ❌ | Autostart entry is not a boot-time driver |
| Malware already running as your user | ❌ | Same-integrity process can read `%APPDATA%` and call DPAPI |
| Network attacker | ➖ | Out of scope; the app makes no inbound connections |
| Screen recording | ❌ | Out of scope |

**SENTINEL is a deterrent plus an audit trail, not a mandatory access control
boundary.** Windows itself provides that: use a real account password, lock on
idle, and enable BitLocker.

---

## Controls and rationale

### Password hashing

```
pbkdf2_sha256$310000$<salt hex>$<digest hex>
```

- Per-user 16-byte salt from `os.urandom`
- 310,000 iterations — the OWASP 2023 recommendation for PBKDF2-HMAC-SHA256
- Constant-time comparison via `hmac.compare_digest`
- Hashes from version ≤ 4.0 (bare unsalted SHA-256) are accepted once and then
  replaced on the next successful login, so upgrades do not lock users out

### SMTP credential

The app password must be available without user interaction (alerts fire when
nobody is at the keyboard), so it cannot be hashed. It is encrypted with
`CryptProtectData` (DPAPI) under the current Windows logon. Consequences:

- Copying `config.json` to another machine → blob cannot be decrypted
- Another Windows user reading the file → blob cannot be decrypted

Failure to encrypt falls back to plaintext so the app keeps working; if you see
a plaintext password in `config.json`, DPAPI failed on that host and you should
rotate the Gmail app password.

### Runtime package installation

Earlier builds ran `pip install opencv-python` on startup. That is a
supply-chain risk (network fetch + code execution during launch) and breaks
offline or locked-down hosts. Version 4.1.0 never installs packages; the
dependency is declared in `requirements.txt` and the app degrades gracefully.

### Logging

`security.log`, `statistics.json` and captured frames live in
`%APPDATA%\Sentinel`. They are **not encrypted at rest** — protect the volume,
not just the app, if the audit trail is sensitive.

---

## Hardening checklist for users

- [ ] Use a unique password, not one used anywhere else
- [ ] Use a Gmail **app password**, never your account password
- [ ] Enable BitLocker on the drive holding `%APPDATA%`
- [ ] Use the webcam feature only on hardware you own or are authorised to monitor
- [ ] Check your local law before capturing images of people
- [ ] Install from this repository only — verify the source you run

---

## Legal note

Webcam capture and login monitoring can be unlawful when applied to other
people without consent. This project is intended for protecting your own
machine. Misuse is the operator's responsibility, not the author's.
