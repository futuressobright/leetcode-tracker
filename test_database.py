# tests/test_database.py
import pytest
from datetime import datetime, date

def test_get_problems(db):
    """Test basic problem retrieval"""
    problems = db.get_problems()
    assert len(problems) == 2
    assert problems[0]['leetcode_id'] == '1'
    assert problems[1]['leetcode_id'] == '2'

def test_problem_search(db):
    """Test problem search functionality"""
    problems = db.get_problems(search='Test Problem 1')
    assert len(problems) == 1
    assert problems[0]['title'] == 'Test Problem 1'

def test_topic_filter(db):
    """Test filtering by topic"""
    problems = db.get_problems(topic_filter='Arrays')
    assert len(problems) == 1
    assert 'Arrays' in problems[0]['topics']

def test_log_attempt(db):
    """Test logging an attempt"""
    db.log_attempt(1, 'Medium', 'Test notes', 7)
    
    history = db.get_problem_history(1)
    assert len(history) == 1
    assert history[0]['comfort_level'] == 'Medium'
    assert history[0]['notes'] == 'Test notes'

def test_toggle_list(db):
    """Test adding and removing problem from list"""
    # Add to list
    db.toggle_list(1, 1)  # Add problem 1 to list 1
    problems = db.get_problems(list_filter='1')
    assert len(problems) == 1
    
    # Remove from list
    db.toggle_list(1, 1)  # Remove problem 1 from list 1
    problems = db.get_problems(list_filter='1')
    assert len(problems) == 0

def test_rename_list(db):
    """Test list renaming"""
    db.rename_list(1, 'New Name')
    lists = db.get_lists()
    assert any(l['name'] == 'New Name' for l in lists)

def test_due_problems(db):
    """Test due problems functionality"""
    # Add an attempt that's due
    db.log_attempt(1, 'Low', 'Need to review', 0)  # Due immediately
    
    due_problems = db.get_due_problems()
    assert len(due_problems) == 1
    assert due_problems[0]['leetcode_id'] == '1'
import pytest
from database import Database
from exceptions import DatabaseError, RecordNotFoundError, DatabaseConnectionError
from datetime import datetime, date, timedelta

def test_get_problems_empty_db(db):
    """Test problem retrieval with empty database"""
    # Clear the problems table
    conn = db.get_connection()
    conn.execute('DELETE FROM problems')
    conn.commit()
    
    problems = db.get_problems()
    assert len(problems) == 0



def test_invalid_list_slot(db):
    """Test handling invalid list slot numbers"""
    with pytest.raises(ValueError):
        db.rename_list(0, 'Invalid List')  # Too low
    with pytest.raises(ValueError):
        db.rename_list(6, 'Invalid List')  # Too high

def test_empty_list_name(db):
    """Test handling empty list names"""
    with pytest.raises(ValueError):
        db.rename_list(1, '')
    with pytest.raises(ValueError):
        db.rename_list(1, '   ')

def test_nonexistent_problem_attempt(db):
    """Test logging attempt for non-existent problem"""
    with pytest.raises(RecordNotFoundError):
        db.log_attempt(999, 'Medium', 'Test notes', 7)

def test_invalid_comfort_level(db):
    """Test logging attempt with invalid comfort level"""
    # First insert a valid problem
    conn = db.get_connection()
    conn.execute('''
        INSERT INTO problems (id, leetcode_id, title, difficulty, topics)
        VALUES (999, '999', 'Test Problem', 'Easy', 'Arrays')
    ''')
    conn.commit()
    
    # Now try to log with invalid comfort level
    # Note: This might need to be adjusted based on your application's validation logic
    db.log_attempt(999, 'Invalid', 'Test notes', 7)
    
    # Verify the attempt was logged with the provided comfort level
    history = db.get_problem_history(999)
    assert history[0]['comfort_level'] == 'Invalid'

def test_multiple_attempts_ordering(db):
    """Test that attempts are returned in correct order"""
    # Insert a problem
    conn = db.get_connection()
    conn.execute('''
        INSERT INTO problems (id, leetcode_id, title, difficulty, topics)
        VALUES (888, '888', 'Test Problem', 'Easy', 'Arrays')
    ''')
    
    # Log multiple attempts at different times
    base_date = datetime.now() - timedelta(days=5)
    for i in range(3):
        conn.execute('''
            INSERT INTO attempts (problem_id, comfort_level, notes, attempted_at)
            VALUES (?, ?, ?, ?)
        ''', (888, f'Medium{i}', f'Note {i}', 
              base_date + timedelta(days=i)))
    conn.commit()
    
    history = db.get_problem_history(888)
    assert len(history) == 3
    # Verify reverse chronological order
    assert history[0]['comfort_level'] == 'Medium2'
    assert history[2]['comfort_level'] == 'Medium0'

def test_get_problems_with_multiple_topics(db):
    """Test filtering problems with multiple topics"""
    conn = db.get_connection()
    conn.execute('''
        INSERT INTO problems (leetcode_id, title, difficulty, topics)
        VALUES 
            ('777', 'Multi Topic', 'Medium', 'Arrays,Dynamic Programming,Math'),
            ('778', 'Single Topic', 'Easy', 'Arrays')
    ''')
    conn.commit()
    
    problems = db.get_problems(topic_filter='Dynamic Programming')
    assert len(problems) == 1
    assert problems[0]['leetcode_id'] == '777'


def test_search_with_special_characters(db):
    """Test search functionality with special SQL characters"""
    conn = db.get_connection()
    conn.execute('''
        INSERT INTO problems (leetcode_id, title, difficulty, topics)
        VALUES ('3', 'Test% Problem', 'Easy', 'Arrays')
    ''')
    conn.commit()

    # Search for the exact '%' character
    problems = db.get_problems(search='%')
    assert len(problems) == 1
    assert problems[0]['title'] == 'Test% Problem'

    # Make sure regular search still works
    problems = db.get_problems(search='Test')
    assert len(problems) == 3  # The two default test problems plus our new one


def test_concurrent_list_operations(db):
    """Test handling concurrent list operations"""
    # Add problem to list
    db.toggle_list(1, 1)  # Add problem 1 to list 1

    # Verify it was added
    problems = db.get_problems(list_filter='1')
    assert len(problems) == 1

    # Toggle again should remove it
    db.toggle_list(1, 1)
    problems = db.get_problems(list_filter='1')
    assert len(problems) == 0  # Should be removed after second toggle

    # Toggle once more should add it back
    db.toggle_list(1, 1)
    problems = db.get_problems(list_filter='1')
    assert len(problems) == 1  # Should be back after third toggle


def test_due_problems_date_handling(db):
    """Test due problems with various date scenarios"""
    conn = db.get_connection()
    today = date.today()
    
    # Insert problem with various due dates
    problem_data = [
        (1, 'past', today - timedelta(days=5)),
        (2, 'today', today),
        (3, 'future', today + timedelta(days=5))
    ]
    
    for problem_id, status, due_date in problem_data:
        conn.execute('''
            INSERT OR REPLACE INTO problems (id, leetcode_id, title)
            VALUES (?, ?, ?)
        ''', (problem_id, str(problem_id), f'Problem {problem_id}'))
        
        conn.execute('''
            INSERT INTO attempts (problem_id, comfort_level, next_review)
            VALUES (?, ?, ?)
        ''', (problem_id, 'Medium', due_date))
    conn.commit()
    
    due_problems = db.get_due_problems()
    due_ids = [p['id'] for p in due_problems]
    
    assert 1 in due_ids  # Past due should be included
    assert 2 in due_ids  # Due today should be included
    assert 3 not in due_ids  # Future due should not be included
