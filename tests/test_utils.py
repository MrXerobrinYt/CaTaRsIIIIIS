"""Tests for Figura Unchained Backend - auth, profile, and utility functions."""

import sys
import os
import hashlib
import uuid
import json
import unittest
from unittest.mock import patch, MagicMock

# Ensure the project root is on the path so we can import server
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import server  # noqa: E402


class TestCanonicalUUID(unittest.TestCase):
    """canonical_uuid_for must produce a deterministic v3 UUID from a username."""

    def test_deterministic(self):
        u1 = server.canonical_uuid_for("Player1")
        u2 = server.canonical_uuid_for("Player1")
        self.assertEqual(u1, u2)

    def test_is_version_3(self):
        u = server.canonical_uuid_for("Player1")
        parsed = uuid.UUID(u)
        self.assertEqual(parsed.version, 3)

    def test_different_usernames_different_uuids(self):
        self.assertNotEqual(
            server.canonical_uuid_for("Alice"),
            server.canonical_uuid_for("Bob"),
        )


class TestCleanUsername(unittest.TestCase):
    """Username validation: 3-16 chars, alphanumeric + underscore."""

    def test_valid(self):
        self.assertEqual(server.clean_username("Player_1"), "Player_1")
        self.assertEqual(server.clean_username("abc"), "abc")
        self.assertEqual(server.clean_username("A" * 16), "A" * 16)

    def test_invalid(self):
        self.assertIsNone(server.clean_username("ab"))        # too short
        self.assertIsNone(server.clean_username("A" * 17))    # too long
        self.assertIsNone(server.clean_username("bad!name"))  # invalid char
        self.assertIsNone(server.clean_username(""))          # empty
        self.assertIsNone(server.clean_username(None))        # not a string


class TestIsValidUUID(unittest.TestCase):
    def test_valid_uuid(self):
        self.assertTrue(server.is_valid_uuid("550e8400-e29b-41d4-a716-446655440000"))

    def test_invalid_uuid(self):
        self.assertFalse(server.is_valid_uuid("not-a-uuid"))
        self.assertFalse(server.is_valid_uuid(""))
        self.assertFalse(server.is_valid_uuid(None))
        self.assertFalse(server.is_valid_uuid("550e8400-e29b-41d4-a716"))  # too short


class TestIsOfflineUUID(unittest.TestCase):
    def test_offline_uuid_v3(self):
        # MD5-based namespace DNS -> version 3
        u = str(uuid.uuid3(uuid.NAMESPACE_DNS, "example.com"))
        self.assertTrue(server.is_offline_uuid(u))

    def test_random_uuid_v4_not_offline(self):
        self.assertFalse(server.is_offline_uuid(str(uuid.uuid4())))


class TestParseAddonVersion(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(server.parse_addon_version("1.9.3"), (1, 9, 3))
        self.assertEqual(server.parse_addon_version("v2.0.1"), (2, 0, 1))

    def test_invalid(self):
        self.assertIsNone(server.parse_addon_version(""))
        self.assertIsNone(server.parse_addon_version("not-a-version"))
        self.assertIsNone(server.parse_addon_version("1.9"))


class TestAddonVersionStatus(unittest.TestCase):
    def setUp(self):
        server.MIN_ADDON_VERSION = (1, 9, 3)
        server.MIN_ADDON_VERSION_RAW = "1.9.3"

    def test_ok(self):
        self.assertEqual(server.addon_version_status("1.9.3"), "ok")
        self.assertEqual(server.addon_version_status("2.0.0"), "ok")

    def test_outdated(self):
        self.assertEqual(server.addon_version_status("1.9.2"), "outdated")
        self.assertEqual(server.addon_version_status("1.0.0"), "outdated")

    def test_missing_invalid(self):
        self.assertEqual(server.addon_version_status(""), "missing")
        self.assertEqual(server.addon_version_status("none"), "invalid")
        self.assertEqual(server.addon_version_status(None), "missing")


class TestGzipValidator(unittest.TestCase):
    def test_valid_gzip(self):
        import zlib
        comp = zlib.compressobj(9, zlib.DEFLATED, 16 + zlib.MAX_WBITS)
        data = comp.compress(b"hello world " * 100) + comp.flush()
        v = server.GzipValidator(limit=10000)
        self.assertTrue(v.feed(data))
        self.assertTrue(v.complete())

    def test_exceeds_limit(self):
        import zlib
        comp = zlib.compressobj(9, zlib.DEFLATED, 16 + zlib.MAX_WBITS)
        data = comp.compress(b"x" * 20000000) + comp.flush()
        v = server.GzipValidator(limit=100)
        self.assertFalse(v.feed(data))


class TestUtils(unittest.TestCase):
    def test_fmt_dur(self):
        self.assertEqual(server.fmt_dur(0), "0s")
        self.assertEqual(server.fmt_dur(45), "45s")
        self.assertEqual(server.fmt_dur(90), "1m30s")
        self.assertEqual(server.fmt_dur(3661), "1h01m")

    def test_short_uuid(self):
        u = "550e8400-e29b-41d4-a716-446655440000"
        self.assertEqual(server.short_uuid(u), "550e8400")


if __name__ == "__main__":
    unittest.main()
