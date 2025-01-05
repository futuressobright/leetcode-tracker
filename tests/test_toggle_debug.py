# tests/test_toggle_debug.py
from database import Database

def test_toggle_list_basic(test_client, test_db_path):
    """Basic test of toggle_list functionality"""
    db = Database(test_db_path)
    conn = db.get_connection()
    
    # First verify our test database structure
    print("\nDatabase tables:")
    tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
    for table in tables:
        print(f"- {table['name']}")
        columns = conn.execute(f"PRAGMA table_info({table['name']})").fetchall()
        for col in columns:
            print(f"  - {col['name']}: {col['type']}")
    
    # Check lists table content
    print("\nExisting lists:")
    lists = conn.execute("SELECT * FROM lists").fetchall()
    for lst in lists:
        print(f"- Slot {lst['slot']}: {lst['name']} (id: {lst['id']})")
    
    # Add a test problem
    conn.execute('''
        INSERT INTO problems (leetcode_id, title, difficulty, topics) 
        VALUES ('999', 'Test Toggle Problem', 'Easy', 'Testing')
    ''')
    conn.commit()
    
    # Get the problem id
    problem = conn.execute("SELECT id FROM problems WHERE leetcode_id = '999'").fetchone()
    problem_id = problem['id']
    print(f"\nTest problem id: {problem_id}")
    
    # Try to toggle it
    print("\nAttempting toggle:")
    response = test_client.post(f'/toggle_list/{problem_id}/1')
    print(f"Response status: {response.status_code}")
    print(f"Response data: {response.data}")
    
    # Check if it was added
    result = conn.execute('''
        SELECT * FROM problem_lists 
        WHERE problem_id = ?
    ''', [problem_id]).fetchone()
    
    print("\nResult in database:", result)
