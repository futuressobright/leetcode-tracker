# tests/conftest.py
import sys
sys.path.append('..')

import pytest
import os
import sqlite3
from database import Database

@pytest.fixture
def test_db_path():
    """Provide a path for the test database"""
    return 'leetcode_test.db'

@pytest.fixture
def db(test_db_path):
    """Create a test database with schema"""
    # Remove test database if it exists
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    # Create fresh database
    db = Database(test_db_path)
    conn = db.get_connection()
    
    # Read and execute schema
    with open('schema.sql', 'r') as f:
        conn.executescript(f.read())
    
    # Add some test data
    conn.executescript('''
        INSERT INTO problems (leetcode_id, title, difficulty, topics) 
        VALUES 
            ('1', 'Test Problem 1', 'Easy', 'Arrays,Strings'),
            ('2', 'Test Problem 2', 'Medium', 'LinkedList,Trees');
            
        INSERT INTO lists (slot, name)
        VALUES 
            (1, 'Test List 1'),
            (2, 'Test List 2');
    ''')
    conn.commit()
    
    yield db
    
    # Cleanup after tests
    db.close()
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
