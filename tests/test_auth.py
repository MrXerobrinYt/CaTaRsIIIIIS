"""Tests for authentication and profile endpoints (unit, mocked DB)."""

import sys
import os
import hashlib
import uuid
import json
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import server  # noqa: E402


class TestAuthStatus(unittest.TestCase):
    """auth_status must correctly evaluate registration, bans, and tokens."""

    def setUp(self):
        server.REQUIRE_AUTH = True
        server.db_conn = MagicMock()
        server.db_lock = MagicMock()

    def test_banned_user(self):
        server.db_conn.execute.return_value.fetchone.return_value = (1,)
        request = MagicMock()
        request.headers = {}
        authed, reason = server.auth_status(request, "550e8400-e29b-41d4-a716-446655440000")
        self.assertFalse(authed)
        self.assertEqual(reason, "account-banned")

    def test_unregistered_user(self):
        # First query: bans -> None. Second query: users -> None.
        server.db_conn.execute.return_value.fetchone.side_effect = [None, None]
        request = MagicMock()
        request.headers = {}
        authed, reason = server.auth_status(request, "550e8400-e29b-41d4-a716-446655440000")
        self.assertFalse(authed)
        self.assertEqual(reason, "unregistered")

    def test_auth_disabled(self):
        server.REQUIRE_AUTH = False
        request = MagicMock()
        request.headers = {}
        authed, reason = server.auth_status(request, "550e8400-e29b-41d4-a716-446655440000")
        self.assertTrue(authed)
        self.assertEqual(reason, "auth-disabled")

    def test_no_token(self):
        server.db_conn.execute.return_value.fetchone.side_effect = [None, (1,)]
        request = MagicMock()
        request.headers = {}
        authed, reason = server.auth_status(request, "550e8400-e29b-41d4-a716-446655440000")
        self.assertFalse(authed)
        self.assertEqual(reason, "no-token")

    def test_invalid_token(self):
        server.db_conn.execute.return_value.fetchone.side_effect = [None, (1,)]
        request = MagicMock()
        request.headers = {"token": "invalid-token"}
        authed, reason = server.auth_status(request, "550e8400-e29b-41d4-a716-446655440000")
        self.assertFalse(authed)
        self.assertEqual(reason, "token-invalid")


class TestCanonicalMapping(unittest.TestCase):
    """Username <-> canonical UUID mapping must be consistent."""

    def test_register_and_resolve(self):
        name = "TestPlayer"
        canonical = server.canonical_uuid_for(name)
        server.register_known_user(name)
        self.assertEqual(server.username_for_canonical(canonical), name)
        self.assertEqual(server.resolve_canonical(canonical), canonical)


class TestProfileEndpoint(unittest.TestCase):
    """handle_user_profile should return equipped avatar and badges."""

    def setUp(self):
        server.hash_cache = {}
        server.users_with_avatars = set()
        server.user_badges = {}
        server.MAX_PRIDE_BADGE_ID = 63

    @patch("server.os.path.exists", return_value=True)
    @patch("server.asyncio.to_thread")
    async def test_profile_with_avatar(self, mock_to_thread, mock_exists):
        mock_to_thread.return_value = "abc123hash"
        target_uuid = "550e8400-e29b-41d4-a716-446655440000"
        server.uuid_to_username[target_uuid] = "TestPlayer"
        server.user_canonical_uuids["TestPlayer"] = target_uuid

        request = MagicMock()
        request.match_info = {"uuid": target_uuid}

        resp = await server.handle_user_profile(request)
        body = resp.body if hasattr(resp, 'body') else None
        self.assertIsNotNone(body)


if __name__ == "__main__":
    unittest.main()
