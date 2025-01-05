# tests/test_attempts.py
import pytest
from datetime import datetime, timedelta

def test_log_attempt(test_client, test_db):
    """Test logging a new attempt"""
    response = test_client.post('/log_attempt/1', data={
        'comfort': 'Medium',
        'notes': 'Test attempt notes'
    })
    assert response.status_code == 302  # Should redirect after successful log
    
    # Verify attempt was logged in database
    attempts = test_db.get_problem_history(1)
    assert len(attempts) == 1
    assert attempts[0]['comfort_level'] == 'Medium'
    assert attempts[0]['notes'] == 'Test attempt notes'

def test_attempt_validation(test_client):
    """Test attempt logging validation"""
    # Test missing comfort level
    response = test_client.post('/log_attempt/1', data={
        'notes': 'Test notes'
    })
    assert response.status_code != 200  # Should fail
    
    # Test invalid problem ID
    response = test_client.post('/log_attempt/999', data={
        'comfort': 'Medium',
        'notes': 'Test notes'
    })
    assert response.status_code != 200  # Should fail
    
    # Test invalid comfort level
    response = test_client.post('/log_attempt/1', data={
        'comfort': 'Invalid',
        'notes': 'Test notes'
    })
    assert response.status_code != 200  # Should fail

def test_due_problems(test_client, test_db):
    """Test due problems functionality"""
    # Add an attempt due for review
    test_db.log_attempt(1, 'Medium', 'Test notes', 0)  # Due immediately
    
    # Check due problems section
    response = test_client.get('/')
    assert b'Due for Review' in response.data
    assert b'Two Sum' in response.data
    
    # Add attempt with future review date
    test_db.log_attempt(2, 'High', 'Test notes', 30)  # Due in 30 days
    response = test_client.get('/')
    assert b'Add Two Numbers' not in response.data  # Shouldn't be due yet

def test_attempt_history(test_client, test_db):
    """Test viewing attempt history"""
    # Add multiple attempts
    test_db.log_attempt(1, 'Low', 'First attempt', 2)
    test_db.log_attempt(1, 'Medium', 'Second attempt', 6)
    
    # View history page
    response = test_client.get('/history/1')
    assert response.status_code == 200
    assert b'Two Sum' in response.data
    assert b'First attempt' in response.data
    assert b'Second attempt' in response.data
    
    # Test invalid problem ID
    response = test_client.get('/history/999')
    assert response.status_code == 200  # Should show error page
    assert b'Problem Not Found' in response.data

def test_comfort_level_progression(test_client, test_db):
    """Test comfort level progression over multiple attempts"""
    # Log progression from Low to High
    test_db.log_attempt(1, 'Low', 'Struggling', 2)
    test_db.log_attempt(1, 'Medium', 'Getting better', 6)
    test_db.log_attempt(1, 'High', 'Mastered', 21)
    
    # Check history shows progression
    response = test_client.get('/history/1')
    data = response.data.decode('utf-8')
    
    # Verify attempts appear in reverse chronological order
    high_pos = data.find('High')
    medium_pos = data.find('Medium')
    low_pos = data.find('Low')
    
    assert high_pos < medium_pos < low_pos  # Most recent (High) should appear first
