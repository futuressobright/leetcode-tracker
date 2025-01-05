# tests/conftest.py
import pytest
import sqlite3
import os
from app import app
from database import Database

@pytest.fixture(scope="function")
def test_db_path(tmpdir):
    """Create a temporary database file path"""
    db_path = tmpdir.join("test_leetcode.db")
    return str(db_path)

@pytest.fixture(scope="function")
def init_database(test_db_path):
    """Initialize test database with schema and test data"""
    # Create new test database
    conn = sqlite3.connect(test_db_path)
    
    try:
        # Read and execute schema
        with open('schema.sql', 'r') as f:
            conn.executescript(f.read())
        
        # Insert test data
        conn.executescript('''
            INSERT INTO problems (leetcode_id, title, difficulty, topics) VALUES 
                ('1', 'Two Sum', 'Easy', 'Arrays,Hash Table');
                
            INSERT INTO lists (slot, name) VALUES 
                (1, 'List 1'),
                (2, 'List 2');
        ''')
        conn.commit()
        
    except Exception as e:
        print(f"Error initializing test database: {e}")
        conn.close()
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
        raise
    
    conn.close()
    return test_db_path

@pytest.fixture
def test_client(init_database):
    """Configure Flask test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
