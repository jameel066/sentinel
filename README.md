# 🛡️ SENTINEL

**Self-hosted access protection for Windows workstations** — progressive lockout,
intruder photo capture, and email alerts, with everything stored locally.

![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011-0078D4?logo=windows&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-2ea44f)
![Dependencies](https://img.shields.io/badge/runtime%20deps-1%20optional-lightgrey)
![tests](https://github.com/jameel066/sentinel/actions/workflows/tests.yml/badge.svg)
![Status](https://img.shields.io/badge/status-active-brightgreen)

---

## What it is

SENTINEL is a desktop security layer for a personal or shared Windows machine.
It adds a full-screen authentication gate in front of the session, enforces a
strong password policy, and escalates its response the more often someone fails
to get in.

Most "lock my PC" scripts stop at a password prompt. SENTINEL treats repeated
failures as an incident: the lockout window doubles every cycle, a webcam frame
is captured, and an alert with the photo lands in your inbox.

```
Attempt 1-3   ──▶  normal prompt
Attempt 4     ──▶  lockout #1   15s   + photo + email
Attempt 5     ──▶  lockout #2   30s   + photo + email
Attempt 6     ──▶  lockout #3   60s   + photo + email
   ...
Attempt n     ──▶  capped at 30 minutes
```

---

## Features

| | |
|---|---|
| **Progressive lockout** | 15 s → 30 s → 60 s → … → 30 min cap. Brute force becomes impractical without locking you out for a day. |
| **Strong password policy** | Live checklist: length, upper, lower, digit, special. Strength meter updates as you type. |
| **Intruder capture** | Webcam frame saved on every lockout. Multiple OpenCV backends (DSHOW / MSMF / default) so it works on laptops with awkward drivers. |
| **Email alerts** | SMTP over TLS with the captured frame attached. Gmail app passwords supported. |
| **Dashboard** | Statistics, security log viewer with filtering, capture gallery, live settings. |
| **Installer wizard** | 5 screens, no config files to hand-edit. |
| **Auto-start** | Optional `HKCU\...\Run` entry, so the gate is up after reboot. |
| **Local only** | No telemetry, no cloud, no account. Config and captures stay in `%APPDATA%\Sentinel`. |

---

<!--
## Screenshots

Drop images into docs/screenshots/ and uncomment:

| Installer | Dashboard |
|---|---|
| ![Installer](docs/screenshots/installer.png) | ![Dashboard](docs/screenshots/dashboard.png) |

| Lockout | Captures |
|---|---|
| ![Lockout](docs/screenshots/lockout.png) | ![Captures](docs/screenshots/captures.png) |
-->

---

## Requirements

- Windows 7 / 8 / 10 / 11
- Python 3.8+ with Tkinter (included in the python.org installer)
- Optional: `opencv-python` for intruder capture

```powershell
pip install -r requirements.txt
```

Without OpenCV everything still works — capture is simply disabled and the UI
says so.

---

## Installation

```powershell
git clone https://github.com/jameel066/sentinel.git
cd sentinel
python sentinel.py
```

First run opens the setup wizard. It asks for an admin account, an optional
SMTP configuration, and the lockout policy — then writes
`%APPDATA%\Sentinel\config.json`.

---

## Usage

```powershell
python sentinel.py              # smart launch: installer first run, dashboard after
python sentinel.py --login      # jump straight to the authentication screen
python sentinel.py --dashboard  # open the control panel
python sentinel.py --uninstall  # remove config, logs, captures and the autostart entry
python sentinel.py --help
```

---

## How the lockout works

```python
duration = INITIAL_LOCKOUT_SECONDS * (2 ** (lockout_count - 1))
duration = min(duration, MAX_LOCKOUT_SECONDS)   # 30 minutes
```

The counter lives for the lifetime of the process; `lockout_count` is what makes
the timer escalate rather than reset. Configurable failed-attempt threshold
(1–10) is set in the wizard.

---

## Tests

```powershell
python -m unittest discover -s tests -v
```

13 tests cover password hashing (format, salting, legacy migration, malformed
input), the password policy, and secret-at-rest encryption. CI runs them on
Windows for Python 3.9 and 3.12 via GitHub Actions.

---

## Security design

| Control | Implementation |
|---|---|
| Password storage | **PBKDF2-HMAC-SHA256**, 310,000 iterations, 16-byte random salt per user |
| Password comparison | `hmac.compare_digest` (constant time) |
| Legacy migration | Unsalted SHA-256 hashes from ≤ 4.0 are verified once, then transparently upgraded |
| SMTP credential at rest | **Windows DPAPI** — ciphertext is bound to the current Windows account |
| Runtime installs | None. The app never calls pip on your behalf |
| Network | Only outbound SMTP, only when you enable email alerts |

> DPAPI means `config.json` copied to another machine (or opened under another
> Windows account) yields an unusable email password, not a stolen one.

---

## Privacy and limitations

SENTINEL is a **deterrent and an audit trail**, not a security boundary.

- **A local admin can bypass it.** Kill the process, boot into Safe Mode, or
  edit the registry. It protects against casual access, not a determined
  attacker with physical control of the machine.
- **Webcam capture needs consent.** Use it only on hardware you own or are
  authorised to monitor, and check your local law. Capturing people without
  consent is illegal in many jurisdictions.
- **Captures are unencrypted files** in `%APPDATA%\Sentinel\captures`. Encrypt
  the volume (BitLocker) if the photos matter.
- **Tkinter is not hardened.** It is a deterrent UI, not a secure desktop.
- Do not deploy this to monitor other people. That is the exact behaviour this
  project exists to help you defend against.

---

## Project layout

```
sentinel.py          single-file application (UI, auth, capture, alerts)
requirements.txt     one optional dependency
SECURITY.md          threat model, controls, responsible disclosure
docs/screenshots/    UI captures used in this README
```

---

## License

MIT — see [LICENSE](LICENSE).

## Disclaimer

Provided for educational and personal defensive use. You are responsible for
complying with the law and with the policy of any machine you install it on.
