"""
Test Configuration — conftest.py
Yeh file pytest ko batati hai ki tests kaise setup karni hain.
Saare tests isko automatically use karte hain.
"""
import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User


@pytest.fixture(scope="session")
def django_db_setup():
    """Test database setup — ek baar run hoti hai puri test session mein"""
    pass


@pytest.fixture
def api_client():
    """
    Unauthenticated API client — login ke bina requests karne ke liye.
    Yeh public endpoints test karne ke kaam aata hai.
    """
    return APIClient()


@pytest.fixture
def auth_client(db):
    """
    Authenticated API client — login karke requests karne ke liye.
    Yeh protected endpoints test karne ke kaam aata hai.
    """
    user = User.objects.create_user(
        username="testuser",
        password="testpass123",
        email="test@example.com"
    )
    client = APIClient()

    # JWT token lo
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)

    # Header mein token set karo
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
    return client


@pytest.fixture
def test_user(db):
    """
    Test user fixture — jab bhi user ki zarurat ho tests mein.
    """
    return User.objects.create_user(
        username="testuser2",
        password="testpass123",
        email="test2@example.com"
    )


@pytest.fixture
def admin_user(db):
    """
    Admin user fixture — admin operations test karne ke liye.
    """
    return User.objects.create_superuser(
        username="adminuser",
        password="adminpass123",
        email="admin@example.com"
    )
