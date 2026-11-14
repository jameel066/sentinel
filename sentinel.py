#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════
  ███████ ███████ ███    ██ ████████ ██ ███    ██ ███████ ██      
  ██      ██      ████   ██    ██    ██ ████   ██ ██      ██      
  ███████ █████   ██ ██  ██    ██    ██ ██ ██  ██ █████   ██      
       ██ ██      ██  ██ ██    ██    ██ ██  ██ ██ ██      ██      
  ███████ ███████ ██   ████    ██    ██ ██   ████ ███████ ███████ 
═══════════════════════════════════════════════════════════════════════
  SENTINEL — Advanced Access Protection System
  Enterprise-Grade Windows Security Suite
═══════════════════════════════════════════════════════════════════════

  Version:    4.1.0
  Platform:   Windows 7/8/10/11
  License:    MIT (see LICENSE)
  
  CORE FEATURES:
  ──────────────────────────────────────────────────────────────────
  • Animated Splash Screen with Loading
  • 5-Step Installation Wizard with Step Indicator
  • Full-Featured Dashboard with Sidebar Navigation
  • Live Security Analytics & Statistics
  • Intruder Photo Gallery
  • Security Log Viewer with Filtering
  • Real-time Settings Panel
  • Show/Hide Password Toggle
  • Strong Password Enforcement (5-rule policy)
  • Progressive Lockout Timer (15s → 30s → 60s → ... → 30min)
  • Webcam Intruder Capture
  • Email Alert System with SMTP
  • PBKDF2-SHA256 Password Hashing (310,000 iterations)
  • Windows Registry Auto-Start
  • Privacy-First Design (100% local storage)
═══════════════════════════════════════════════════════════════════════
"""

import os
import sys
import json
import hmac
import base64
import ctypes
import hashlib
import platform
import threading
import smtplib
import shutil
from datetime import datetime, timedelta
from email.message import EmailMessage
import tkinter as tk
from tkinter import messagebox, filedialog
import glob

# Legacy Windows consoles default to a code page that cannot render the
# box-drawing characters used below. Reconfigure rather than crash.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# ════════════════════════════════════════════════════════════════════
#  BRAND CONFIGURATION
# ════════════════════════════════════════════════════════════════════

APP_NAME = "SENTINEL"
APP_TAGLINE = "Advanced Access Protection System"
APP_VERSION = "4.1.0"
APP_FOLDER = "Sentinel"
APP_REGISTRY_KEY = "Sentinel"

# ════════════════════════════════════════════════════════════════════
#  THEME — ENTERPRISE DESIGN SYSTEM
# ════════════════════════════════════════════════════════════════════

class Theme:
    """Enterprise design system inspired by modern security platforms"""
    
    # ─── PRIMARY PALETTE ───
    PRIMARY = '#1E3A8A'           # Deep navy blue
    PRIMARY_LIGHT = '#3B82F6'     # Bright blue
    PRIMARY_LIGHTER = '#DBEAFE'   # Pale blue
    PRIMARY_DARK = '#1E293B'      # Near black
    
    # ─── ACCENT COLORS ───
    ACCENT = '#06B6D4'            # Cyan
    ACCENT_LIGHT = '#CFFAFE'      # Pale cyan
    
    # ─── STATUS COLORS ───
    SUCCESS = '#059669'           # Emerald
    SUCCESS_LIGHT = '#D1FAE5'
    WARNING = '#D97706'           # Amber
    WARNING_LIGHT = '#FEF3C7'
    DANGER = '#DC2626'            # Red
    DANGER_LIGHT = '#FEE2E2'
    
    # ─── NEUTRALS ───
    BG = '#F8FAFC'                # Light gray bg
    BG_CARD = '#FFFFFF'           # Card background
    BG_DARK = '#0F172A'           # Sidebar dark
    BG_DARKER = '#020617'         # Darker accent
    
    BORDER = '#E2E8F0'            # Light border
    BORDER_DARK = '#334155'       # Dark border
    
    TEXT_PRIMARY = '#0F172A'      # Almost black
    TEXT_SECONDARY = '#475569'    # Medium gray
    TEXT_MUTED = '#94A3B8'        # Light gray
    TEXT_WHITE = '#FFFFFF'
    TEXT_DIM = '#CBD5E1'          # Dim white for dark bg
    
    # ─── SIDEBAR ───
    SIDEBAR_BG = '#0F172A'
    SIDEBAR_HOVER = '#1E293B'
    SIDEBAR_ACTIVE = '#3B82F6'
    SIDEBAR_TEXT = '#CBD5E1'
    SIDEBAR_TEXT_ACTIVE = '#FFFFFF'
    
    # ─── FOOTER ───
    FOOTER_BG = '#F1F5F9'
    
    # ─── TYPOGRAPHY ───
    FONT = 'Segoe UI'
    FONT_MONO = 'Consolas'

# ════════════════════════════════════════════════════════════════════
#  WINDOW SIZES
# ════════════════════════════════════════════════════════════════════

SPLASH_WIDTH, SPLASH_HEIGHT = 500, 320
INSTALLER_WIDTH, INSTALLER_HEIGHT = 800, 680
DASHBOARD_WIDTH, DASHBOARD_HEIGHT = 1100, 720

# Lockout configuration
INITIAL_LOCKOUT_SECONDS = 15
MAX_LOCKOUT_SECONDS = 1800  # 30 minutes

# ════════════════════════════════════════════════════════════════════
#  PLATFORM CHECK
# ════════════════════════════════════════════════════════════════════

if platform.system() != 'Windows':
    print(f"⚠️  {APP_NAME} requires Windows OS")
    input("\nPress Enter to exit...")
    sys.exit(0)

# ════════════════════════════════════════════════════════════════════
#  OPENCV AUTO-INSTALL
# ════════════════════════════════════════════════════════════════════

OPENCV_AVAILABLE = False
cv2 = None

def setup_opencv():
    global OPENCV_AVAILABLE, cv2
    
    print(f"\n{'═' * 70}")
    print(f"  {APP_NAME} v{APP_VERSION}")
    print(f"  {APP_TAGLINE}")
    print(f"{'═' * 70}")
    print("  Initializing system components...\n")
    
    try:
        import cv2 as cv2_module
        cv2 = cv2_module
        OPENCV_AVAILABLE = True
        print("  ✓ Camera subsystem ready")
    except ImportError:
        # Never install packages at runtime: silent pip calls are a supply-chain
        # risk and break on locked-down or offline machines.
        print("  ! Camera subsystem not installed")
        print("    Optional. Enable intruder capture with:")
        print("      pip install -r requirements.txt")
        print("    Continuing with capture disabled.")
    
    print(f"{'═' * 70}\n")

# ════════════════════════════════════════════════════════════════════
#  SECRET PROTECTION — WINDOWS DPAPI
# ════════════════════════════════════════════════════════════════════
#
# The SMTP app password must be recoverable without user interaction, so it
# cannot be hashed. It is instead encrypted at rest with Windows DPAPI, which
# binds the ciphertext to the current Windows account. Copying config.json to
# another machine or another user makes the blob useless.

SECRET_PREFIX = "dpapi:"


class _DataBlob(ctypes.Structure):
    _fields_ = [
        ("cbData", ctypes.c_uint32),
        ("pbData", ctypes.POINTER(ctypes.c_char)),
    ]


def _blob_from_bytes(data):
    """Build a DATA_BLOB that keeps its backing buffer alive."""
    buffer = ctypes.create_string_buffer(data, len(data))
    blob = _DataBlob(len(data), ctypes.cast(buffer, ctypes.POINTER(ctypes.c_char)))
    return blob, buffer


def protect_secret(plaintext):
    """Encrypt a secret with DPAPI. Returns 'dpapi:<base64>' or the input."""
    if not plaintext:
        return ""
    if plaintext.startswith(SECRET_PREFIX):
        return plaintext
    try:
        blob_in, _keep_alive = _blob_from_bytes(plaintext.encode("utf-8"))
        blob_out = _DataBlob()
        if not ctypes.windll.crypt32.CryptProtectData(
            ctypes.byref(blob_in), None, None, None, None, 0, ctypes.byref(blob_out)
        ):
            return plaintext
        try:
            cipher = ctypes.string_at(blob_out.pbData, blob_out.cbData)
        finally:
            ctypes.windll.kernel32.LocalFree(blob_out.pbData)
        return SECRET_PREFIX + base64.b64encode(cipher).decode("ascii")
    except Exception:
        return plaintext


def unprotect_secret(stored):
    """Decrypt a DPAPI blob. Legacy plaintext values pass through unchanged."""
    if not stored:
        return ""
    if not stored.startswith(SECRET_PREFIX):
        return stored
    try:
        cipher = base64.b64decode(stored[len(SECRET_PREFIX):])
        blob_in, _keep_alive = _blob_from_bytes(cipher)
        blob_out = _DataBlob()
        if not ctypes.windll.crypt32.CryptUnprotectData(
            ctypes.byref(blob_in), None, None, None, None, 0, ctypes.byref(blob_out)
        ):
            return ""
        try:
            plain = ctypes.string_at(blob_out.pbData, blob_out.cbData)
        finally:
            ctypes.windll.kernel32.LocalFree(blob_out.pbData)
        return plain.decode("utf-8", "replace")
    except Exception:
        return ""


# ════════════════════════════════════════════════════════════════════
#  CONFIGURATION MANAGER
# ════════════════════════════════════════════════════════════════════

class ConfigManager:
    """Centralized configuration and data management"""
    
    def __init__(self):
        self.app_dir = os.path.join(os.getenv('APPDATA'), APP_FOLDER)
        self.config_file = os.path.join(self.app_dir, 'config.json')
        self.log_file = os.path.join(self.app_dir, 'security.log')
        self.capture_dir = os.path.join(self.app_dir, 'captures')
        self.stats_file = os.path.join(self.app_dir, 'statistics.json')
        
        os.makedirs(self.app_dir, exist_ok=True)
        os.makedirs(self.capture_dir, exist_ok=True)
    
    def save(self, data):
        try:
            payload = json.loads(json.dumps(data))
            email = payload.get("email")
            if isinstance(email, dict) and email.get("password"):
                email["password"] = protect_secret(str(email["password"]))
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(payload, f, indent=4)
            return True
        except Exception:
            return False
    
    def load(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                email = data.get("email")
                if isinstance(email, dict) and email.get("password"):
                    email["password"] = unprotect_secret(str(email["password"]))
                return data
        except Exception:
            pass
        return None
    
    def exists(self):
        return os.path.exists(self.config_file)
    
    def log(self, message, level="INFO"):
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(f"[{timestamp}] [{level}] {message}\n")
        except Exception:
            pass
    
    def load_logs(self, limit=100):
        """Load security logs"""
        if not os.path.exists(self.log_file):
            return []
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            return lines[-limit:] if limit else lines
        except Exception:
            return []
    
    def get_captures(self):
        """Get list of captured intruder photos"""
        if not os.path.exists(self.capture_dir):
            return []
        files = glob.glob(os.path.join(self.capture_dir, "*.jpg"))
        return sorted(files, key=os.path.getmtime, reverse=True)
    
    def load_stats(self):
        """Load statistics"""
        try:
            if os.path.exists(self.stats_file):
                with open(self.stats_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return {
            'total_logins': 0,
            'successful_logins': 0,
            'failed_attempts': 0,
            'total_lockouts': 0,
            'photos_captured': 0,
            'emails_sent': 0,
            'last_login': None,
            'last_lockout': None
        }
    
    def update_stats(self, **kwargs):
        """Update statistics counters"""
        try:
            stats = self.load_stats()
            for key, value in kwargs.items():
                if key in stats:
                    if isinstance(stats[key], (int, float)):
                        stats[key] += value
                    else:
                        stats[key] = value
            with open(self.stats_file, 'w') as f:
                json.dump(stats, f, indent=4)
        except Exception:
            pass

# ════════════════════════════════════════════════════════════════════
#  PASSWORD UTILITIES
# ════════════════════════════════════════════════════════════════════

HASH_PREFIX = "pbkdf2_sha256$"
PBKDF2_ITERATIONS = 310_000


def hash_password(password):
    """Hash a password with PBKDF2-HMAC-SHA256 and a random 16-byte salt."""
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS
    )
    return f"{HASH_PREFIX}{PBKDF2_ITERATIONS}${salt.hex()}${digest.hex()}"


def verify_password(stored, password):
    """Constant-time verification, with support for legacy v4.0 hashes."""
    if not stored:
        return False

    if stored.startswith(HASH_PREFIX):
        try:
            _, iterations, salt_hex, digest_hex = stored.split("$", 3)
            digest = hashlib.pbkdf2_hmac(
                "sha256",
                password.encode("utf-8"),
                bytes.fromhex(salt_hex),
                int(iterations),
            )
            return hmac.compare_digest(digest.hex(), digest_hex)
        except (ValueError, TypeError):
            return False

    # SENTINEL <= 4.0 stored a bare unsalted SHA-256 digest. It is still
    # accepted once and then transparently upgraded on the next login.
    legacy = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return hmac.compare_digest(legacy, stored)

def check_password_requirements(password):
    return {
        'length': len(password) >= 8,
        'uppercase': any(c.isupper() for c in password),
        'lowercase': any(c.islower() for c in password),
        'digit': any(c.isdigit() for c in password),
        'special': any(not c.isalnum() and not c.isspace() for c in password)
    }

def calculate_password_strength(password):
    if not password:
        return "—", Theme.TEXT_MUTED, check_password_requirements("")
    
    reqs = check_password_requirements(password)
    score = sum(reqs.values())
    
    if score == 5:
        return "Strong", Theme.SUCCESS, reqs
    elif score >= 3:
        return "Medium", Theme.WARNING, reqs
    else:
        return "Weak", Theme.DANGER, reqs

def is_password_acceptable(password):
    return all(check_password_requirements(password).values())

# ════════════════════════════════════════════════════════════════════
#  SECURITY ACTIONS
# ════════════════════════════════════════════════════════════════════

def capture_intruder():
    """Capture webcam photo with multiple backend fallback"""
    if not OPENCV_AVAILABLE or cv2 is None:
        return None
    
    try:
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not cap.isOpened():
            cap = cv2.VideoCapture(0, cv2.CAP_MSMF)
        if not cap.isOpened():
            cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            return None
        
        for _ in range(8):
            cap.read()
        
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            return None
        
        config = ConfigManager()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(config.capture_dir, f"intruder_{timestamp}.jpg")
        cv2.imwrite(path, frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
        
        config.update_stats(photos_captured=1)
        return path
    except Exception:
        return None

def send_security_alert(email_cfg, image_path, username, attempts, lockout_count, lockout_duration):
    try:
        sender = email_cfg.get('sender')
        password = email_cfg.get('password')
        receiver = email_cfg.get('receiver')
        
        if not all([sender, password, receiver]):
            return False
        
        msg = EmailMessage()
        msg['Subject'] = f"🚨 SENTINEL ALERT: Lockout #{lockout_count} - Unauthorized Access Attempt"
        msg['From'] = f"SENTINEL Security <{sender}>"
        msg['To'] = receiver
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        body = f"""
╔══════════════════════════════════════════════════════════════╗
║   🛡️  SENTINEL SECURITY ALERT — UNAUTHORIZED ACCESS DETECTED   ║
╠══════════════════════════════════════════════════════════════╣

  LOCKOUT INCIDENT #{lockout_count}
  
  ─────────────────────────────────────────────────────────────
   INCIDENT DETAILS
  ─────────────────────────────────────────────────────────────
  
  Timestamp:         {timestamp}
  Computer Name:     {platform.node()}
  Operating System:  Windows {platform.release()}
  Attempted User:    {username}
  Failed Attempts:   {attempts}
  Lockout Duration:  {lockout_duration} seconds
  Lockout Number:    #{lockout_count} (this session)
  
  ─────────────────────────────────────────────────────────────
   ACTIONS TAKEN
  ─────────────────────────────────────────────────────────────
  
  ✓ Account locked for {lockout_duration} seconds
  ✓ Intruder image captured {'(see attachment)' if image_path else '(camera unavailable)'}
  ✓ Event logged to security audit trail
  ✓ Administrator notified via email
  
  ─────────────────────────────────────────────────────────────
   PROGRESSIVE LOCKOUT INFORMATION
  ─────────────────────────────────────────────────────────────
  
  Current Lockout:  {lockout_duration} seconds
  Next Lockout:     {min(lockout_duration * 2, MAX_LOCKOUT_SECONDS)} seconds
  
  Each lockout duration DOUBLES until reaching the 30-minute cap.
  This deterrent makes brute-force attacks extremely impractical.
  
  ─────────────────────────────────────────────────────────────
   RECOMMENDED ACTIONS
  ─────────────────────────────────────────────────────────────
  
  1. Review the attached intruder photo
  2. Check SENTINEL dashboard for full activity log
  3. Verify physical security of your device
  4. Consider changing your password if compromise suspected
  5. Review whether familiar individuals had access

╠══════════════════════════════════════════════════════════════╣
║  SENTINEL v{APP_VERSION}                                       
║  Advanced Access Protection System                            
║  Automated Security Monitoring                                
╚══════════════════════════════════════════════════════════════╝
"""
        msg.set_content(body)
        
        if image_path and os.path.exists(image_path):
            with open(image_path, 'rb') as f:
                msg.add_attachment(
                    f.read(),
                    maintype='image',
                    subtype='jpeg',
                    filename=os.path.basename(image_path)
                )
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=15) as smtp:
            smtp.login(sender, password)
            smtp.send_message(msg)
        
        ConfigManager().update_stats(emails_sent=1)
        return True
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")
        return False

def enable_autostart():
    try:
        import winreg
        script_path = os.path.abspath(__file__)
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(
            key, APP_REGISTRY_KEY, 0, winreg.REG_SZ,
            f'"{sys.executable}" "{script_path}" --login'
        )
        winreg.CloseKey(key)
        return True
    except Exception:
        return False

def disable_autostart():
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_SET_VALUE
        )
        try:
            winreg.DeleteValue(key, APP_REGISTRY_KEY)
        except FileNotFoundError:
            pass
        winreg.CloseKey(key)
        return True
    except Exception:
        return False

def check_autostart_enabled():
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_READ
        )
        try:
            winreg.QueryValueEx(key, APP_REGISTRY_KEY)
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            winreg.CloseKey(key)
            return False
    except Exception:
        return False

# ════════════════════════════════════════════════════════════════════
#  CUSTOM UI COMPONENTS
# ════════════════════════════════════════════════════════════════════

class ModernButton(tk.Button):
    """Flat modern button with hover effects"""
    
    def __init__(self, parent, text, command, style='primary', width=14, **kwargs):
        styles = {
            'primary': (Theme.PRIMARY_LIGHT, Theme.PRIMARY, Theme.TEXT_WHITE),
            'success': (Theme.SUCCESS, '#047857', Theme.TEXT_WHITE),
            'secondary': ('#94A3B8', '#64748B', Theme.TEXT_WHITE),
            'danger': (Theme.DANGER, '#B91C1C', Theme.TEXT_WHITE),
            'ghost': (Theme.BG_CARD, Theme.BORDER, Theme.TEXT_PRIMARY),
        }
        
        bg, hover_bg, fg = styles.get(style, styles['primary'])
        
        super().__init__(
            parent, text=text, command=command,
            font=(Theme.FONT, 10, 'bold'),
            bg=bg, fg=fg,
            activebackground=hover_bg, activeforeground=fg,
            relief='flat', borderwidth=0, cursor='hand2',
            width=width, height=2, **kwargs
        )
        
        self._bg = bg
        self._hover_bg = hover_bg
        
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
    
    def _on_enter(self, e):
        if self['state'] == 'normal':
            self.config(bg=self._hover_bg)
    
    def _on_leave(self, e):
        if self['state'] == 'normal':
            self.config(bg=self._bg)


class PasswordEntry(tk.Frame):
    """Password entry with show/hide toggle"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=Theme.BG_CARD)
        
        self.is_shown = False
        
        self.container = tk.Frame(
            self,
            bg=Theme.BG_CARD,
            relief='solid',
            bd=1,
            highlightthickness=1,
            highlightcolor=Theme.PRIMARY_LIGHT,
            highlightbackground=Theme.BORDER
        )
        self.container.pack(fill='x')
        
        self.entry = tk.Entry(
            self.container,
            font=(Theme.FONT, 11),
            show='●',
            relief='flat',
            bd=0,
            highlightthickness=0,
            bg=Theme.BG_CARD
        )
        self.entry.pack(side='left', fill='x', expand=True, padx=10, ipady=7)
        
        self.toggle_btn = tk.Button(
            self.container,
            text="👁  Show",
            command=self.toggle_visibility,
            font=(Theme.FONT, 9),
            bg=Theme.BG_CARD,
            fg=Theme.PRIMARY_LIGHT,
            activebackground=Theme.BG_CARD,
            activeforeground=Theme.PRIMARY,
            relief='flat',
            bd=0,
            cursor='hand2',
            padx=10
        )
        self.toggle_btn.pack(side='right', padx=(0, 4))
    
    def toggle_visibility(self):
        self.is_shown = not self.is_shown
        if self.is_shown:
            self.entry.config(show='')
            self.toggle_btn.config(text="🙈  Hide")
        else:
            self.entry.config(show='●')
            self.toggle_btn.config(text="👁  Show")
    
    def get(self):
        return self.entry.get()
    
    def delete(self, first, last=None):
        if last is None:
            self.entry.delete(first)
        else:
            self.entry.delete(first, last)
    
    def insert(self, index, string):
        self.entry.insert(index, string)
    
    def config(self, **kwargs):
        if 'state' in kwargs:
            self.entry.config(state=kwargs['state'])
            self.toggle_btn.config(state=kwargs['state'])
            if kwargs['state'] == 'disabled':
                self.container.config(bg='#F1F5F9')
                self.entry.config(disabledbackground='#F1F5F9')
                self.toggle_btn.config(bg='#F1F5F9')
            else:
                self.container.config(bg=Theme.BG_CARD)
                self.toggle_btn.config(bg=Theme.BG_CARD)
    
    def bind(self, sequence, func):
        self.entry.bind(sequence, func)
    
    def focus(self):
        self.entry.focus()


class PasswordRequirements(tk.Frame):
    """Live password requirements checklist"""
    
    def __init__(self, parent):
        super().__init__(parent, bg=Theme.BG_CARD)
        
        self.requirements = [
            ('length', 'At least 8 characters'),
            ('uppercase', 'Uppercase letter (A-Z)'),
            ('lowercase', 'Lowercase letter (a-z)'),
            ('digit', 'Number (0-9)'),
            ('special', 'Special character (!@#$%...)')
        ]
        
        self.labels = {}
        
        for key, text in self.requirements:
            row = tk.Frame(self, bg=Theme.BG_CARD)
            row.pack(fill='x', pady=1)
            
            icon = tk.Label(
                row, text="○",
                font=(Theme.FONT, 9),
                bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED,
                width=2
            )
            icon.pack(side='left')
            
            label = tk.Label(
                row, text=text,
                font=(Theme.FONT, 8),
                bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED,
                anchor='w'
            )
            label.pack(side='left', fill='x', expand=True)
            
            self.labels[key] = (icon, label)
    
    def update(self, password):
        if not password:
            for key, (icon, label) in self.labels.items():
                icon.config(text="○", fg=Theme.TEXT_MUTED)
                label.config(fg=Theme.TEXT_MUTED)
            return
        
        reqs = check_password_requirements(password)
        for key, (icon, label) in self.labels.items():
            if reqs.get(key):
                icon.config(text="✓", fg=Theme.SUCCESS)
                label.config(fg=Theme.SUCCESS)
            else:
                icon.config(text="✗", fg=Theme.DANGER)
                label.config(fg=Theme.DANGER)


class StepIndicator(tk.Frame):
    """Wizard step progress indicator"""
    
    def __init__(self, parent, current, total=4):
        super().__init__(parent, bg=Theme.BG_CARD)
        
        steps = ["Welcome", "Account", "Email", "Security"]
        
        container = tk.Frame(self, bg=Theme.BG_CARD)
        container.pack(pady=14)
        
        for i in range(total):
            color = Theme.PRIMARY_LIGHT if i < current else Theme.BORDER
            text_color = Theme.TEXT_WHITE if i < current else Theme.TEXT_MUTED
            
            circle = tk.Label(
                container, text=f" {i+1} ",
                font=(Theme.FONT, 9, 'bold'),
                bg=color, fg=text_color, width=3
            )
            circle.pack(side='left', padx=3)
            
            label = tk.Label(
                container,
                text=steps[i] if i < len(steps) else f"Step {i+1}",
                font=(Theme.FONT, 9, 'bold' if i == current - 1 else 'normal'),
                bg=Theme.BG_CARD,
                fg=Theme.PRIMARY_LIGHT if i == current - 1 else Theme.TEXT_MUTED
            )
            label.pack(side='left', padx=(2, 10))
            
            if i < total - 1:
                tk.Frame(container, bg=color, height=2, width=20).pack(side='left', padx=2)


class StatCard(tk.Frame):
    """Statistic card for dashboard"""
    
    def __init__(self, parent, icon, value, label, color=Theme.PRIMARY_LIGHT):
        super().__init__(parent, bg=Theme.BG_CARD, relief='solid', bd=1)
        
        # Color accent bar at top
        tk.Frame(self, bg=color, height=4).pack(fill='x')
        
        inner = tk.Frame(self, bg=Theme.BG_CARD)
        inner.pack(fill='both', expand=True, padx=20, pady=15)
        
        # Icon
        tk.Label(
            inner, text=icon,
            font=(Theme.FONT, 24),
            bg=Theme.BG_CARD
        ).pack(anchor='w')
        
        # Value
        self.value_label = tk.Label(
            inner, text=str(value),
            font=(Theme.FONT, 24, 'bold'),
            bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY
        )
        self.value_label.pack(anchor='w', pady=(5, 0))
        
        # Label
        tk.Label(
            inner, text=label,
            font=(Theme.FONT, 9),
            bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY
        ).pack(anchor='w')
    
    def update_value(self, value):
        self.value_label.config(text=str(value))


class SidebarButton(tk.Frame):
    """Sidebar navigation button"""
    
    def __init__(self, parent, icon, text, command, is_active=False):
        super().__init__(parent, bg=Theme.SIDEBAR_BG, cursor='hand2')
        
        self.command = command
        self.is_active = is_active
        
        # Active indicator line on left
        self.indicator = tk.Frame(
            self,
            bg=Theme.SIDEBAR_ACTIVE if is_active else Theme.SIDEBAR_BG,
            width=4
        )
        self.indicator.pack(side='left', fill='y')
        
        # Content
        inner = tk.Frame(
            self,
            bg=Theme.SIDEBAR_ACTIVE if is_active else Theme.SIDEBAR_BG
        )
        inner.pack(side='left', fill='both', expand=True)
        
        self.inner = inner
        
        # Icon
        self.icon_label = tk.Label(
            inner, text=icon,
            font=(Theme.FONT, 14),
            bg=Theme.SIDEBAR_ACTIVE if is_active else Theme.SIDEBAR_BG,
            fg=Theme.SIDEBAR_TEXT_ACTIVE if is_active else Theme.SIDEBAR_TEXT
        )
        self.icon_label.pack(side='left', padx=(15, 10), pady=12)
        
        # Text
        self.text_label = tk.Label(
            inner, text=text,
            font=(Theme.FONT, 10, 'bold' if is_active else 'normal'),
            bg=Theme.SIDEBAR_ACTIVE if is_active else Theme.SIDEBAR_BG,
            fg=Theme.SIDEBAR_TEXT_ACTIVE if is_active else Theme.SIDEBAR_TEXT
        )
        self.text_label.pack(side='left', pady=12)
        
        # Bind events
        for widget in [self, inner, self.icon_label, self.text_label]:
            widget.bind('<Button-1>', lambda e: command())
            widget.bind('<Enter>', self._on_enter)
            widget.bind('<Leave>', self._on_leave)
    
    def _on_enter(self, e):
        if not self.is_active:
            self.inner.config(bg=Theme.SIDEBAR_HOVER)
            self.icon_label.config(bg=Theme.SIDEBAR_HOVER)
            self.text_label.config(bg=Theme.SIDEBAR_HOVER)
    
    def _on_leave(self, e):
        if not self.is_active:
            self.inner.config(bg=Theme.SIDEBAR_BG)
            self.icon_label.config(bg=Theme.SIDEBAR_BG)
            self.text_label.config(bg=Theme.SIDEBAR_BG)
    
    def set_active(self, active):
        self.is_active = active
        bg = Theme.SIDEBAR_ACTIVE if active else Theme.SIDEBAR_BG
        fg = Theme.SIDEBAR_TEXT_ACTIVE if active else Theme.SIDEBAR_TEXT
        weight = 'bold' if active else 'normal'
        
        self.indicator.config(bg=Theme.SIDEBAR_ACTIVE if active else Theme.SIDEBAR_BG)
        self.inner.config(bg=bg)
        self.icon_label.config(bg=bg, fg=fg)
        self.text_label.config(bg=bg, fg=fg, font=(Theme.FONT, 10, weight))

# ════════════════════════════════════════════════════════════════════
#  SPLASH SCREEN
# ════════════════════════════════════════════════════════════════════

class SplashScreen:
    """Animated splash screen on startup"""
    
    def __init__(self, on_complete):
        self.root = tk.Tk()
        self.root.title(APP_NAME)
        self.root.geometry(f"{SPLASH_WIDTH}x{SPLASH_HEIGHT}")
        self.root.overrideredirect(True)  # Remove window decorations
        self.root.configure(bg=Theme.PRIMARY_DARK)
        
        # Center
        x = (self.root.winfo_screenwidth() - SPLASH_WIDTH) // 2
        y = (self.root.winfo_screenheight() - SPLASH_HEIGHT) // 2
        self.root.geometry(f"{SPLASH_WIDTH}x{SPLASH_HEIGHT}+{x}+{y}")
        
        self.on_complete = on_complete
        
        self._build()
        self._animate()
    
    def _build(self):
        # Decorative border
        border = tk.Frame(self.root, bg=Theme.PRIMARY_LIGHT, height=4)
        border.pack(fill='x')
        
        # Main content
        content = tk.Frame(self.root, bg=Theme.PRIMARY_DARK)
        content.pack(fill='both', expand=True)
        
        center = tk.Frame(content, bg=Theme.PRIMARY_DARK)
        center.place(relx=0.5, rely=0.45, anchor='center')
        
        # Logo
        tk.Label(
            center, text="🛡️",
            font=(Theme.FONT, 64),
            bg=Theme.PRIMARY_DARK
        ).pack(pady=(0, 5))
        
        # App name
        tk.Label(
            center, text=APP_NAME,
            font=(Theme.FONT, 32, 'bold'),
            bg=Theme.PRIMARY_DARK,
            fg=Theme.TEXT_WHITE
        ).pack()
        
        # Tagline
        tk.Label(
            center, text=APP_TAGLINE,
            font=(Theme.FONT, 10),
            bg=Theme.PRIMARY_DARK,
            fg=Theme.TEXT_DIM
        ).pack(pady=(2, 0))
        
        # Version
        tk.Label(
            center, text=f"v{APP_VERSION}",
            font=(Theme.FONT, 8),
            bg=Theme.PRIMARY_DARK,
            fg=Theme.TEXT_MUTED
        ).pack(pady=(5, 0))
        
        # Loading bar
        bar_frame = tk.Frame(self.root, bg=Theme.PRIMARY_DARK)
        bar_frame.place(relx=0.5, rely=0.85, anchor='center')
        
        self.loading_bar_bg = tk.Frame(bar_frame, bg='#1E293B', width=300, height=4)
        self.loading_bar_bg.pack()
        
        self.loading_bar = tk.Frame(self.loading_bar_bg, bg=Theme.PRIMARY_LIGHT, height=4)
        self.loading_bar.place(x=0, y=0, width=0, height=4)
        
        # Status text
        self.status_label = tk.Label(
            self.root, text="Initializing...",
            font=(Theme.FONT, 8),
            bg=Theme.PRIMARY_DARK,
            fg=Theme.TEXT_MUTED
        )
        self.status_label.place(relx=0.5, rely=0.92, anchor='center')
        
        # Bottom border
        tk.Frame(self.root, bg=Theme.PRIMARY_LIGHT, height=4).pack(side='bottom', fill='x')
    
    def _animate(self):
        """Animate loading progress"""
        self.progress = 0
        self.messages = [
            ("Initializing system...", 20),
            ("Loading security modules...", 40),
            ("Checking camera subsystem...", 60),
            ("Preparing interface...", 80),
            ("Ready", 100)
        ]
        self.message_idx = 0
        self._advance()
    
    def _advance(self):
        if self.message_idx < len(self.messages):
            text, target = self.messages[self.message_idx]
            self.status_label.config(text=text)
            
            if self.progress < target:
                self.progress += 2
                self.loading_bar.place(width=int(300 * self.progress / 100))
                self.root.after(30, self._advance)
            else:
                self.message_idx += 1
                self.root.after(150, self._advance)
        else:
            self.root.after(400, self._finish)
    
    def _finish(self):
        self.root.destroy()
        self.on_complete()
    
    def run(self):
        self.root.mainloop()

# ════════════════════════════════════════════════════════════════════
#  INSTALLER WIZARD
# ════════════════════════════════════════════════════════════════════

class InstallerApp:
    """Multi-step installation wizard"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"{APP_NAME} — Setup Wizard")
        self.root.geometry(f"{INSTALLER_WIDTH}x{INSTALLER_HEIGHT}")
        self.root.resizable(False, False)
        self.root.configure(bg=Theme.BG)
        
        x = (self.root.winfo_screenwidth() - INSTALLER_WIDTH) // 2
        y = (self.root.winfo_screenheight() - INSTALLER_HEIGHT) // 2
        self.root.geometry(f"{INSTALLER_WIDTH}x{INSTALLER_HEIGHT}+{x}+{y}")
        
        self.config_mgr = ConfigManager()
        self.config_data = {
            'users': {},
            'email': {'enabled': False},
            'autostart': True,
            'max_attempts': 3,
            'capture_on_lockout': True,
            'email_on_lockout': True
        }
        
        self.show_welcome()
    
    def clear_window(self):
        for w in self.root.winfo_children():
            w.destroy()
    
    def create_header(self, title, subtitle=None):
        header = tk.Frame(self.root, bg=Theme.PRIMARY_DARK, height=95)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        # Accent line
        tk.Frame(header, bg=Theme.PRIMARY_LIGHT, height=4).pack(fill='x', side='bottom')
        
        inner = tk.Frame(header, bg=Theme.PRIMARY_DARK)
        inner.place(relx=0.5, rely=0.45, anchor='center')
        
        title_row = tk.Frame(inner, bg=Theme.PRIMARY_DARK)
        title_row.pack()
        
        tk.Label(
            title_row, text="🛡️",
            font=(Theme.FONT, 24),
            bg=Theme.PRIMARY_DARK
        ).pack(side='left', padx=(0, 10))
        
        tk.Label(
            title_row, text=title,
            font=(Theme.FONT, 18, 'bold'),
            bg=Theme.PRIMARY_DARK, fg=Theme.TEXT_WHITE
        ).pack(side='left')
        
        if subtitle:
            tk.Label(
                inner, text=subtitle,
                font=(Theme.FONT, 9),
                bg=Theme.PRIMARY_DARK, fg=Theme.TEXT_DIM
            ).pack(pady=(2, 0))
    
    def create_footer(self, buttons):
        footer = tk.Frame(self.root, bg=Theme.FOOTER_BG, height=70)
        footer.pack(side='bottom', fill='x')
        footer.pack_propagate(False)
        
        tk.Frame(footer, bg=Theme.BORDER, height=1).pack(fill='x')
        
        # Brand on left
        left = tk.Frame(footer, bg=Theme.FOOTER_BG)
        left.pack(side='left', padx=25, pady=20)
        
        tk.Label(
            left, text=f"{APP_NAME} v{APP_VERSION}",
            font=(Theme.FONT, 8),
            bg=Theme.FOOTER_BG, fg=Theme.TEXT_MUTED
        ).pack()
        
        # Buttons on right
        btn_container = tk.Frame(footer, bg=Theme.FOOTER_BG)
        btn_container.pack(side='right', padx=25, pady=15)
        
        for text, command, style in reversed(buttons):
            btn = ModernButton(btn_container, text, command, style)
            btn.pack(side='right', padx=4)
    
    # ─── SCREEN 1: WELCOME ───
    
    def show_welcome(self):
        self.clear_window()
        self.create_header(APP_NAME, APP_TAGLINE)
        StepIndicator(self.root, current=1).pack(fill='x')
        
        content = tk.Frame(self.root, bg=Theme.BG)
        content.pack(fill='both', expand=True, padx=45, pady=10)
        
        card = tk.Frame(content, bg=Theme.BG_CARD, relief='solid', bd=1)
        card.pack(fill='both', expand=True, pady=5)
        
        inner = tk.Frame(card, bg=Theme.BG_CARD)
        inner.pack(fill='both', expand=True, padx=35, pady=20)
        
        tk.Label(
            inner, text=f"Welcome to {APP_NAME}",
            font=(Theme.FONT, 16, 'bold'),
            bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY
        ).pack(anchor='w', pady=(0, 5))
        
        tk.Label(
            inner,
            text="Enterprise-grade access protection with progressive lockout, intruder capture, and real-time alerts.",
            font=(Theme.FONT, 10),
            bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY,
            wraplength=650, justify='left'
        ).pack(anchor='w', pady=(0, 18))
        
        # Feature grid (2 columns)
        features_frame = tk.Frame(inner, bg=Theme.BG_CARD)
        features_frame.pack(fill='x', pady=(0, 15))
        
        features = [
            ("🛡️", "Smart Authentication", "Strong password enforcement"),
            ("⏱️", "Progressive Lockout", "15s → 30s → 60s → 30min cap"),
            ("📸", "Intruder Capture", "Automatic webcam photography"),
            ("📧", "Email Alerts", "Real-time SMTP notifications"),
            ("📊", "Live Dashboard", "Statistics and activity monitoring"),
            ("🔒", "Privacy First", "100% local, SHA-256 encrypted"),
        ]
        
        for i, (icon, title, desc) in enumerate(features):
            row, col = i // 2, i % 2
            
            cell = tk.Frame(features_frame, bg=Theme.BG_CARD)
            cell.grid(row=row, column=col, sticky='w', padx=(0, 25), pady=4)
            
            tk.Label(
                cell, text=icon,
                font=(Theme.FONT, 14),
                bg=Theme.BG_CARD
            ).pack(side='left', padx=(0, 10))
            
            text_frame = tk.Frame(cell, bg=Theme.BG_CARD)
            text_frame.pack(side='left')
            
            tk.Label(
                text_frame, text=title,
                font=(Theme.FONT, 10, 'bold'),
                bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY,
                anchor='w'
            ).pack(anchor='w')
            
            tk.Label(
                text_frame, text=desc,
                font=(Theme.FONT, 9),
                bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY,
                anchor='w'
            ).pack(anchor='w')
        
        # System Status Card
        status_frame = tk.Frame(inner, bg=Theme.PRIMARY_LIGHTER)
        status_frame.pack(fill='x', pady=(15, 0))
        
        status_inner = tk.Frame(status_frame, bg=Theme.PRIMARY_LIGHTER)
        status_inner.pack(fill='x', padx=15, pady=10)
        
        tk.Label(
            status_inner, text="⚡ SYSTEM READY",
            font=(Theme.FONT, 9, 'bold'),
            bg=Theme.PRIMARY_LIGHTER, fg=Theme.PRIMARY
        ).pack(anchor='w')
        
        tk.Label(
            status_inner,
            text=f"Windows {platform.release()}  •  Python {sys.version_info.major}.{sys.version_info.minor}  •  Camera: {'Ready ✓' if OPENCV_AVAILABLE else 'Unavailable'}",
            font=(Theme.FONT, 9),
            bg=Theme.PRIMARY_LIGHTER, fg=Theme.PRIMARY
        ).pack(anchor='w', pady=(2, 0))
        
        self.create_footer([
            ("Exit", self.root.destroy, 'secondary'),
            ("Get Started →", self.show_account_setup, 'primary')
        ])
    
    # ─── SCREEN 2: ACCOUNT SETUP ───
    
    def show_account_setup(self):
        self.clear_window()
        self.create_header("Create Your Account", "Set up secure credentials")
        StepIndicator(self.root, current=2).pack(fill='x')
        
        content = tk.Frame(self.root, bg=Theme.BG)
        content.pack(fill='both', expand=True, padx=45, pady=5)
        
        card = tk.Frame(content, bg=Theme.BG_CARD, relief='solid', bd=1)
        card.pack(fill='both', expand=True, pady=5)
        
        inner = tk.Frame(card, bg=Theme.BG_CARD)
        inner.pack(fill='both', expand=True, padx=40, pady=18)
        
        tk.Label(
            inner, text="Account Credentials",
            font=(Theme.FONT, 14, 'bold'),
            bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY
        ).pack(anchor='w', pady=(0, 12))
        
        # Username
        tk.Label(
            inner, text="Username",
            font=(Theme.FONT, 10, 'bold'),
            bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY
        ).pack(anchor='w', pady=(0, 3))
        
        self.username_entry = tk.Entry(
            inner,
            font=(Theme.FONT, 11),
            relief='solid', bd=1,
            highlightthickness=1,
            highlightcolor=Theme.PRIMARY_LIGHT,
            highlightbackground=Theme.BORDER
        )
        self.username_entry.pack(fill='x', ipady=6, pady=(0, 12))
        
        # Password with show/hide
        pwd_header = tk.Frame(inner, bg=Theme.BG_CARD)
        pwd_header.pack(fill='x', pady=(0, 3))
        
        tk.Label(
            pwd_header, text="Password",
            font=(Theme.FONT, 10, 'bold'),
            bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY
        ).pack(side='left')
        
        self.strength_label = tk.Label(
            pwd_header, text="",
            font=(Theme.FONT, 9, 'bold'),
            bg=Theme.BG_CARD
        )
        self.strength_label.pack(side='right')
        
        self.password_entry = PasswordEntry(inner)
        self.password_entry.pack(fill='x', pady=(0, 8))
        self.password_entry.bind('<KeyRelease>', self.update_password_strength)
        
        # Requirements
        req_frame = tk.Frame(inner, bg=Theme.BG_CARD)
        req_frame.pack(fill='x', pady=(0, 12))
        
        tk.Label(
            req_frame, text="Password must contain:",
            font=(Theme.FONT, 9, 'bold'),
            bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY
        ).pack(anchor='w')
        
        self.requirements_widget = PasswordRequirements(req_frame)
        self.requirements_widget.pack(fill='x', padx=10, pady=(3, 0))
        
        # Confirm
        tk.Label(
            inner, text="Confirm Password",
            font=(Theme.FONT, 10, 'bold'),
            bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY
        ).pack(anchor='w', pady=(0, 3))
        
        self.confirm_entry = PasswordEntry(inner)
        self.confirm_entry.pack(fill='x', pady=(0, 5))
        
        self.match_label = tk.Label(
            inner, text="",
            font=(Theme.FONT, 8),
            bg=Theme.BG_CARD
        )
        self.match_label.pack(anchor='w')
        self.confirm_entry.bind('<KeyRelease>', self.check_password_match)
        
        self.create_footer([
            ("← Back", self.show_welcome, 'secondary'),
            ("Continue →", self.save_account, 'primary')
        ])
    
    def update_password_strength(self, event=None):
        password = self.password_entry.get()
        self.requirements_widget.update(password)
        
        strength, color, _ = calculate_password_strength(password)
        if password:
            self.strength_label.config(text=f"● {strength}", fg=color)
        else:
            self.strength_label.config(text="")
        
        self.check_password_match()
    
    def check_password_match(self, event=None):
        password = self.password_entry.get()
        confirm = self.confirm_entry.get()
        
        if not confirm:
            self.match_label.config(text="")
        elif password == confirm:
            self.match_label.config(text="✓ Passwords match", fg=Theme.SUCCESS)
        else:
            self.match_label.config(text="✗ Passwords do not match", fg=Theme.DANGER)
    
    def save_account(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        confirm = self.confirm_entry.get()
        
        if not username or len(username) < 3:
            messagebox.showerror("Validation Error", "Username must be at least 3 characters")
            return
        
        if not is_password_acceptable(password):
            messagebox.showerror(
                "Weak Password",
                "Password must meet ALL requirements:\n\n"
                "• At least 8 characters\n"
                "• Uppercase letter (A-Z)\n"
                "• Lowercase letter (a-z)\n"
                "• Number (0-9)\n"
                "• Special character (!@#$%...)"
            )
            return
        
        if password != confirm:
            messagebox.showerror("Validation Error", "Passwords do not match")
            return
        
        self.config_data['users'][username] = {
            'hash': hash_password(password),
            'created': datetime.now().isoformat(),
            'role': 'admin'
        }
        
        self.show_email_setup()
    
    # ─── SCREEN 3: EMAIL ───
    
    def show_email_setup(self):
        self.clear_window()
        self.create_header("Email Notifications", "Optional — Alerts on security events")
        StepIndicator(self.root, current=3).pack(fill='x')
        
        content = tk.Frame(self.root, bg=Theme.BG)
        content.pack(fill='both', expand=True, padx=45, pady=10)
        
        card = tk.Frame(content, bg=Theme.BG_CARD, relief='solid', bd=1)
        card.pack(fill='both', expand=True, pady=5)
        
        inner = tk.Frame(card, bg=Theme.BG_CARD)
        inner.pack(fill='both', expand=True, padx=40, pady=18)
        
        self.email_enabled = tk.BooleanVar(value=False)
        tk.Checkbutton(
            inner, text="  Enable email alerts on lockout",
            variable=self.email_enabled,
            font=(Theme.FONT, 11, 'bold'),
            bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY,
            command=self.toggle_email,
            cursor='hand2', activebackground=Theme.BG_CARD
        ).pack(anchor='w', pady=(0, 3))
        
        tk.Label(
            inner,
            text="Receive instant email notifications with intruder photo when account is locked",
            font=(Theme.FONT, 9),
            bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY
        ).pack(anchor='w', pady=(0, 15))
        
        self.email_frame = tk.Frame(inner, bg=Theme.BG_CARD)
        self.email_frame.pack(fill='x')
        
        tk.Label(
            self.email_frame, text="Sender Gmail Address",
            font=(Theme.FONT, 10, 'bold'),
            bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY
        ).pack(anchor='w', pady=(0, 3))
        
        self.email_sender = tk.Entry(
            self.email_frame,
            font=(Theme.FONT, 10),
            relief='solid', bd=1,
            state='disabled',
            disabledbackground='#F1F5F9'
        )
        self.email_sender.pack(fill='x', ipady=5, pady=(0, 10))
        
        tk.Label(
            self.email_frame, text="Gmail App Password",
            font=(Theme.FONT, 10, 'bold'),
            bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY
        ).pack(anchor='w', pady=(0, 3))
        
        self.email_password = PasswordEntry(self.email_frame)
        self.email_password.pack(fill='x', pady=(0, 5))
        self.email_password.config(state='disabled')
        
        tk.Label(
            self.email_frame,
            text="🔗 Get app password: myaccount.google.com/apppasswords",
            font=(Theme.FONT, 8, 'italic'),
            bg=Theme.BG_CARD, fg=Theme.PRIMARY_LIGHT
        ).pack(anchor='w', pady=(0, 10))
        
        tk.Label(
            self.email_frame, text="Alert Recipient Email",
            font=(Theme.FONT, 10, 'bold'),
            bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY
        ).pack(anchor='w', pady=(0, 3))
        
        self.email_receiver = tk.Entry(
            self.email_frame,
            font=(Theme.FONT, 10),
            relief='solid', bd=1,
            state='disabled',
            disabledbackground='#F1F5F9'
        )
        self.email_receiver.pack(fill='x', ipady=5)
        
        self.create_footer([
            ("← Back", self.show_account_setup, 'secondary'),
            ("Continue →", self.save_email, 'primary')
        ])
    
    def toggle_email(self):
        state = 'normal' if self.email_enabled.get() else 'disabled'
        self.email_sender.config(state=state)
        self.email_password.config(state=state)
        self.email_receiver.config(state=state)
    
    def save_email(self):
        if self.email_enabled.get():
            sender = self.email_sender.get().strip()
            password = self.email_password.get()
            receiver = self.email_receiver.get().strip()
            
            if not all([sender, password, receiver]):
                messagebox.showerror("Validation Error", "Please fill all email fields")
                return
            
            if '@' not in sender or '@' not in receiver:
                messagebox.showerror("Validation Error", "Invalid email format")
                return
            
            self.config_data['email'] = {
                'enabled': True,
                'sender': sender,
                'password': password,
                'receiver': receiver
            }
        else:
            self.config_data['email'] = {'enabled': False}
        
        self.show_security_settings()
    
    # ─── SCREEN 4: SECURITY ───
    
    def show_security_settings(self):
        self.clear_window()
        self.create_header("Security Policy", "Configure lockout behavior")
        StepIndicator(self.root, current=4).pack(fill='x')
        
        content = tk.Frame(self.root, bg=Theme.BG)
        content.pack(fill='both', expand=True, padx=45, pady=10)
        
        card = tk.Frame(content, bg=Theme.BG_CARD, relief='solid', bd=1)
        card.pack(fill='both', expand=True, pady=5)
        
        inner = tk.Frame(card, bg=Theme.BG_CARD)
        inner.pack(fill='both', expand=True, padx=40, pady=18)
        
        # Attempts
        tk.Label(
            inner, text="🎯 Failed Login Attempts",
            font=(Theme.FONT, 11, 'bold'),
            bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY
        ).pack(anchor='w')
        
        tk.Label(
            inner,
            text="Number of wrong attempts before account is temporarily locked",
            font=(Theme.FONT, 9),
            bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY
        ).pack(anchor='w', pady=(0, 8))
        
        slider_frame = tk.Frame(inner, bg=Theme.BG_CARD)
        slider_frame.pack(fill='x')
        
        self.attempts_var = tk.IntVar(value=3)
        
        self.attempts_display = tk.Label(
            slider_frame, text="3 attempts",
            font=(Theme.FONT, 14, 'bold'),
            bg=Theme.PRIMARY_LIGHTER, fg=Theme.PRIMARY,
            width=12
        )
        self.attempts_display.pack(side='right', padx=(15, 0), ipady=4)
        
        tk.Scale(
            slider_frame, from_=1, to=10, orient='horizontal',
            variable=self.attempts_var,
            bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY,
            troughcolor=Theme.PRIMARY_LIGHTER,
            activebackground=Theme.PRIMARY_LIGHT,
            highlightthickness=0, showvalue=False,
            command=self.update_attempts_display
        ).pack(side='left', fill='x', expand=True)
        
        # Info
        info_frame = tk.Frame(inner, bg=Theme.WARNING_LIGHT)
        info_frame.pack(fill='x', pady=(8, 10))
        
        self.attempts_info = tk.Label(
            info_frame,
            text="ℹ️ After 3 wrong attempts → 15s lockout (doubles each cycle: 15s → 30s → 60s ...)",
            font=(Theme.FONT, 9),
            bg=Theme.WARNING_LIGHT, fg='#92400E', anchor='w',
            wraplength=650
        )
        self.attempts_info.pack(fill='x', padx=10, pady=6)
        
        # Progressive explainer
        explainer = tk.Frame(inner, bg=Theme.PRIMARY_LIGHTER)
        explainer.pack(fill='x', pady=(0, 12))
        
        tk.Label(
            explainer,
            text="⏱️ Progressive Lockout Timer:\n"
                 "Lockout #1: 15s  →  #2: 30s  →  #3: 60s  →  #4: 2min  →  #5: 4min  →  #6: 8min  →  Max: 30min\n"
                 "Camera capture + email alert triggers on EACH lockout cycle",
            font=(Theme.FONT, 9),
            bg=Theme.PRIMARY_LIGHTER, fg=Theme.PRIMARY,
            justify='left'
        ).pack(padx=10, pady=8, anchor='w')
        
        tk.Frame(inner, bg=Theme.BORDER, height=1).pack(fill='x', pady=8)
        
        # Response actions
        tk.Label(
            inner, text="🚨 Security Response Actions",
            font=(Theme.FONT, 11, 'bold'),
            bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY
        ).pack(anchor='w', pady=(0, 5))
        
        self.capture_on_lockout = tk.BooleanVar(value=True)
        cap_check = tk.Checkbutton(
            inner, text="  Capture intruder photo on each lockout",
            variable=self.capture_on_lockout,
            font=(Theme.FONT, 10),
            bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY,
            cursor='hand2', activebackground=Theme.BG_CARD
        )
        cap_check.pack(anchor='w', pady=2)
        
        if not OPENCV_AVAILABLE:
            self.capture_on_lockout.set(False)
            cap_check.config(state='disabled')
        
        self.email_on_lockout = tk.BooleanVar(value=True)
        email_check = tk.Checkbutton(
            inner, text="  Send email alert on each lockout",
            variable=self.email_on_lockout,
            font=(Theme.FONT, 10),
            bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY,
            cursor='hand2', activebackground=Theme.BG_CARD
        )
        email_check.pack(anchor='w', pady=2)
        
        if not self.config_data['email'].get('enabled'):
            self.email_on_lockout.set(False)
            email_check.config(state='disabled')
        
        self.autostart_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            inner, text="  Start SENTINEL automatically when Windows boots",
            variable=self.autostart_var,
            font=(Theme.FONT, 10),
            bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY,
            cursor='hand2', activebackground=Theme.BG_CARD
        ).pack(anchor='w', pady=2)
        
        self.create_footer([
            ("← Back", self.show_email_setup, 'secondary'),
            ("Install SENTINEL ✓", self.complete_installation, 'success')
        ])
    
    def update_attempts_display(self, value):
        n = int(value)
        self.attempts_display.config(text=f"{n} attempt{'s' if n != 1 else ''}")
        
        if n == 1:
            msg = f"⚠️ Very Strict: 1 wrong attempt → 15s lockout (then 30s, 60s, etc.)"
        elif n <= 3:
            msg = f"ℹ️ Standard: After {n} wrong attempts → 15s lockout (doubles each cycle)"
        elif n <= 5:
            msg = f"✓ Balanced: {n} attempts allowed before progressive lockout"
        else:
            msg = f"⚠️ Lenient: {n} attempts (consider lower for stronger security)"
        
        self.attempts_info.config(text=msg)
    
    def complete_installation(self):
        try:
            self.config_data['max_attempts'] = self.attempts_var.get()
            self.config_data['capture_on_lockout'] = self.capture_on_lockout.get()
            self.config_data['email_on_lockout'] = self.email_on_lockout.get()
            self.config_data['autostart'] = self.autostart_var.get()
            self.config_data['installed_at'] = datetime.now().isoformat()
            self.config_data['version'] = APP_VERSION
            
            if not self.config_mgr.save(self.config_data):
                messagebox.showerror("Error", "Failed to save configuration")
                return
            
            if self.config_data['autostart']:
                enable_autostart()
            
            self.config_mgr.log(f"{APP_NAME} v{APP_VERSION} installed", "INFO")
            self.config_mgr.log(f"Max attempts: {self.config_data['max_attempts']}", "INFO")
            
            self.show_completion()
        except Exception as e:
            messagebox.showerror("Installation Error", str(e))
    
    def show_completion(self):
        self.clear_window()
        
        header = tk.Frame(self.root, bg=Theme.SUCCESS, height=120)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        tk.Frame(header, bg='#047857', height=4).pack(fill='x', side='bottom')
        
        sf = tk.Frame(header, bg=Theme.SUCCESS)
        sf.place(relx=0.5, rely=0.5, anchor='center')
        
        tk.Label(sf, text="✓", font=(Theme.FONT, 36, 'bold'),
                bg=Theme.SUCCESS, fg=Theme.TEXT_WHITE).pack()
        tk.Label(sf, text="Installation Successful!",
                font=(Theme.FONT, 16, 'bold'),
                bg=Theme.SUCCESS, fg=Theme.TEXT_WHITE).pack()
        
        content = tk.Frame(self.root, bg=Theme.BG)
        content.pack(fill='both', expand=True, padx=45, pady=20)
        
        card = tk.Frame(content, bg=Theme.BG_CARD, relief='solid', bd=1)
        card.pack(fill='both', expand=True)
        
        inner = tk.Frame(card, bg=Theme.BG_CARD)
        inner.pack(fill='both', expand=True, padx=40, pady=20)
        
        tk.Label(inner, text="✨ SENTINEL is now protecting your system",
                font=(Theme.FONT, 13, 'bold'),
                bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(anchor='w', pady=(0, 12))
        
        username = list(self.config_data['users'].keys())[0]
        items = [
            ("👤", "Administrator", username),
            ("🎯", "Max Failed Attempts", str(self.config_data['max_attempts'])),
            ("⏱️", "Initial Lockout", f"{INITIAL_LOCKOUT_SECONDS}s (progressive)"),
            ("📸", "Camera Capture", "Enabled ✓" if self.config_data['capture_on_lockout'] else "Disabled"),
            ("📧", "Email Alerts", "Enabled ✓" if self.config_data['email'].get('enabled') else "Disabled"),
            ("🚀", "Auto-Start", "Enabled ✓" if self.config_data['autostart'] else "Disabled"),
        ]
        
        for icon, label, value in items:
            row = tk.Frame(inner, bg=Theme.BG_CARD)
            row.pack(fill='x', pady=3)
            
            tk.Label(row, text=icon, font=(Theme.FONT, 11),
                    bg=Theme.BG_CARD, width=3).pack(side='left')
            
            tk.Label(row, text=label,
                    font=(Theme.FONT, 10),
                    bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY,
                    width=22, anchor='w').pack(side='left')
            
            tk.Label(row, text=value,
                    font=(Theme.FONT, 10, 'bold'),
                    bg=Theme.BG_CARD, fg=Theme.SUCCESS,
                    anchor='w').pack(side='left')
        
        info_box = tk.Frame(inner, bg=Theme.PRIMARY_LIGHTER)
        info_box.pack(fill='x', pady=(15, 0))
        
        tk.Label(info_box,
                text="📊 Open Dashboard to view statistics, captures, logs, and modify settings.\n"
                     "🔒 Test Login lets you verify the protection system before reboot.",
                font=(Theme.FONT, 9),
                bg=Theme.PRIMARY_LIGHTER, fg=Theme.PRIMARY,
                justify='left').pack(padx=15, pady=12, anchor='w')
        
        self.create_footer([
            ("Test Login", self.launch_login, 'secondary'),
            ("Open Dashboard →", self.launch_dashboard, 'success'),
        ])
    
    def launch_login(self):
        self.root.destroy()
        LoginApp().run()
    
    def launch_dashboard(self):
        self.root.destroy()
        Dashboard().run()
    
    def run(self):
        self.root.mainloop()

# ════════════════════════════════════════════════════════════════════
#  DASHBOARD — MAIN CONTROL PANEL
# ════════════════════════════════════════════════════════════════════

class Dashboard:
    """Main dashboard with sidebar navigation"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"{APP_NAME} — Dashboard")
        self.root.geometry(f"{DASHBOARD_WIDTH}x{DASHBOARD_HEIGHT}")
        self.root.configure(bg=Theme.BG)
        self.root.minsize(900, 600)
        
        x = (self.root.winfo_screenwidth() - DASHBOARD_WIDTH) // 2
        y = (self.root.winfo_screenheight() - DASHBOARD_HEIGHT) // 2
        self.root.geometry(f"{DASHBOARD_WIDTH}x{DASHBOARD_HEIGHT}+{x}+{y}")
        
        self.config_mgr = ConfigManager()
        self.config = self.config_mgr.load() or {}
        
        self.sidebar_buttons = {}
        self.current_view = None
        
        self._build_layout()
        self.show_overview()
    
    def _build_layout(self):
        # Main container
        main = tk.Frame(self.root, bg=Theme.BG)
        main.pack(fill='both', expand=True)
        
        # Sidebar
        sidebar = tk.Frame(main, bg=Theme.SIDEBAR_BG, width=240)
        sidebar.pack(side='left', fill='y')
        sidebar.pack_propagate(False)
        
        # Brand at top
        brand_frame = tk.Frame(sidebar, bg=Theme.SIDEBAR_BG, height=100)
        brand_frame.pack(fill='x')
        brand_frame.pack_propagate(False)
        
        # Accent line
        tk.Frame(brand_frame, bg=Theme.PRIMARY_LIGHT, height=3).pack(fill='x', side='bottom')
        
        brand_inner = tk.Frame(brand_frame, bg=Theme.SIDEBAR_BG)
        brand_inner.place(relx=0.5, rely=0.5, anchor='center')
        
        brand_row = tk.Frame(brand_inner, bg=Theme.SIDEBAR_BG)
        brand_row.pack()
        
        tk.Label(brand_row, text="🛡️", font=(Theme.FONT, 20),
                bg=Theme.SIDEBAR_BG).pack(side='left', padx=(0, 8))
        
        tk.Label(brand_row, text=APP_NAME,
                font=(Theme.FONT, 18, 'bold'),
                bg=Theme.SIDEBAR_BG, fg=Theme.TEXT_WHITE).pack(side='left')
        
        tk.Label(brand_inner, text=f"v{APP_VERSION}",
                font=(Theme.FONT, 8),
                bg=Theme.SIDEBAR_BG, fg=Theme.TEXT_MUTED).pack(pady=(2, 0))
        
        # Navigation items
        nav_items = [
            ("📊", "Overview", self.show_overview),
            ("📸", "Captures", self.show_captures),
            ("📋", "Activity Log", self.show_logs),
            ("⚙️", "Settings", self.show_settings),
            ("ℹ️", "About", self.show_about),
        ]
        
        nav_frame = tk.Frame(sidebar, bg=Theme.SIDEBAR_BG)
        nav_frame.pack(fill='x', pady=10)
        
        for icon, text, cmd in nav_items:
            btn = SidebarButton(nav_frame, icon, text, cmd)
            btn.pack(fill='x')
            self.sidebar_buttons[text] = btn
        
        # User info at bottom
        user_frame = tk.Frame(sidebar, bg=Theme.BG_DARKER, height=70)
        user_frame.pack(side='bottom', fill='x')
        user_frame.pack_propagate(False)
        
        if self.config.get('users'):
            username = list(self.config['users'].keys())[0]
            
            tk.Label(user_frame, text=f"👤 {username}",
                    font=(Theme.FONT, 10, 'bold'),
                    bg=Theme.BG_DARKER, fg=Theme.TEXT_WHITE).pack(pady=(15, 2), padx=20, anchor='w')
            
            tk.Label(user_frame, text="Administrator",
                    font=(Theme.FONT, 8),
                    bg=Theme.BG_DARKER, fg=Theme.TEXT_MUTED).pack(padx=20, anchor='w')
        
        # Content area
        self.content_frame = tk.Frame(main, bg=Theme.BG)
        self.content_frame.pack(side='left', fill='both', expand=True)
    
    def _set_active(self, name):
        for btn_name, btn in self.sidebar_buttons.items():
            btn.set_active(btn_name == name)
    
    def _clear_content(self):
        for w in self.content_frame.winfo_children():
            w.destroy()
    
    def _create_page_header(self, title, subtitle=None, action_button=None):
        """Create consistent page header"""
        header = tk.Frame(self.content_frame, bg=Theme.BG_CARD, height=80)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        tk.Frame(header, bg=Theme.BORDER, height=1).pack(side='bottom', fill='x')
        
        inner = tk.Frame(header, bg=Theme.BG_CARD)
        inner.pack(fill='both', expand=True, padx=30, pady=15)
        
        left = tk.Frame(inner, bg=Theme.BG_CARD)
        left.pack(side='left', fill='y')
        
        tk.Label(left, text=title,
                font=(Theme.FONT, 18, 'bold'),
                bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(anchor='w')
        
        if subtitle:
            tk.Label(left, text=subtitle,
                    font=(Theme.FONT, 10),
                    bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY).pack(anchor='w')
        
        if action_button:
            text, command, style = action_button
            right = tk.Frame(inner, bg=Theme.BG_CARD)
            right.pack(side='right', fill='y')
            ModernButton(right, text, command, style).pack(pady=8)
    
    # ─── OVERVIEW PAGE ───
    
    def show_overview(self):
        self._clear_content()
        self._set_active("Overview")
        
        self._create_page_header(
            "Overview",
            "Real-time system status and statistics"
        )
        
        # Scrollable content
        canvas = tk.Canvas(self.content_frame, bg=Theme.BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(self.content_frame, orient='vertical', command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        scroll_frame = tk.Frame(canvas, bg=Theme.BG)
        canvas.create_window(0, 0, window=scroll_frame, anchor='nw')
        
        # Padding
        content = tk.Frame(scroll_frame, bg=Theme.BG)
        content.pack(fill='both', expand=True, padx=30, pady=20)
        
        # Stats cards (4 in row)
        stats = self.config_mgr.load_stats()
        
        tk.Label(content, text="Live Statistics",
                font=(Theme.FONT, 13, 'bold'),
                bg=Theme.BG, fg=Theme.TEXT_PRIMARY).pack(anchor='w', pady=(0, 10))
        
        cards_frame = tk.Frame(content, bg=Theme.BG)
        cards_frame.pack(fill='x', pady=(0, 20))
        
        card_data = [
            ("✓", stats['successful_logins'], "Successful Logins", Theme.SUCCESS),
            ("✗", stats['failed_attempts'], "Failed Attempts", Theme.WARNING),
            ("🔒", stats['total_lockouts'], "Total Lockouts", Theme.DANGER),
            ("📸", stats['photos_captured'], "Photos Captured", Theme.PRIMARY_LIGHT),
        ]
        
        for i, (icon, value, label, color) in enumerate(card_data):
            card = StatCard(cards_frame, icon, value, label, color)
            card.grid(row=0, column=i, padx=5, sticky='nsew')
            cards_frame.columnconfigure(i, weight=1)
        
        # System Status
        tk.Label(content, text="System Status",
                font=(Theme.FONT, 13, 'bold'),
                bg=Theme.BG, fg=Theme.TEXT_PRIMARY).pack(anchor='w', pady=(10, 10))
        
        status_card = tk.Frame(content, bg=Theme.BG_CARD, relief='solid', bd=1)
        status_card.pack(fill='x', pady=(0, 15))
        
        tk.Frame(status_card, bg=Theme.SUCCESS, height=4).pack(fill='x')
        
        status_inner = tk.Frame(status_card, bg=Theme.BG_CARD)
        status_inner.pack(fill='x', padx=25, pady=15)
        
        status_items = [
            ("🛡️ Protection Status", "Active" if self.config else "Not Configured",
             Theme.SUCCESS if self.config else Theme.DANGER),
            ("📷 Camera Module", "Ready" if OPENCV_AVAILABLE else "Unavailable",
             Theme.SUCCESS if OPENCV_AVAILABLE else Theme.WARNING),
            ("📧 Email Alerts", "Enabled" if self.config.get('email', {}).get('enabled') else "Disabled",
             Theme.SUCCESS if self.config.get('email', {}).get('enabled') else Theme.TEXT_MUTED),
            ("🚀 Auto-Start", "Enabled" if check_autostart_enabled() else "Disabled",
             Theme.SUCCESS if check_autostart_enabled() else Theme.TEXT_MUTED),
            ("🎯 Max Attempts", str(self.config.get('max_attempts', 3)), Theme.PRIMARY_LIGHT),
        ]
        
        for label, value, color in status_items:
            row = tk.Frame(status_inner, bg=Theme.BG_CARD)
            row.pack(fill='x', pady=4)
            
            tk.Label(row, text=label,
                    font=(Theme.FONT, 10),
                    bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY,
                    width=22, anchor='w').pack(side='left')
            
            tk.Label(row, text="● " + value,
                    font=(Theme.FONT, 10, 'bold'),
                    bg=Theme.BG_CARD, fg=color,
                    anchor='w').pack(side='left')
        
        # Recent Activity preview
        tk.Label(content, text="Recent Activity",
                font=(Theme.FONT, 13, 'bold'),
                bg=Theme.BG, fg=Theme.TEXT_PRIMARY).pack(anchor='w', pady=(10, 10))
        
        activity_card = tk.Frame(content, bg=Theme.BG_CARD, relief='solid', bd=1)
        activity_card.pack(fill='x', pady=(0, 15))
        
        activity_inner = tk.Frame(activity_card, bg=Theme.BG_CARD)
        activity_inner.pack(fill='x', padx=25, pady=15)
        
        logs = self.config_mgr.load_logs(limit=8)
        
        if logs:
            for log in reversed(logs[-8:]):
                log_line = log.strip()
                if not log_line:
                    continue
                
                # Parse level for color
                color = Theme.TEXT_SECONDARY
                if '[CRITICAL]' in log_line:
                    color = Theme.DANGER
                elif '[WARNING]' in log_line:
                    color = Theme.WARNING
                elif '✓' in log_line:
                    color = Theme.SUCCESS
                
                tk.Label(activity_inner, text=log_line,
                        font=(Theme.FONT_MONO, 8),
                        bg=Theme.BG_CARD, fg=color,
                        anchor='w', justify='left').pack(fill='x', pady=1)
        else:
            tk.Label(activity_inner, text="No activity yet",
                    font=(Theme.FONT, 10, 'italic'),
                    bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED).pack(pady=10)
        
        # Quick actions
        tk.Label(content, text="Quick Actions",
                font=(Theme.FONT, 13, 'bold'),
                bg=Theme.BG, fg=Theme.TEXT_PRIMARY).pack(anchor='w', pady=(10, 10))
        
        actions_frame = tk.Frame(content, bg=Theme.BG)
        actions_frame.pack(fill='x')
        
        ModernButton(actions_frame, "🔒 Test Login Screen",
                    self._open_login, 'primary', width=22).pack(side='left', padx=(0, 8))
        
        ModernButton(actions_frame, "📂 Open Data Folder",
                    self._open_folder, 'secondary', width=20).pack(side='left', padx=4)
        
        ModernButton(actions_frame, "🗑️ Uninstall",
                    self._uninstall, 'danger', width=15).pack(side='right')
        
        # Update scroll region
        scroll_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox('all'))
        
        # Mouse wheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    # ─── CAPTURES PAGE ───
    
    def show_captures(self):
        self._clear_content()
        self._set_active("Captures")
        
        self._create_page_header(
            "Intruder Captures",
            "Photos captured during security incidents",
            ("🔄 Refresh", self.show_captures, 'secondary')
        )
        
        # Content area
        content = tk.Frame(self.content_frame, bg=Theme.BG)
        content.pack(fill='both', expand=True, padx=30, pady=20)
        
        captures = self.config_mgr.get_captures()
        
        if not captures:
            # Empty state
            empty = tk.Frame(content, bg=Theme.BG_CARD, relief='solid', bd=1)
            empty.pack(fill='both', expand=True)
            
            center = tk.Frame(empty, bg=Theme.BG_CARD)
            center.place(relx=0.5, rely=0.5, anchor='center')
            
            tk.Label(center, text="📸",
                    font=(Theme.FONT, 48),
                    bg=Theme.BG_CARD).pack()
            
            tk.Label(center, text="No Captures Yet",
                    font=(Theme.FONT, 14, 'bold'),
                    bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(pady=(10, 5))
            
            tk.Label(center, text="Intruder photos will appear here when account lockouts occur",
                    font=(Theme.FONT, 10),
                    bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY).pack()
        else:
            # Stats bar
            stats_bar = tk.Frame(content, bg=Theme.PRIMARY_LIGHTER)
            stats_bar.pack(fill='x', pady=(0, 15))
            
            tk.Label(stats_bar,
                    text=f"📸 Total Captures: {len(captures)}  •  Latest: {datetime.fromtimestamp(os.path.getmtime(captures[0])).strftime('%Y-%m-%d %H:%M')}",
                    font=(Theme.FONT, 10, 'bold'),
                    bg=Theme.PRIMARY_LIGHTER, fg=Theme.PRIMARY).pack(padx=15, pady=10, anchor='w')
            
            # Scrollable list
            list_container = tk.Frame(content, bg=Theme.BG_CARD, relief='solid', bd=1)
            list_container.pack(fill='both', expand=True)
            
            canvas = tk.Canvas(list_container, bg=Theme.BG_CARD, highlightthickness=0)
            scrollbar = tk.Scrollbar(list_container, command=canvas.yview)
            
            scroll_frame = tk.Frame(canvas, bg=Theme.BG_CARD)
            canvas.create_window(0, 0, window=scroll_frame, anchor='nw')
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side='left', fill='both', expand=True)
            scrollbar.pack(side='right', fill='y')
            
            # List captures
            for i, path in enumerate(captures):
                mtime = os.path.getmtime(path)
                date_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
                size_kb = os.path.getsize(path) / 1024
                filename = os.path.basename(path)
                
                row = tk.Frame(scroll_frame, bg=Theme.BG_CARD)
                row.pack(fill='x', padx=15, pady=8)
                
                if i > 0:
                    tk.Frame(scroll_frame, bg=Theme.BORDER, height=1).pack(fill='x', padx=15)
                    row.pack_forget()
                    row.pack(fill='x', padx=15, pady=8)
                
                # Icon
                icon_frame = tk.Frame(row, bg=Theme.DANGER_LIGHT, width=60, height=60)
                icon_frame.pack(side='left', padx=(0, 15))
                icon_frame.pack_propagate(False)
                
                tk.Label(icon_frame, text="📸",
                        font=(Theme.FONT, 24),
                        bg=Theme.DANGER_LIGHT).place(relx=0.5, rely=0.5, anchor='center')
                
                # Info
                info = tk.Frame(row, bg=Theme.BG_CARD)
                info.pack(side='left', fill='x', expand=True)
                
                tk.Label(info, text=filename,
                        font=(Theme.FONT, 10, 'bold'),
                        bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY,
                        anchor='w').pack(fill='x')
                
                tk.Label(info, text=f"📅 {date_str}  •  💾 {size_kb:.1f} KB",
                        font=(Theme.FONT, 9),
                        bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY,
                        anchor='w').pack(fill='x', pady=(2, 0))
                
                # Actions
                actions = tk.Frame(row, bg=Theme.BG_CARD)
                actions.pack(side='right')
                
                ModernButton(actions, "View", lambda p=path: self._view_image(p),
                            'primary', width=8).pack(side='left', padx=2)
                
                ModernButton(actions, "Delete", lambda p=path: self._delete_capture(p),
                            'danger', width=8).pack(side='left', padx=2)
            
            scroll_frame.update_idletasks()
            canvas.config(scrollregion=canvas.bbox('all'))
            
            def _on_mousewheel(event):
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def _view_image(self, path):
        """Open image with default Windows viewer"""
        try:
            os.startfile(path)
        except Exception as e:
            messagebox.showerror("Error", f"Cannot open image: {e}")
    
    def _delete_capture(self, path):
        """Delete a captured image"""
        if messagebox.askyesno("Delete Capture", 
                               f"Delete this capture permanently?\n\n{os.path.basename(path)}"):
            try:
                os.remove(path)
                self.show_captures()
            except Exception as e:
                messagebox.showerror("Error", f"Cannot delete: {e}")
    
    # ─── LOGS PAGE ───
    
    def show_logs(self):
        self._clear_content()
        self._set_active("Activity Log")
        
        self._create_page_header(
            "Activity Log",
            "Security event audit trail",
            ("🔄 Refresh", self.show_logs, 'secondary')
        )
        
        # Content
        content = tk.Frame(self.content_frame, bg=Theme.BG)
        content.pack(fill='both', expand=True, padx=30, pady=20)
        
        # Filter buttons
        filter_frame = tk.Frame(content, bg=Theme.BG)
        filter_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(filter_frame, text="Filter:",
                font=(Theme.FONT, 10, 'bold'),
                bg=Theme.BG, fg=Theme.TEXT_PRIMARY).pack(side='left', padx=(0, 10))
        
        self.log_filter = tk.StringVar(value="ALL")
        
        filters = [("ALL", "All"), ("INFO", "Info"), ("WARNING", "Warning"), ("CRITICAL", "Critical")]
        for value, label in filters:
            btn = tk.Radiobutton(filter_frame, text=label, value=value,
                                variable=self.log_filter,
                                font=(Theme.FONT, 9),
                                bg=Theme.BG, fg=Theme.TEXT_PRIMARY,
                                command=self._refresh_logs,
                                cursor='hand2')
            btn.pack(side='left', padx=4)
        
        # Log display
        log_container = tk.Frame(content, bg=Theme.BG_DARKER, relief='solid', bd=1)
        log_container.pack(fill='both', expand=True)
        
        # Header bar
        log_header = tk.Frame(log_container, bg='#1E293B', height=35)
        log_header.pack(fill='x')
        log_header.pack_propagate(False)
        
        tk.Label(log_header, text="🖥️ SENTINEL Security Log",
                font=(Theme.FONT_MONO, 9, 'bold'),
                bg='#1E293B', fg='#10B981').pack(side='left', padx=15, pady=8)
        
        tk.Label(log_header, text=f"Path: {self.config_mgr.log_file}",
                font=(Theme.FONT_MONO, 8),
                bg='#1E293B', fg=Theme.TEXT_MUTED).pack(side='right', padx=15, pady=8)
        
        # Text widget for logs
        log_frame = tk.Frame(log_container, bg=Theme.BG_DARKER)
        log_frame.pack(fill='both', expand=True)
        
        self.log_text = tk.Text(
            log_frame,
            font=(Theme.FONT_MONO, 9),
            bg=Theme.BG_DARKER,
            fg='#10B981',
            relief='flat',
            bd=0,
            padx=15,
            pady=10,
            wrap='word'
        )
        
        log_scroll = tk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scroll.set)
        
        self.log_text.pack(side='left', fill='both', expand=True)
        log_scroll.pack(side='right', fill='y')
        
        # Tag colors for log levels
        self.log_text.tag_config('CRITICAL', foreground='#EF4444')
        self.log_text.tag_config('WARNING', foreground='#F59E0B')
        self.log_text.tag_config('INFO', foreground='#10B981')
        self.log_text.tag_config('SUCCESS', foreground='#34D399')
        
        self._refresh_logs()
    
    def _refresh_logs(self):
        """Refresh and filter logs"""
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        
        logs = self.config_mgr.load_logs(limit=500)
        filter_level = self.log_filter.get()
        
        for log in logs:
            log = log.strip()
            if not log:
                continue
            
            # Apply filter
            if filter_level != "ALL" and f"[{filter_level}]" not in log:
                continue
            
            # Determine tag
            tag = None
            if '[CRITICAL]' in log:
                tag = 'CRITICAL'
            elif '[WARNING]' in log:
                tag = 'WARNING'
            elif '[INFO]' in log:
                tag = 'INFO'
            
            if tag:
                self.log_text.insert(tk.END, log + '\n', tag)
            else:
                self.log_text.insert(tk.END, log + '\n')
        
        self.log_text.config(state='disabled')
        self.log_text.see(tk.END)
    
    # ─── SETTINGS PAGE ───
    
    def show_settings(self):
        self._clear_content()
        self._set_active("Settings")
        
        self._create_page_header(
            "Settings",
            "Modify SENTINEL configuration"
        )
        
        # Scrollable content
        canvas = tk.Canvas(self.content_frame, bg=Theme.BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(self.content_frame, command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        scroll_frame = tk.Frame(canvas, bg=Theme.BG)
        canvas.create_window(0, 0, window=scroll_frame, anchor='nw')
        
        content = tk.Frame(scroll_frame, bg=Theme.BG)
        content.pack(fill='both', expand=True, padx=30, pady=20)
        
        # Reload config
        self.config = self.config_mgr.load() or {}
        
        # === Security Settings ===
        sec_card = tk.Frame(content, bg=Theme.BG_CARD, relief='solid', bd=1)
        sec_card.pack(fill='x', pady=(0, 15))
        
        tk.Frame(sec_card, bg=Theme.PRIMARY_LIGHT, height=4).pack(fill='x')
        
        sec_inner = tk.Frame(sec_card, bg=Theme.BG_CARD)
        sec_inner.pack(fill='x', padx=25, pady=18)
        
        tk.Label(sec_inner, text="🎯 Security Policy",
                font=(Theme.FONT, 13, 'bold'),
                bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(anchor='w', pady=(0, 12))
        
        # Max attempts
        att_frame = tk.Frame(sec_inner, bg=Theme.BG_CARD)
        att_frame.pack(fill='x', pady=5)
        
        tk.Label(att_frame, text="Max Failed Attempts:",
                font=(Theme.FONT, 10),
                bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY,
                width=22, anchor='w').pack(side='left')
        
        self.set_attempts = tk.IntVar(value=self.config.get('max_attempts', 3))
        
        self.set_attempts_display = tk.Label(
            att_frame, text=f"{self.set_attempts.get()} attempts",
            font=(Theme.FONT, 11, 'bold'),
            bg=Theme.PRIMARY_LIGHTER, fg=Theme.PRIMARY,
            width=12
        )
        self.set_attempts_display.pack(side='right', padx=(15, 0), ipady=3)
        
        tk.Scale(att_frame, from_=1, to=10, orient='horizontal',
                variable=self.set_attempts,
                bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY,
                troughcolor=Theme.PRIMARY_LIGHTER,
                activebackground=Theme.PRIMARY_LIGHT,
                highlightthickness=0, showvalue=False,
                command=lambda v: self.set_attempts_display.config(
                    text=f"{int(v)} attempt{'s' if int(v) != 1 else ''}"
                )).pack(side='left', fill='x', expand=True, padx=10)
        
        # Capture on lockout
        self.set_capture = tk.BooleanVar(value=self.config.get('capture_on_lockout', True))
        cap = tk.Checkbutton(sec_inner, text="  Capture intruder photo on lockout",
                            variable=self.set_capture,
                            font=(Theme.FONT, 10),
                            bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY,
                            activebackground=Theme.BG_CARD, cursor='hand2')
        cap.pack(anchor='w', pady=5)
        if not OPENCV_AVAILABLE:
            cap.config(state='disabled')
        
        # Email on lockout
        self.set_email_lockout = tk.BooleanVar(value=self.config.get('email_on_lockout', True))
        em = tk.Checkbutton(sec_inner, text="  Send email on lockout",
                           variable=self.set_email_lockout,
                           font=(Theme.FONT, 10),
                           bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY,
                           activebackground=Theme.BG_CARD, cursor='hand2')
        em.pack(anchor='w', pady=5)
        if not self.config.get('email', {}).get('enabled'):
            em.config(state='disabled')
        
        # Auto-start
        self.set_autostart = tk.BooleanVar(value=check_autostart_enabled())
        tk.Checkbutton(sec_inner, text="  Auto-start on Windows boot",
                      variable=self.set_autostart,
                      font=(Theme.FONT, 10),
                      bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY,
                      activebackground=Theme.BG_CARD, cursor='hand2').pack(anchor='w', pady=5)
        
        # Save button
        save_frame = tk.Frame(sec_inner, bg=Theme.BG_CARD)
        save_frame.pack(fill='x', pady=(15, 0))
        
        ModernButton(save_frame, "💾 Save Changes",
                    self._save_settings, 'success', width=18).pack(side='right')
        
        # === Account Settings ===
        acc_card = tk.Frame(content, bg=Theme.BG_CARD, relief='solid', bd=1)
        acc_card.pack(fill='x', pady=(0, 15))
        
        tk.Frame(acc_card, bg=Theme.ACCENT, height=4).pack(fill='x')
        
        acc_inner = tk.Frame(acc_card, bg=Theme.BG_CARD)
        acc_inner.pack(fill='x', padx=25, pady=18)
        
        tk.Label(acc_inner, text="👤 Account",
                font=(Theme.FONT, 13, 'bold'),
                bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(anchor='w', pady=(0, 12))
        
        if self.config.get('users'):
            for username, user_data in self.config['users'].items():
                user_row = tk.Frame(acc_inner, bg=Theme.BG_CARD)
                user_row.pack(fill='x', pady=4)
                
                tk.Label(user_row, text=f"👤 {username}",
                        font=(Theme.FONT, 11, 'bold'),
                        bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY,
                        anchor='w').pack(side='left')
                
                created = user_data.get('created', 'Unknown')
                if isinstance(created, str) and 'T' in created:
                    created = created.split('T')[0]
                
                tk.Label(user_row, text=f"Created: {created}",
                        font=(Theme.FONT, 9),
                        bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY,
                        anchor='w').pack(side='left', padx=15)
                
                tk.Label(user_row, text=user_data.get('role', 'user').title(),
                        font=(Theme.FONT, 9, 'bold'),
                        bg=Theme.PRIMARY_LIGHTER, fg=Theme.PRIMARY,
                        padx=8, pady=2).pack(side='right')
        
        ModernButton(acc_inner, "🔑 Change Password",
                    self._change_password, 'primary', width=18).pack(anchor='w', pady=(10, 0))
        
        # === Danger Zone ===
        danger_card = tk.Frame(content, bg=Theme.BG_CARD, relief='solid', bd=1)
        danger_card.pack(fill='x')
        
        tk.Frame(danger_card, bg=Theme.DANGER, height=4).pack(fill='x')
        
        danger_inner = tk.Frame(danger_card, bg=Theme.BG_CARD)
        danger_inner.pack(fill='x', padx=25, pady=18)
        
        tk.Label(danger_inner, text="⚠️ Danger Zone",
                font=(Theme.FONT, 13, 'bold'),
                bg=Theme.BG_CARD, fg=Theme.DANGER).pack(anchor='w', pady=(0, 12))
        
        tk.Label(danger_inner, text="These actions are permanent and cannot be undone",
                font=(Theme.FONT, 9),
                bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY).pack(anchor='w', pady=(0, 12))
        
        danger_btns = tk.Frame(danger_inner, bg=Theme.BG_CARD)
        danger_btns.pack(fill='x')
        
        ModernButton(danger_btns, "🗑️ Clear All Logs",
                    self._clear_logs, 'danger', width=15).pack(side='left', padx=(0, 5))
        
        ModernButton(danger_btns, "🗑️ Clear Captures",
                    self._clear_captures, 'danger', width=15).pack(side='left', padx=5)
        
        ModernButton(danger_btns, "❌ Uninstall SENTINEL",
                    self._uninstall, 'danger', width=20).pack(side='right')
        
        scroll_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox('all'))
        
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def _save_settings(self):
        """Save settings changes"""
        try:
            self.config['max_attempts'] = self.set_attempts.get()
            self.config['capture_on_lockout'] = self.set_capture.get()
            self.config['email_on_lockout'] = self.set_email_lockout.get()
            
            if self.set_autostart.get():
                enable_autostart()
            else:
                disable_autostart()
            
            if self.config_mgr.save(self.config):
                self.config_mgr.log("Settings updated", "INFO")
                messagebox.showinfo("Saved", "Settings saved successfully ✓")
            else:
                messagebox.showerror("Error", "Failed to save settings")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def _change_password(self):
        """Show change password dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Change Password")
        dialog.geometry("450x450")
        dialog.configure(bg=Theme.BG_CARD)
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        x = self.root.winfo_x() + (self.root.winfo_width() - 450) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - 450) // 2
        dialog.geometry(f"450x450+{x}+{y}")
        
        # Header
        hdr = tk.Frame(dialog, bg=Theme.PRIMARY_DARK, height=60)
        hdr.pack(fill='x')
        hdr.pack_propagate(False)
        
        tk.Label(hdr, text="🔑 Change Password",
                font=(Theme.FONT, 14, 'bold'),
                bg=Theme.PRIMARY_DARK, fg=Theme.TEXT_WHITE).pack(pady=18)
        
        inner = tk.Frame(dialog, bg=Theme.BG_CARD)
        inner.pack(fill='both', expand=True, padx=30, pady=20)
        
        # Current password
        tk.Label(inner, text="Current Password",
                font=(Theme.FONT, 10, 'bold'),
                bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(anchor='w', pady=(0, 3))
        
        current_entry = PasswordEntry(inner)
        current_entry.pack(fill='x', pady=(0, 12))
        
        # New password
        tk.Label(inner, text="New Password",
                font=(Theme.FONT, 10, 'bold'),
                bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(anchor='w', pady=(0, 3))
        
        new_entry = PasswordEntry(inner)
        new_entry.pack(fill='x', pady=(0, 8))
        
        req_widget = PasswordRequirements(inner)
        req_widget.pack(fill='x', pady=(0, 12))
        
        new_entry.bind('<KeyRelease>', lambda e: req_widget.update(new_entry.get()))
        
        # Confirm
        tk.Label(inner, text="Confirm New Password",
                font=(Theme.FONT, 10, 'bold'),
                bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(anchor='w', pady=(0, 3))
        
        confirm_entry = PasswordEntry(inner)
        confirm_entry.pack(fill='x', pady=(0, 15))
        
        def save_password():
            current = current_entry.get()
            new_pwd = new_entry.get()
            confirm = confirm_entry.get()
            
            users = self.config.get('users', {})
            if not users:
                messagebox.showerror("Error", "No user found")
                return
            
            username = list(users.keys())[0]
            
            if not verify_password(users[username].get('hash', ''), current):
                messagebox.showerror("Error", "Current password is incorrect")
                return
            
            if not is_password_acceptable(new_pwd):
                messagebox.showerror("Weak Password", "New password doesn't meet requirements")
                return
            
            if new_pwd != confirm:
                messagebox.showerror("Error", "Passwords don't match")
                return
            
            users[username]['hash'] = hash_password(new_pwd)
            users[username]['password_changed'] = datetime.now().isoformat()
            
            if self.config_mgr.save(self.config):
                self.config_mgr.log(f"Password changed for {username}", "INFO")
                messagebox.showinfo("Success", "Password changed successfully ✓")
                dialog.destroy()
            else:
                messagebox.showerror("Error", "Failed to save")
        
        btn_frame = tk.Frame(inner, bg=Theme.BG_CARD)
        btn_frame.pack(fill='x', pady=(10, 0))
        
        ModernButton(btn_frame, "Cancel", dialog.destroy, 'secondary').pack(side='right', padx=5)
        ModernButton(btn_frame, "Update Password", save_password, 'success').pack(side='right', padx=5)
    
    def _clear_logs(self):
        if messagebox.askyesno("Clear Logs", "Delete all security logs permanently?"):
            try:
                if os.path.exists(self.config_mgr.log_file):
                    os.remove(self.config_mgr.log_file)
                self.config_mgr.log("Logs cleared", "INFO")
                messagebox.showinfo("Done", "Logs cleared")
            except Exception as e:
                messagebox.showerror("Error", str(e))
    
    def _clear_captures(self):
        if messagebox.askyesno("Clear Captures", "Delete all captured photos permanently?"):
            try:
                for f in glob.glob(os.path.join(self.config_mgr.capture_dir, "*.jpg")):
                    os.remove(f)
                messagebox.showinfo("Done", "All captures deleted")
                self.show_captures() if self.current_view == 'captures' else None
            except Exception as e:
                messagebox.showerror("Error", str(e))
    
    # ─── ABOUT PAGE ───
    
    def show_about(self):
        self._clear_content()
        self._set_active("About")
        
        self._create_page_header("About", f"{APP_NAME} v{APP_VERSION}")
        
        content = tk.Frame(self.content_frame, bg=Theme.BG)
        content.pack(fill='both', expand=True, padx=30, pady=20)
        
        # Hero card
        hero = tk.Frame(content, bg=Theme.PRIMARY_DARK, relief='flat')
        hero.pack(fill='x', pady=(0, 15))
        
        hero_inner = tk.Frame(hero, bg=Theme.PRIMARY_DARK)
        hero_inner.pack(padx=40, pady=30)
        
        tk.Label(hero_inner, text="🛡️", font=(Theme.FONT, 48),
                bg=Theme.PRIMARY_DARK).pack()
        
        tk.Label(hero_inner, text=APP_NAME,
                font=(Theme.FONT, 28, 'bold'),
                bg=Theme.PRIMARY_DARK, fg=Theme.TEXT_WHITE).pack(pady=(5, 0))
        
        tk.Label(hero_inner, text=APP_TAGLINE,
                font=(Theme.FONT, 10),
                bg=Theme.PRIMARY_DARK, fg=Theme.TEXT_DIM).pack(pady=(2, 0))
        
        tk.Label(hero_inner, text=f"Version {APP_VERSION}",
                font=(Theme.FONT, 9, 'italic'),
                bg=Theme.PRIMARY_DARK, fg=Theme.TEXT_MUTED).pack(pady=(8, 0))
        
        # Info cards
        info_card = tk.Frame(content, bg=Theme.BG_CARD, relief='solid', bd=1)
        info_card.pack(fill='x', pady=(0, 15))
        
        info_inner = tk.Frame(info_card, bg=Theme.BG_CARD)
        info_inner.pack(fill='x', padx=25, pady=18)
        
        tk.Label(info_inner, text="Application Information",
                font=(Theme.FONT, 12, 'bold'),
                bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(anchor='w', pady=(0, 10))
        
        items = [
            ("Version", APP_VERSION),
            ("Platform", f"Windows {platform.release()}"),
            ("Python Version", f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"),
            ("Camera Module", "OpenCV " + (cv2.__version__ if OPENCV_AVAILABLE and cv2 else "Not available")),
            ("Data Directory", self.config_mgr.app_dir),
            ("Build", "Educational Edition"),
        ]
        
        for label, value in items:
            row = tk.Frame(info_inner, bg=Theme.BG_CARD)
            row.pack(fill='x', pady=3)
            
            tk.Label(row, text=label,
                    font=(Theme.FONT, 10),
                    bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY,
                    width=18, anchor='w').pack(side='left')
            
            tk.Label(row, text=value,
                    font=(Theme.FONT, 10, 'bold'),
                    bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY,
                    anchor='w').pack(side='left')
        
        # Features card
        feat_card = tk.Frame(content, bg=Theme.BG_CARD, relief='solid', bd=1)
        feat_card.pack(fill='x')
        
        feat_inner = tk.Frame(feat_card, bg=Theme.BG_CARD)
        feat_inner.pack(fill='x', padx=25, pady=18)
        
        tk.Label(feat_inner, text="✨ Key Features",
                font=(Theme.FONT, 12, 'bold'),
                bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(anchor='w', pady=(0, 10))
        
        features = [
            "Progressive lockout timer (15s → 30s → 60s → ... → 30min)",
            "Configurable failed attempt threshold (1-10)",
            "Strong password enforcement with live requirements",
            "Webcam intruder capture with multi-backend support",
            "Email alerts via secure SMTP (SSL)",
            "Real-time statistics and activity dashboard",
            "Intruder photo gallery with management",
            "Filterable security audit log",
            "Privacy-first: 100% local storage, no cloud",
            "SHA-256 password hashing",
            "Windows Registry auto-start integration",
        ]
        
        for feature in features:
            tk.Label(feat_inner, text=f"  ✓ {feature}",
                    font=(Theme.FONT, 9),
                    bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY,
                    anchor='w').pack(fill='x', pady=1)
    
    # ─── ACTIONS ───
    
    def _open_login(self):
        if messagebox.askyesno("Test Login", "Open the login screen?\n\nDashboard will close."):
            self.root.destroy()
            LoginApp().run()
    
    def _open_folder(self):
        try:
            os.startfile(self.config_mgr.app_dir)
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def _uninstall(self):
        if messagebox.askyesno("Uninstall SENTINEL",
                               "This will permanently remove:\n\n"
                               "• All configuration\n"
                               "• Security logs\n"
                               "• Captured photos\n"
                               "• Auto-start entry\n\n"
                               "Continue?"):
            try:
                disable_autostart()
                shutil.rmtree(self.config_mgr.app_dir)
                messagebox.showinfo("Uninstalled", f"{APP_NAME} has been removed.")
                self.root.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Uninstall failed: {e}")
    
    def run(self):
        self.root.mainloop()

# ════════════════════════════════════════════════════════════════════
#  LOGIN APP WITH PROGRESSIVE LOCKOUT
# ════════════════════════════════════════════════════════════════════

class LoginApp:
    """Fullscreen login with progressive lockout"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"{APP_NAME} — Authentication")
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg=Theme.PRIMARY_DARK)
        self.root.protocol("WM_DELETE_WINDOW", lambda: None)
        
        self.config_mgr = ConfigManager()
        self.config = self.config_mgr.load()
        
        if not self.config:
            messagebox.showerror("Error", "Configuration not found")
            sys.exit(1)
        
        self.failed_attempts = 0
        self.max_attempts = self.config.get('max_attempts', 3)
        self.lockout_count = 0
        self.is_locked = False
        self.countdown_remaining = 0
        self.countdown_after_id = None
        
        self.setup_ui()
    
    def calculate_lockout_duration(self):
        duration = INITIAL_LOCKOUT_SECONDS * (2 ** (self.lockout_count - 1))
        return min(duration, MAX_LOCKOUT_SECONDS)
    
    def format_time(self, seconds):
        if seconds < 60:
            return f"{seconds}s"
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}m {secs}s" if secs else f"{minutes}m"
    
    def setup_ui(self):
        # Background gradient effect with frames
        bg = tk.Frame(self.root, bg=Theme.PRIMARY_DARK)
        bg.pack(fill='both', expand=True)
        
        # Decorative accent
        tk.Frame(bg, bg=Theme.PRIMARY_LIGHT, height=4).pack(fill='x')
        
        self.center = tk.Frame(bg, bg=Theme.PRIMARY_DARK)
        self.center.place(relx=0.5, rely=0.5, anchor='center')
        
        # Logo
        tk.Label(self.center, text="🛡️",
                font=(Theme.FONT, 55),
                bg=Theme.PRIMARY_DARK).pack(pady=(0, 5))
        
        tk.Label(self.center, text=APP_NAME,
                font=(Theme.FONT, 32, 'bold'),
                bg=Theme.PRIMARY_DARK, fg=Theme.TEXT_WHITE).pack()
        
        tk.Label(self.center, text=APP_TAGLINE,
                font=(Theme.FONT, 10),
                bg=Theme.PRIMARY_DARK, fg=Theme.TEXT_DIM).pack(pady=(2, 25))
        
        # Login card
        self.card = tk.Frame(self.center, bg=Theme.BG_CARD, relief='flat')
        self.card.pack(padx=50)
        
        self.inner = tk.Frame(self.card, bg=Theme.BG_CARD)
        self.inner.pack(padx=55, pady=40)
        
        self.build_login_form()
        
        # Footer
        footer = tk.Frame(self.center, bg=Theme.PRIMARY_DARK)
        footer.pack(pady=15)
        
        tk.Label(footer,
                text=f"💻 {platform.node()}  •  Windows {platform.release()}  •  v{APP_VERSION}",
                font=(Theme.FONT, 9),
                bg=Theme.PRIMARY_DARK, fg=Theme.TEXT_DIM).pack()
        
        tk.Label(footer,
                text=f"🔒 Authorized access only  •  Max attempts: {self.max_attempts}",
                font=(Theme.FONT, 8),
                bg=Theme.PRIMARY_DARK, fg=Theme.TEXT_MUTED).pack(pady=(2, 0))
        
        # Exit button
        tk.Button(self.root, text="✕ Exit",
                 command=self.exit_app,
                 font=(Theme.FONT, 8),
                 bg='#1E293B', fg=Theme.TEXT_WHITE,
                 activebackground='#0F172A',
                 relief='flat', cursor='hand2',
                 padx=15, pady=5).place(relx=0.98, rely=0.98, anchor='se')
    
    def build_login_form(self):
        for w in self.inner.winfo_children():
            w.destroy()
        
        tk.Label(self.inner, text="Username",
                font=(Theme.FONT, 10, 'bold'),
                bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(anchor='w', pady=(0, 4))
        
        self.username_entry = tk.Entry(
            self.inner, font=(Theme.FONT, 12), width=32,
            relief='solid', bd=1,
            highlightthickness=1,
            highlightcolor=Theme.PRIMARY_LIGHT,
            highlightbackground=Theme.BORDER
        )
        self.username_entry.pack(ipady=7, pady=(0, 15))
        self.username_entry.focus()
        
        tk.Label(self.inner, text="Password",
                font=(Theme.FONT, 10, 'bold'),
                bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY).pack(anchor='w', pady=(0, 4))
        
        self.password_entry = PasswordEntry(self.inner)
        self.password_entry.pack(fill='x', pady=(0, 20))
        self.password_entry.bind('<Return>', lambda e: self.authenticate())
        
        self.login_btn = tk.Button(
            self.inner, text="🔓  Sign In",
            command=self.authenticate,
            font=(Theme.FONT, 11, 'bold'),
            bg=Theme.PRIMARY_LIGHT, fg=Theme.TEXT_WHITE,
            activebackground=Theme.PRIMARY,
            relief='flat', bd=0,
            cursor='hand2', width=30, height=2
        )
        self.login_btn.pack(pady=(0, 10))
        
        self.status_frame = tk.Frame(self.inner, bg=Theme.BG_CARD, height=40)
        self.status_frame.pack(fill='x', pady=(5, 0))
        self.status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(self.status_frame, text="",
                                    font=(Theme.FONT, 10),
                                    bg=Theme.BG_CARD)
        self.status_label.pack(pady=8)
    
    def show_lockout_ui(self):
        for w in self.inner.winfo_children():
            w.destroy()
        
        tk.Label(self.inner, text="🔒",
                font=(Theme.FONT, 50),
                bg=Theme.BG_CARD, fg=Theme.DANGER).pack(pady=(0, 5))
        
        tk.Label(self.inner, text="Account Locked",
                font=(Theme.FONT, 16, 'bold'),
                bg=Theme.BG_CARD, fg=Theme.DANGER).pack()
        
        tk.Label(self.inner,
                text=f"Lockout #{self.lockout_count} • Too many failed attempts",
                font=(Theme.FONT, 9),
                bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY).pack(pady=(2, 15))
        
        countdown_frame = tk.Frame(self.inner, bg=Theme.DANGER_LIGHT)
        countdown_frame.pack(fill='x', pady=10)
        
        tk.Label(countdown_frame, text="Try again in:",
                font=(Theme.FONT, 10),
                bg=Theme.DANGER_LIGHT, fg=Theme.DANGER).pack(pady=(12, 2))
        
        self.countdown_label = tk.Label(
            countdown_frame,
            text=self.format_time(self.countdown_remaining),
            font=(Theme.FONT, 36, 'bold'),
            bg=Theme.DANGER_LIGHT, fg=Theme.DANGER
        )
        self.countdown_label.pack(pady=(0, 12))
        
        next_duration = min(self.calculate_lockout_duration() * 2, MAX_LOCKOUT_SECONDS)
        warning_frame = tk.Frame(self.inner, bg=Theme.WARNING_LIGHT)
        warning_frame.pack(fill='x', pady=(10, 0))
        
        tk.Label(warning_frame,
                text=f"⚠️ Next lockout will be: {self.format_time(next_duration)}",
                font=(Theme.FONT, 9),
                bg=Theme.WARNING_LIGHT, fg='#92400E').pack(pady=8)
        
        actions = []
        if self.config.get('capture_on_lockout', True) and OPENCV_AVAILABLE:
            actions.append("📸 Photo captured")
        if self.config.get('email_on_lockout', True) and self.config.get('email', {}).get('enabled'):
            actions.append("📧 Email sent")
        
        if actions:
            tk.Label(self.inner,
                    text="  •  ".join(actions),
                    font=(Theme.FONT, 9, 'italic'),
                    bg=Theme.BG_CARD, fg=Theme.TEXT_SECONDARY).pack(pady=(15, 0))
    
    def exit_app(self):
        if messagebox.askyesno("Confirm Exit", "Exit the login screen?"):
            if self.countdown_after_id:
                self.root.after_cancel(self.countdown_after_id)
            self.root.destroy()
    
    def authenticate(self):
        if self.is_locked:
            return
        
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username or not password:
            self.show_status("Please enter both username and password", "warning")
            return
        
        self.config_mgr.update_stats(total_logins=1)
        
        users = self.config.get('users', {})
        stored_hash = users.get(username, {}).get('hash', '') if isinstance(users, dict) else ''

        if username in users and verify_password(stored_hash, password):
            if not stored_hash.startswith(HASH_PREFIX):
                # Transparent upgrade from the legacy unsalted SHA-256 format.
                users[username]['hash'] = hash_password(password)
                self.config['users'] = users
                self.config_mgr.save(self.config)
                self.config_mgr.log("Password hash upgraded to PBKDF2-SHA256", "INFO")
            self.config_mgr.log(f"✓ Successful login: {username}", "INFO")
            self.config_mgr.update_stats(successful_logins=1, last_login=datetime.now().isoformat())
            self.grant_access(username)
        else:
            self.config_mgr.update_stats(failed_attempts=1)
            self.handle_failed_attempt(username)
    
    def handle_failed_attempt(self, username):
        self.failed_attempts += 1
        attempts_remaining = self.max_attempts - self.failed_attempts
        
        self.password_entry.delete(0, tk.END)
        self.password_entry.focus()
        
        if attempts_remaining > 0:
            self.config_mgr.log(
                f"⚠ Failed attempt {self.failed_attempts}/{self.max_attempts}: {username}",
                "WARNING"
            )
            
            if attempts_remaining == 1:
                self.show_status(
                    "⚠ FINAL WARNING: 1 attempt remaining before lockout",
                    "danger"
                )
            else:
                self.show_status(
                    f"✗ Invalid credentials. {attempts_remaining} attempts remaining",
                    "warning"
                )
        else:
            self.trigger_lockout(username)
    
    def trigger_lockout(self, username):
        self.is_locked = True
        self.lockout_count += 1
        
        duration = self.calculate_lockout_duration()
        self.countdown_remaining = duration
        
        self.config_mgr.log(
            f"🚨 LOCKOUT #{self.lockout_count}: Account locked for {duration}s. User: {username}",
            "CRITICAL"
        )
        self.config_mgr.update_stats(
            total_lockouts=1,
            last_lockout=datetime.now().isoformat()
        )
        
        self.show_lockout_ui()
        
        threading.Thread(
            target=self._execute_security_actions,
            args=(username, duration),
            daemon=True
        ).start()
        
        self.start_countdown()
    
    def start_countdown(self):
        if self.countdown_remaining > 0:
            self.countdown_label.config(text=self.format_time(self.countdown_remaining))
            self.countdown_remaining -= 1
            self.countdown_after_id = self.root.after(1000, self.start_countdown)
        else:
            self.unlock_account()
    
    def unlock_account(self):
        self.is_locked = False
        self.failed_attempts = 0
        
        self.config_mgr.log(f"🔓 Lockout #{self.lockout_count} expired", "INFO")
        
        self.build_login_form()
        
        next_duration = self.calculate_lockout_duration() * 2
        if next_duration > MAX_LOCKOUT_SECONDS:
            next_duration = MAX_LOCKOUT_SECONDS
        
        self.show_status(
            f"🔓 You may try again. Next lockout: {self.format_time(next_duration)}",
            "info"
        )
    
    def _execute_security_actions(self, username, duration):
        image_path = None
        
        if self.config.get('capture_on_lockout', True) and OPENCV_AVAILABLE:
            self.config_mgr.log("📸 Capturing intruder photo...", "INFO")
            image_path = capture_intruder()
            
            if image_path:
                self.config_mgr.log(f"✓ Photo saved: {os.path.basename(image_path)}", "INFO")
            else:
                self.config_mgr.log("⚠ Photo capture failed", "WARNING")
        
        if (self.config.get('email_on_lockout', True) and
            self.config.get('email', {}).get('enabled')):
            
            self.config_mgr.log("📧 Sending email alert...", "INFO")
            
            success = send_security_alert(
                self.config['email'], image_path, username,
                self.max_attempts, self.lockout_count, duration
            )
            
            if success:
                self.config_mgr.log("✓ Email alert sent", "INFO")
            else:
                self.config_mgr.log("✗ Email alert failed", "ERROR")
    
    def grant_access(self, username):
        self.show_status("✓ Access Granted - Welcome!", "success")
        self.login_btn.config(state='disabled')
        self.username_entry.config(state='disabled')
        self.password_entry.config(state='disabled')
        
        if self.countdown_after_id:
            self.root.after_cancel(self.countdown_after_id)
        
        self.show_success_popup(username)
    
    def show_success_popup(self, username):
        popup = tk.Toplevel(self.root)
        popup.title("Access Granted")
        popup.geometry("450x280")
        popup.configure(bg=Theme.SUCCESS)
        popup.resizable(False, False)
        popup.attributes('-topmost', True)
        popup.overrideredirect(True)
        
        x = (popup.winfo_screenwidth() - 450) // 2
        y = (popup.winfo_screenheight() - 280) // 2
        popup.geometry(f"450x280+{x}+{y}")
        
        # Accent
        tk.Frame(popup, bg='#047857', height=4).pack(fill='x')
        
        tk.Label(popup, text="✓",
                font=(Theme.FONT, 50, 'bold'),
                bg=Theme.SUCCESS, fg=Theme.TEXT_WHITE).pack(pady=(25, 5))
        
        tk.Label(popup, text="Welcome back,",
                font=(Theme.FONT, 12),
                bg=Theme.SUCCESS, fg=Theme.TEXT_WHITE).pack()
        
        tk.Label(popup, text=username,
                font=(Theme.FONT, 20, 'bold'),
                bg=Theme.SUCCESS, fg=Theme.TEXT_WHITE).pack(pady=(0, 5))
        
        tk.Label(popup, text="Access has been granted",
                font=(Theme.FONT, 10),
                bg=Theme.SUCCESS, fg=Theme.TEXT_WHITE).pack(pady=10)
        
        tk.Frame(popup, bg='#047857', height=4).pack(side='bottom', fill='x')
        
        popup.after(2500, lambda: [popup.destroy(), self.root.destroy()])
    
    def show_status(self, message, style="info"):
        colors = {
            'info': Theme.PRIMARY_LIGHT,
            'success': Theme.SUCCESS,
            'warning': Theme.WARNING,
            'danger': Theme.DANGER
        }
        color = colors.get(style, Theme.TEXT_PRIMARY)
        weight = 'bold' if style == 'danger' else 'normal'
        
        self.status_label.config(
            text=message, fg=color,
            font=(Theme.FONT, 10, weight)
        )
    
    def run(self):
        self.root.mainloop()

# ════════════════════════════════════════════════════════════════════
#  MAIN ENTRY POINT
# ════════════════════════════════════════════════════════════════════

def launch_app():
    """Launch the appropriate app based on state"""
    config = ConfigManager()
    
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        
        if arg == '--login':
            LoginApp().run()
            return
        elif arg == '--dashboard':
            Dashboard().run()
            return
        elif arg == '--uninstall':
            if messagebox.askyesno("Confirm Uninstall",
                                  f"Uninstall {APP_NAME}?"):
                disable_autostart()
                try:
                    shutil.rmtree(config.app_dir)
                    messagebox.showinfo("Done", f"{APP_NAME} removed")
                except Exception as e:
                    messagebox.showerror("Error", str(e))
            return
        elif arg == '--help':
            print(f"""
{APP_NAME} v{APP_VERSION} — Commands:

  python sentinel.py              Smart launch (installer/dashboard)
  python sentinel.py --login      Show login screen
  python sentinel.py --dashboard  Open dashboard
  python sentinel.py --uninstall  Remove SENTINEL
  python sentinel.py --help       Show this help
            """)
            return
    
    # Smart launch
    if config.exists():
        # Already installed - go straight to dashboard
        Dashboard().run()
    else:
        # Fresh install
        InstallerApp().run()

def main():
    """Entry point with splash screen"""
    setup_opencv()

    if len(sys.argv) > 1:
        # Skip splash for command-line modes
        launch_app()
    else:
        # Show splash, then launch
        splash = SplashScreen(on_complete=launch_app)
        splash.run()

if __name__ == "__main__":
    main()
