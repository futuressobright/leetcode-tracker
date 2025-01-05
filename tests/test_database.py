# tests/test_database.py
import pytest
import sqlite3
from database import Database

def test_database_connection(init_database, test_db_path):
    """Test basic database connection and operations"""
    try:
        # Create database instance with initialized test database
        db = Database(test_db_path)
        
        # Test simple query
        problems = db.get_problems()
        
        # Verify the structure
        assert isinstance(problems, dict), "get_problems should return a dictionary"
        assert 'problems' in problems, "Result should have 'problems' key"
        assert 'total' in problems, "Result should have 'total' key"
        
        # Verify test data
        problem_list = problems['problems']
        assert len(problem_list) > 0, "Should have at least one problem"
        
        # Find the Two Sum problem
        two_sum = next((p for p in problem_list if p['title'] == 'Two Sum'), None)
        assert two_sum is not None, "Should find Two Sum problem"
        assert two_sum['difficulty'] == 'Easy'
        assert 'Arrays' in two_sum['topics']
        
        db.close()
        
    except Exception as e:
        pytest.fail(f"Database test failed: {str(e)}")
