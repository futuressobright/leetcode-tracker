# tests/test_basic.py
import pytest
from app import app

def test_home_page():
    """Test that the home page loads"""
    client = app.test_client()
    response = client.get('/')
    assert response.status_code == 200
    assert b'LeetCode Tracker' in response.data

def test_error_page():
    """Test that non-existent routes return error page"""
    client = app.test_client()
    response = client.get('/nonexistent')
    assert response.status_code == 404
