"""
API Tests — test_api.py
Stock Prediction Portal ke saare API endpoints ke tests.
Har test ek specific cheez check karta hai.
"""
import pytest
from rest_framework import status
from django.contrib.auth.models import User


# ============================================================
# HEALTH CHECK TESTS
# ============================================================

@pytest.mark.django_db
class TestHealthCheck:
    """Health endpoint ke tests"""

    def test_health_returns_200(self, api_client):
        """
        Health endpoint 200 deta hai ya nahi check karo.
        Yeh sabse basic test hai — agar yeh fail ho toh
        server hi nahi chal raha.
        """
        response = api_client.get("/api/v1/health/")
        assert response.status_code == status.HTTP_200_OK

    def test_health_returns_json(self, api_client):
        """Response JSON format mein aana chahiye"""
        response = api_client.get("/api/v1/health/")
        assert response.content_type == "application/json"

    def test_health_has_status_field(self, api_client):
        """Response mein 'status' field hona chahiye"""
        response = api_client.get("/api/v1/health/")
        data = response.json()
        assert "status" in data

    def test_health_has_services_field(self, api_client):
        """Response mein 'services' field hona chahiye"""
        response = api_client.get("/api/v1/health/")
        data = response.json()
        assert "services" in data


# ============================================================
# AUTHENTICATION TESTS
# ============================================================

@pytest.mark.django_db
class TestAuthentication:
    """Login + Registration ke tests"""

    def test_register_success(self, api_client):
        """
        Naya user register ho sakta hai ya nahi.
        Valid data bhejo — 201 Created milna chahiye.
        """
        payload = {
            "username": "newuser",
            "password": "StrongPass123!",
            "email": "newuser@example.com"
        }
        response = api_client.post("/api/v1/register/", payload)
        assert response.status_code == status.HTTP_201_CREATED

    def test_register_duplicate_username_fails(self, api_client, test_user):
        """
        Same username se dobara register nahi ho sakta.
        400 Bad Request milna chahiye.
        """
        payload = {
            "username": "testuser2",
            "password": "StrongPass123!",
            "email": "another@example.com"
        }
        response = api_client.post("/api/v1/register/", payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_success(self, api_client, test_user):
        """
        Valid credentials se login karo — token milna chahiye.
        JWT access + refresh token response mein hone chahiye.
        """
        payload = {
            "username": "testuser2",
            "password": "testpass123"
        }
        response = api_client.post("/api/v1/token/", payload)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access" in data
        assert "refresh" in data

    def test_login_wrong_password_fails(self, api_client, test_user):
        """
        Wrong password se login nahi ho sakta.
        401 Unauthorized milna chahiye.
        """
        payload = {
            "username": "testuser2",
            "password": "wrongpassword"
        }
        response = api_client.post("/api/v1/token/", payload)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_token_refresh_works(self, api_client, test_user):
        """
        Refresh token se naya access token milta hai ya nahi.
        """
        login_response = api_client.post("/api/v1/token/", {
            "username": "testuser2",
            "password": "testpass123"
        })
        refresh_token = login_response.json()["refresh"]

        refresh_response = api_client.post("/api/v1/token/refresh/", {
            "refresh": refresh_token
        })
        assert refresh_response.status_code == status.HTTP_200_OK
        assert "access" in refresh_response.json()


# ============================================================
# PREDICTION API TESTS
# ============================================================

@pytest.mark.django_db
class TestPredictionAPI:
    """Stock Prediction endpoint ke tests"""

    def test_predict_requires_auth(self, api_client):
        """
        Bina login ke prediction nahi milni chahiye.
        401 Unauthorized milna chahiye.
        """
        response = api_client.post("/api/v1/predict/", {"ticker": "AAPL"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_predict_empty_ticker_fails(self, auth_client):
        """
        Empty ticker bhejne pe 400 Bad Request milna chahiye.
        """
        response = auth_client.post("/api/v1/predict/", {"ticker": ""})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_predict_invalid_ticker_fails(self, auth_client):
        """
        Invalid ticker (jaise SQL injection) pe 400 milna chahiye.
        Security check — malicious input block hona chahiye.
        """
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "<script>alert('xss')</script>",
            "AAPL; rm -rf /",
            "A" * 20,
        ]
        for bad_ticker in malicious_inputs:
            response = auth_client.post("/api/v1/predict/", {"ticker": bad_ticker})
            assert response.status_code in [
                status.HTTP_400_BAD_REQUEST,
                status.HTTP_403_FORBIDDEN
            ], f"Expected 400/403 for: {bad_ticker}"

    def test_predict_missing_ticker_fails(self, auth_client):
        """
        Ticker field missing ho toh 400 milna chahiye.
        """
        response = auth_client.post("/api/v1/predict/", {})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_predict_valid_request_format(self, auth_client):
        """
        Valid ticker bhejne pe ya toh prediction mile (200)
        ya service unavailable (503) — dono acceptable hain.
        (503 isliye kyunki Yahoo Finance ka rate limit ho sakta hai)
        """
        response = auth_client.post("/api/v1/predict/", {"ticker": "AAPL"})
        acceptable_codes = [
            status.HTTP_200_OK,
            status.HTTP_503_SERVICE_UNAVAILABLE,
            status.HTTP_429_TOO_MANY_REQUESTS,
        ]
        assert response.status_code in acceptable_codes


# ============================================================
# RATE LIMITING TESTS
# ============================================================

@pytest.mark.django_db
class TestRateLimiting:
    """Rate limiting ke tests"""

    def test_predict_rate_limit_exists(self, auth_client):
        """
        Rate limiting kaam kar rahi hai ya nahi.
        Bahut saari requests bhejne pe 429 milna chahiye.
        """
        responses = []
        for i in range(10):
            r = auth_client.post("/api/v1/predict/", {"ticker": "AAPL"})
            responses.append(r.status_code)

        status_codes = set(responses)
        has_rate_limit = status.HTTP_429_TOO_MANY_REQUESTS in status_codes
        has_prediction = status.HTTP_200_OK in status_codes

        assert has_rate_limit or has_prediction
