# tests/test_problems.py
import pytest
from datetime import datetime, timedelta

def test_index_route(test_client):
    """Test the main page loads successfully"""
    response = test_client.get('/')
    assert response.status_code == 200
    assert b'LeetCode Tracker' in response.data

def test_problem_listing(test_client):
    """Test that problems are listed correctly"""
    response = test_client.get('/')
    assert b'Two Sum' in response.data
    assert b'Add Two Numbers' in response.data
    assert b'Easy' in response.data
    assert b'Medium' in response.data

def test_search_functionality(test_client):
    """Test search functionality"""
    # Test exact title match
    response = test_client.get('/?search=Two+Sum')
    assert b'Two Sum' in response.data
    assert b'Add Two Numbers' not in response.data
    
    # Test partial match
    response = test_client.get('/?search=Two')
    assert b'Two Sum' in response.data
    assert b'Add Two Numbers' in response.data
    
    # Test topic search
    response = test_client.get('/?search=Arrays')
    assert b'Two Sum' in response.data
    assert b'Longest Substring' not in response.data

def test_difficulty_sorting(test_client):
    """Test difficulty sorting functionality"""
    # Test ascending sort (Easy to Hard)
    response = test_client.get('/?difficulty_sort=asc')
    data = response.data.decode('utf-8')
    easy_pos = data.find('Two Sum')  # Easy problem
    medium_pos = data.find('Add Two Numbers')  # Medium problem
    assert easy_pos < medium_pos  # Easy should appear before Medium
    
    # Test descending sort (Hard to Easy)
    response = test_client.get('/?difficulty_sort=desc')
    data = response.data.decode('utf-8')
    easy_pos = data.find('Two Sum')  # Easy problem
    medium_pos = data.find('Add Two Numbers')  # Medium problem
    assert medium_pos < easy_pos  # Medium should appear before Easy

def test_list_filtering(test_client, test_db):
    """Test filtering by custom lists"""
    # Add a problem to List 1
    test_db.toggle_list(1, 1)  # Add 'Two Sum' to List 1
    
    # Test filtering by List 1
    response = test_client.get('/?list=1')
    assert b'Two Sum' in response.data
    assert b'Add Two Numbers' not in response.data

def test_never_attempted_filter(test_client, test_db):
    """Test filtering for never attempted problems"""
    # Log an attempt for one problem
    add_test_attempt(test_db, 1)  # Add attempt for 'Two Sum'
    
    # Test never attempted filter
    response = test_client.get('/?never_attempted=true')
    assert b'Two Sum' not in response.data  # Should not show attempted problem
    assert b'Add Two Numbers' in response.data  # Should show unattempted problem

def test_pagination(test_client):
    """Test pagination functionality"""
    # First page should show default number of problems
    response = test_client.get('/')
    assert response.status_code == 200
    
    # Test with explicit page parameter
    response = test_client.get('/?page=1')
    assert response.status_code == 200
    
    # Test invalid page number
    response = test_client.get('/?page=999')
    assert response.status_code == 200  # Should still return 200 but might be empty
