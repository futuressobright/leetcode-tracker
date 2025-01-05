# tests/test_list_toggle.py
import pytest

def test_toggle_list_endpoint(test_client, test_db_path):
    """Test the toggle_list endpoint in isolation"""
    # First, verify the problem and list exist
    db = Database(test_db_path)
    
    # Add a test problem if needed
    conn = db.get_connection()
    conn.execute('''
        INSERT INTO problems (leetcode_id, title, difficulty, topics) 
        VALUES ('1', 'Test Problem', 'Easy', 'Test')
    ''')
    conn.commit()
    
    # Get the problem ID
    problem = conn.execute('SELECT id FROM problems WHERE leetcode_id = ?', ['1']).fetchone()
    problem_id = problem['id']
    
    # Test adding to list
    response = test_client.post(f'/toggle_list/{problem_id}/1')
    assert response.status_code in [200, 204]
    
    # Verify it was added
    list_assignment = conn.execute('''
        SELECT 1 FROM problem_lists 
        WHERE problem_id = ? AND list_id = ?
    ''', [problem_id, 1]).fetchone()
    assert list_assignment is not None
    
    # Test removing from list
    response = test_client.post(f'/toggle_list/{problem_id}/1')
    assert response.status_code in [200, 204]
    
    # Verify it was removed
    list_assignment = conn.execute('''
        SELECT 1 FROM problem_lists 
        WHERE problem_id = ? AND list_id = ?
    ''', [problem_id, 1]).fetchone()
    assert list_assignment is None
