"""
========================================================================
CONFTEST.PY - PYTEST CONFIGURATION & FIXTURES
========================================================================

YEH BILKUL IMPORTANT FILE HAI!

Fixtures = Setup code jo har test se pehle run hota hai
Database setup, user creation, API client setup, cache clearing

Agar yeh file nahi hai to tests fail honge!
========================================================================
"""

import pytest
import json
from django.contrib.auth.models import User
from django.test import Client
from rest_framework.test import APIClient
from rest_framework import status
from django.core.cache import cache
from django.conf import settings


# ========================================================================
# 1. API CLIENT FIXTURES
# ========================================================================

@pytest.fixture
def api_client():
    """
    🔧 Unauthenticated API Client
    
    Use case: Testing public endpoints (health check, login)
    
    Example:
        def test_health_check(api_client):
            response = api_client.get('/api/v1/health/')
            assert response.status_code == 200
    """
    return APIClient()


@pytest.fixture
def client():
    """
    🔧 Django Test Client (for non-API endpoints)
    
    Use case: Testing views directly
    """
    return Client()


# ========================================================================
# 2. DATABASE FIXTURES
# ========================================================================

@pytest.fixture
def test_user(db):
    """
    👤 Create test user in database
    
    Username: testuser
    Email: test@example.com
    Password: TestPass123!
    
    Use case: Any test that needs user authentication
    
    Example:
        def test_user_login(test_user, api_client):
            assert test_user.username == 'testuser'
    
    Note: (db) parameter tells pytest to use database
    """
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='TestPass123!'
    )
    return user


@pytest.fixture
def test_admin_user(db):
    """
    👑 Create admin test user
    
    Use case: Testing admin-only endpoints
    """
    admin = User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='AdminPass123!'
    )
    return admin


@pytest.fixture
def test_user_data():
    """
    📝 Test user credentials for registration/login
    
    Use case: Testing login endpoint
    
    Example:
        def test_login(api_client, test_user_data):
            response = api_client.post('/api/v1/token/', test_user_data)
    """
    return {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'TestPass123!',
        'confirm_password': 'TestPass123!'
    }


# ========================================================================
# 3. AUTHENTICATED CLIENT FIXTURES
# ========================================================================

@pytest.fixture
def auth_client(test_user):
    """
    🔑 Authenticated API Client (logged-in user)
    
    Automatically sets JWT token for protected endpoints
    
    Use case: Testing endpoints that require authentication
    
    Example:
        def test_predict_endpoint(auth_client):
            response = auth_client.post('/api/v1/predict/', {
                'ticker': 'AAPL',
                'days': 30
            })
            assert response.status_code == 200
    """
    client = APIClient()
    client.force_authenticate(user=test_user)
    return client


@pytest.fixture
def admin_client(test_admin_user):
    """
    👑 Authenticated Admin Client
    
    Use case: Testing admin-only endpoints
    """
    client = APIClient()
    client.force_authenticate(user=test_admin_user)
    return client


# ========================================================================
# 4. CACHE & RATE LIMITING FIXTURES
# ========================================================================

@pytest.fixture(autouse=True)
def clear_cache():
    """
    🧹 Clear cache before and after each test
    
    🔴 CRITICAL FOR RATE LIMITING TESTS!
    
    Problem: 
    - Rate limiting cache persists between tests
    - If test 1 makes 100 requests, test 2 fails (rate limited)
    - Cache must be cleared before each test
    
    Solution:
    - autouse=True = Automatically runs before every test
    - cache.clear() = Wipes all Redis data
    
    Flow:
    Test Start → cache.clear() → Run test → cache.clear() → Next test
    """
    cache.clear()
    yield  # Test runs here
    cache.clear()


@pytest.fixture
def reset_rate_limit_cache():
    """
    🔄 Manual cache reset (if needed)
    
    Use case: Custom rate limit testing
    
    Example:
        def test_rate_limit(auth_client, reset_rate_limit_cache):
            # Make requests...
            reset_rate_limit_cache  # Clear cache mid-test
    """
    cache.clear()
    return cache


# ========================================================================
# 5. ML MODEL FIXTURES
# ========================================================================

@pytest.fixture
def ml_model_data():
    """
    📊 Sample ML model input data
    
    Use case: Testing ML endpoint
    
    Example:
        def test_predict(auth_client, ml_model_data):
            response = auth_client.post('/api/v1/predict/', ml_model_data)
    """
    return {
        'ticker': 'AAPL',
        'days': 30,
        'start_date': '2024-01-01',
        'end_date': '2024-12-31'
    }


# ========================================================================
# 6. TOKEN FIXTURES
# ========================================================================

@pytest.fixture
def auth_token(test_user, api_client):
    """
    🎫 JWT authentication token
    
    Use case: Testing API with manual token (advanced)
    
    Example:
        def test_with_token(api_client, auth_token):
            api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + auth_token)
    """
    response = api_client.post('/api/v1/token/', {
        'username': 'testuser',
        'password': 'TestPass123!'
    })
    return response.data.get('access')


# ========================================================================
# 7. CONFIGURATION FIXTURES
# ========================================================================

@pytest.fixture
def api_base_url():
    """
    🌐 API base URL
    
    Use case: Constructing full API endpoints
    """
    return '/api/v1'


@pytest.fixture
def test_settings(settings):
    """
    ⚙️ Django settings for testing
    
    Use case: Custom test configuration
    """
    settings.DEBUG = True
    settings.ALLOWED_HOSTS = ['*']
    return settings


# ========================================================================
# 8. RESPONSE VALIDATION FIXTURES
# ========================================================================

@pytest.fixture
def assert_valid_json_response():
    """
    ✅ Helper function to validate JSON responses
    
    Use case: Reusable response validation
    
    Example:
        def test_api(auth_client, assert_valid_json_response):
            response = auth_client.get('/api/v1/endpoint/')
            assert_valid_json_response(response, status.HTTP_200_OK)
    """
    def _assert(response, expected_status=status.HTTP_200_OK):
        assert response.status_code == expected_status, \
            f"Expected {expected_status}, got {response.status_code}: {response.content}"
        assert response['Content-Type'] == 'application/json'
        return response.json()
    return _assert


# ========================================================================
# USAGE GUIDE
# ========================================================================

"""
COMMON TEST PATTERNS:

1️⃣ Public endpoint (no auth needed):
   def test_health_check(api_client):
       response = api_client.get('/api/v1/health/')
       assert response.status_code == 200

2️⃣ Protected endpoint (login required):
   def test_protected(auth_client):
       response = auth_client.get('/api/v1/protected/')
       assert response.status_code == 200

3️⃣ Create user and login:
   def test_login_flow(api_client, test_user_data):
       # Register
       response = api_client.post('/api/v1/register/', test_user_data)
       assert response.status_code == 201
       
       # Login
       response = api_client.post('/api/v1/token/', {
           'username': test_user_data['username'],
           'password': test_user_data['password']
       })
       assert response.status_code == 200
       assert 'access' in response.data

4️⃣ Rate limit test (cache cleared automatically):
   def test_rate_limit(auth_client):
       # Make 101 requests (limit is 100/min)
       for i in range(101):
           response = auth_client.get('/api/v1/endpoint/')
       # 101st should be rate limited (429)
       assert response.status_code == 429

5️⃣ ML model test:
   def test_predict(auth_client, ml_model_data):
       response = auth_client.post('/api/v1/predict/', ml_model_data)
       assert response.status_code == 200
       assert 'prediction' in response.data
"""

# ========================================================================
# END OF CONFTEST.PY
# ========================================================================
