# tests/test_concurrent.py
import pytest
from threading import Thread
import queue

def test_concurrent_database_access(test_db_path):
    """Test concurrent database access safety"""
    db = Database(test_db_path)
    errors = queue.Queue()
    NUM_THREADS = 10
    
    def worker():
        try:
            # Try to read problems
            problems = db.get_problems()
            assert isinstance(problems, dict)
            assert 'problems' in problems
            
            # Try to toggle a list
            conn = db.get_connection()
            problem_id = conn.execute('SELECT id FROM problems LIMIT 1').fetchone()['id']
            db.toggle_list(problem_id, 1)
            
        except Exception as e:
            errors.put(e)
    
    threads = []
    for _ in range(NUM_THREADS):
        thread = Thread(target=worker)
        thread.start()
        threads.append(thread)
    
    for thread in threads:
        thread.join()
    
    # Check if any errors occurred
    error_list = []
    while not errors.empty():
        error_list.append(errors.get())
    
    assert len(error_list) == 0, f"Encountered errors during concurrent access: {error_list}"

def test_concurrent_web_access(test_client):
    """Test concurrent web access safety"""
    errors = queue.Queue()
    NUM_THREADS = 10
    
    def worker():
        try:
            # Test main page access
            response = test_client.get('/')
            assert response.status_code == 200
            
            # Test search
            response = test_client.get('/?search=test')
            assert response.status_code == 200
            
            # Test never attempted filter
            response = test_client.get('/?never_attempted=true')
            assert response.status_code == 200
            
        except Exception as e:
            errors.put(e)
    
    threads = []
    for _ in range(NUM_THREADS):
        thread = Thread(target=worker)
        thread.start()
        threads.append(thread)
    
    for thread in threads:
        thread.join()
    
    # Check if any errors occurred
    error_list = []
    while not errors.empty():
        error_list.append(errors.get())
    
    assert len(error_list) == 0, f"Encountered errors during concurrent access: {error_list}"
