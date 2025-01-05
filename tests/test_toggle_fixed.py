# tests/test_toggle_fixed.py
from database import Database
import time

def test_toggle_list_fixed(test_client, test_db_path):
    """Test toggle list functionality with proper database initialization"""
    print(f"\nUsing test database at: {test_db_path}")
    
    # Ensure app uses the same database
    test_client.application.config['DATABASE'] = test_db_path
    
    db = Database(test_db_path)
    conn = db.get_connection()
    
    print("\nInitial data:")
    problems = conn.execute("SELECT * FROM problems").fetchall()
    print(f"- {len(problems)} problems")
    lists = conn.execute("SELECT * FROM lists").fetchall()
    print(f"- {len(lists)} lists")
    
    # Add a test problem and get its ID
    conn.execute('''
        INSERT INTO problems (leetcode_id, title, difficulty, topics) 
        VALUES (?, ?, ?, ?)
    ''', ('123', 'Test Problem', 'Easy', 'Arrays'))
    conn.commit()
    
    problem = conn.execute("SELECT id FROM problems WHERE leetcode_id = '123'").fetchone()
    problem_id = problem['id']
    print(f"\nCreated test problem with ID: {problem_id}")
    
    # Verify the problem exists
    exists = conn.execute("SELECT 1 FROM problems WHERE id = ?", [problem_id]).fetchone()
    print(f"Problem exists in DB: {exists is not None}")
    
    # Try to toggle it
    print("\nToggling problem to list 1...")
    response = test_client.post(f'/toggle_list/{problem_id}/1')
    print(f"Toggle ON response - status: {response.status_code}, data: {response.data}")
    
    # Check if it was added
    current = conn.execute('''
        SELECT * FROM problem_lists 
        WHERE problem_id = ? AND list_id = 1
    ''', [problem_id]).fetchone()
    print(f"After toggle ON - in database: {current is not None}")
    
    # Toggle it off
    print("\nToggling problem off list 1...")
    response = test_client.post(f'/toggle_list/{problem_id}/1')
    print(f"Toggle OFF response - status: {response.status_code}, data: {response.data}")
    
    # Check if it was removed
    current = conn.execute('''
        SELECT * FROM problem_lists 
        WHERE problem_id = ? AND list_id = 1
    ''', [problem_id]).fetchone()
    print(f"After toggle OFF - in database: {current is not None}")
    
    assert response.status_code in [200, 204], f"Toggle failed with status {response.status_code}"
