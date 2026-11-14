# Changelog

## 4.1.0 — security hardening

No UI changes. Everything here addresses findings from a pre-release review
before the code was published.

### Fixed

- **Password hashing upgraded to PBKDF2-HMAC-SHA256** (310,000 iterations,
  16-byte random salt per user). Version 4.0 stored a bare unsalted SHA-256
  digest, which is trivially crackable from a copied `config.json`.
- **Transparent hash migration.** Existing accounts keep working: a legacy
  SHA-256 hash is verified once and rewritten in the new format on the next
  successful login.
- **SMTP credential encrypted at rest** with Windows DPAPI instead of being
  stored in plaintext. The ciphertext is bound to the current Windows account,
  so it is useless on another machine or under another user.
- **Runtime package installation removed.** Earlier builds ran
  `pip install opencv-python` on startup, which is a supply-chain risk and
  fails on offline or locked-down hosts. The dependency is now declared in
  `requirements.txt` and the application degrades gracefully without it.
- **Constant-time password comparison** via `hmac.compare_digest` instead of
  `==`.

### Changed

- `setup_opencv()` is no longer executed at import time. The module can now be
  imported by tests and tooling without side effects.
- Console output is reconfigured to UTF-8 with replacement characters so
  legacy Windows code pages cannot crash the startup banner.
- Licence changed from "Educational Use" to MIT.

### Added

- `SECURITY.md` with threat model, controls and known limitations.
- `tests/test_security.py` covering hashing, policy and secret storage.
- GitHub Actions workflow running the tests on Windows.

## 4.0

- Initial public baseline: installer wizard, dashboard, progressive lockout,
  webcam capture, SMTP alerts, autostart.
