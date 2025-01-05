# tests/test_toggle_realistic.py
from database import Database
import time

def test_toggle_list_realistic(test_client, test_db_path):
    """Test toggle list functionality with realistic usage patterns"""
    db = Database(test_db_path)
    conn = db.get_connection()
    
    # First verify our test database structure
    print("\nDatabase tables:")
    tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
    for table in tables:
        print(f"- {table['name']}")
        
    # Add several test problems
    problems = [
        ('123', 'Test Problem 1', 'Easy', 'Arrays'),
        ('456', 'Test Problem 2', 'Medium', 'Strings'),
        ('789', 'Test Problem 3', 'Hard', 'Dynamic Programming')
    ]
    
    problem_ids = []
    for leetcode_id, title, difficulty, topic in problems:
        conn.execute('''
            INSERT INTO problems (leetcode_id, title, difficulty, topics) 
            VALUES (?, ?, ?, ?)
        ''', (leetcode_id, title, difficulty, topic))
        conn.commit()
        
        problem = conn.execute("SELECT id FROM problems WHERE leetcode_id = ?", 
                             [leetcode_id]).fetchone()
        problem_ids.append(problem['id'])
    
    print(f"\nCreated test problems with IDs: {problem_ids}")
    
    # Try rapid toggles like a user clicking quickly
    print("\nTesting rapid toggles:")
    for problem_id in problem_ids:
        # Toggle on
        print(f"\nToggling problem {problem_id} ON to list 1:")
        response = test_client.post(f'/toggle_list/{problem_id}/1')
        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.data}")
        
        # Quick toggle off
        print(f"\nToggling problem {problem_id} OFF from list 1:")
        response = test_client.post(f'/toggle_list/{problem_id}/1')
        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.data}")
        
        # Check final state
        result = conn.execute('''
            SELECT * FROM problem_lists 
            WHERE problem_id = ? AND list_id = 1
        ''', [problem_id]).fetchone()
        print(f"Final database state for problem {problem_id}:", result)
        
    # Try toggling between different lists
    print("\nTesting list switches:")
    problem_id = problem_ids[0]
    
    # Add to list 1
    response = test_client.post(f'/toggle_list/{problem_id}/1')
    print(f"\nAdded to list 1 - status: {response.status_code}")
    
    # Quickly add to list 2
    response = test_client.post(f'/toggle_list/{problem_id}/2')
    print(f"Added to list 2 - status: {response.status_code}")
    
    # Check final state
    results = conn.execute('''
        SELECT list_id FROM problem_lists 
        WHERE problem_id = ?
        ORDER BY list_id
    ''', [problem_id]).fetchall()
    print(f"\nFinal lists for problem {problem_id}:", [r['list_id'] for r in results])
    
    # All responses should be successful
    assert all(r.status_code in [200, 204] for r in [response]), \
           "Some toggle operations failed"
