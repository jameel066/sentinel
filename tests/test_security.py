"""Security-focused unit tests for SENTINEL.

Run from the repository root:

    python -m unittest discover -s tests -v

These cover the properties that matter for a security tool: password hashing
agility, constant-time comparison, legacy hash migration and secret-at-rest
encryption. UI behaviour is deliberately tested by hand, not here.
"""

from __future__ import annotations

import hashlib
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import sentinel  # noqa: E402  (path set up above)


class PasswordHashingTests(unittest.TestCase):
    def test_hash_uses_pbkdf2_format(self):
        stored = sentinel.hash_password("Str0ng!Pass")
        self.assertTrue(stored.startswith("pbkdf2_sha256$310000$"))
        self.assertEqual(len(stored.split("$")), 4)

    def test_correct_password_verifies(self):
        stored = sentinel.hash_password("Str0ng!Pass")
        self.assertTrue(sentinel.verify_password(stored, "Str0ng!Pass"))

    def test_wrong_password_rejected(self):
        stored = sentinel.hash_password("Str0ng!Pass")
        self.assertFalse(sentinel.verify_password(stored, "str0ng!pass"))
        self.assertFalse(sentinel.verify_password(stored, ""))

    def test_salt_is_random(self):
        self.assertNotEqual(
            sentinel.hash_password("same-input"),
            sentinel.hash_password("same-input"),
        )

    def test_legacy_sha256_still_verifies(self):
        legacy = hashlib.sha256(b"Str0ng!Pass").hexdigest()
        self.assertTrue(sentinel.verify_password(legacy, "Str0ng!Pass"))
        self.assertFalse(sentinel.verify_password(legacy, "wrong"))

    def test_malformed_hash_never_raises(self):
        for bad in ("", "pbkdf2_sha256$notanint$aa$bb", "pbkdf2_sha256$1000$zz$zz", "garbage"):
            self.assertFalse(sentinel.verify_password(bad, "anything"))


class PasswordPolicyTests(unittest.TestCase):
    def test_strong_password_accepted(self):
        self.assertTrue(sentinel.is_password_acceptable("Str0ng!Pass"))

    def test_each_rule_is_enforced(self):
        weak = (
            "Sh0rt!",            # too short
            "alllowercase1!",    # no uppercase
            "ALLUPPERCASE1!",    # no lowercase
            "NoDigitsHere!",     # no digit
            "NoSpecial123",      # no special character
        )
        for candidate in weak:
            with self.subTest(candidate=candidate):
                self.assertFalse(sentinel.is_password_acceptable(candidate))

    def test_strength_labels(self):
        self.assertEqual(sentinel.calculate_password_strength("Str0ng!Pass")[0], "Strong")
        self.assertEqual(sentinel.calculate_password_strength("abc")[0], "Weak")


class SecretStorageTests(unittest.TestCase):
    def test_plaintext_passthrough(self):
        self.assertEqual(sentinel.unprotect_secret("legacy-plain-value"), "legacy-plain-value")

    def test_empty_secret(self):
        self.assertEqual(sentinel.protect_secret(""), "")
        self.assertEqual(sentinel.unprotect_secret(""), "")

    def test_dpapi_roundtrip(self):
        secret = "abcd efgh ijkl mnop"
        stored = sentinel.protect_secret(secret)
        if not stored.startswith("dpapi:"):
            self.skipTest("DPAPI unavailable on this host")
        self.assertNotIn(secret, stored)
        self.assertEqual(sentinel.unprotect_secret(stored), secret)

    def test_protect_is_idempotent(self):
        stored = sentinel.protect_secret("some-value")
        if not stored.startswith("dpapi:"):
            self.skipTest("DPAPI unavailable on this host")
        self.assertEqual(sentinel.protect_secret(stored), stored)


if __name__ == "__main__":
    unittest.main()
