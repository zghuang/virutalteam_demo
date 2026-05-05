import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock

import bcrypt
import jwt
from fastapi.testclient import TestClient

from app.main import app
from app.routers.auth import JWT_SECRET, JWT_ALGORITHM


class TestAuthEndpoints(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def _mock_user(self, username="testuser", password="password123"):
        hashed = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")
        user = MagicMock()
        user.id = 1
        user.username = username
        user.hashed_password = hashed
        user.created_at = datetime(2026, 1, 1, 12, 0, 0)
        return user

    def _create_token(self, username="testuser"):
        expire = datetime.now(timezone.utc) + timedelta(hours=24)
        return jwt.encode(
            {"sub": username, "exp": expire}, JWT_SECRET, algorithm=JWT_ALGORITHM
        )

    # Register tests

    @patch("app.routers.auth.SessionLocal")
    def test_register_success(self, mock_session_local):
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        mock_db.query.return_value.filter.return_value.first.return_value = None

        response = self.client.post(
            "/api/auth/register",
            json={"username": "newuser", "password": "securepass"},
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {"message": "User created"})
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    @patch("app.routers.auth.SessionLocal")
    def test_register_duplicate_username(self, mock_session_local):
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        existing = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = existing

        response = self.client.post(
            "/api/auth/register",
            json={"username": "testuser", "password": "password123"},
        )

        self.assertEqual(response.status_code, 409)
        self.assertIn("already registered", response.json()["detail"])

    # Login tests

    @patch("app.routers.auth.SessionLocal")
    def test_login_success(self, mock_session_local):
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        user = self._mock_user()
        mock_db.query.return_value.filter.return_value.first.return_value = user

        response = self.client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "password123"},
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("access_token", data)
        self.assertEqual(data["token_type"], "bearer")

    @patch("app.routers.auth.SessionLocal")
    def test_login_wrong_password(self, mock_session_local):
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        user = self._mock_user()
        mock_db.query.return_value.filter.return_value.first.return_value = user

        response = self.client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "wrongpassword"},
        )

        self.assertEqual(response.status_code, 401)
        self.assertIn("Invalid credentials", response.json()["detail"])

    @patch("app.routers.auth.SessionLocal")
    def test_login_user_not_found(self, mock_session_local):
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        mock_db.query.return_value.filter.return_value.first.return_value = None

        response = self.client.post(
            "/api/auth/login",
            json={"username": "nonexistent", "password": "password123"},
        )

        self.assertEqual(response.status_code, 401)
        self.assertIn("Invalid credentials", response.json()["detail"])

    # Me endpoint tests

    @patch("app.routers.auth.SessionLocal")
    def test_me_success(self, mock_session_local):
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        user = self._mock_user()
        mock_db.query.return_value.filter.return_value.first.return_value = user

        token = self._create_token()
        response = self.client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["id"], 1)
        self.assertEqual(data["username"], "testuser")

    @patch("app.routers.auth.SessionLocal")
    def test_me_invalid_token(self, mock_session_local):
        response = self.client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalidtoken123"},
        )

        self.assertEqual(response.status_code, 401)

    @patch("app.routers.auth.SessionLocal")
    def test_me_expired_token(self, mock_session_local):
        expired = datetime.now(timezone.utc) - timedelta(hours=1)
        token = jwt.encode(
            {"sub": "testuser", "exp": expired}, JWT_SECRET, algorithm=JWT_ALGORITHM
        )

        response = self.client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )

        self.assertEqual(response.status_code, 401)
        self.assertIn("expired", response.json()["detail"].lower())

    @patch("app.routers.auth.SessionLocal")
    def test_me_user_not_found(self, mock_session_local):
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        mock_db.query.return_value.filter.return_value.first.return_value = None

        token = self._create_token("nonexistent")
        response = self.client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )

        self.assertEqual(response.status_code, 404)

    @patch("app.routers.auth.SessionLocal")
    def test_me_no_auth_header(self, mock_session_local):
        response = self.client.get("/api/auth/me")
        self.assertEqual(response.status_code, 401)

    # Token creation tests

    def test_create_access_token_returns_string(self):
        from app.routers.auth import create_access_token

        token = create_access_token("testuser")
        self.assertIsInstance(token, str)

    def test_create_access_token_contains_username(self):
        from app.routers.auth import create_access_token

        token = create_access_token("testuser")
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        self.assertEqual(payload["sub"], "testuser")

    def test_create_access_token_has_expiration(self):
        from app.routers.auth import create_access_token

        token = create_access_token("testuser")
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        self.assertIn("exp", payload)


if __name__ == "__main__":
    unittest.main()
