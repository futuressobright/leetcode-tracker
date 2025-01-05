# tests/test_user_simulation.py
import pytest
import threading
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from database import Database

class UserSimulator:
    def __init__(self, client, user_id):
        self.client = client
        self.user_id = user_id
        self.actions_performed = []
        self.errors_encountered = []

    def random_action(self):
        """Perform a random user action"""
        actions = [
            self.view_problems,
            self.search_problems,
            self.log_attempt,
            self.toggle_list,
            self.view_history
        ]
        action = random.choice(actions)
        try:
            action()
        except Exception as e:
            self.errors_encountered.append((action.__name__, str(e)))

    def view_problems(self):
        """Simulate viewing problems page with different filters"""
        filters = [
            '/',
            '/?difficulty_sort=asc',
            '/?difficulty_sort=desc',
            '/?never_attempted=true',
            '/?search=Array'
        ]
        response = self.client.get(random.choice(filters))
        assert response.status_code == 200
        self.actions_performed.append(('view', response.status_code))

    def search_problems(self):
        """Simulate searching for problems"""
        search_terms = ['Two Sum', 'Array', 'Easy', 'Hard', 'List']
        response = self.client.get(f'/?search={random.choice(search_terms)}')
        assert response.status_code == 200
        self.actions_performed.append(('search', response.status_code))

    def log_attempt(self):
        """Simulate logging an attempt"""
        comfort_levels = ['Low', 'Medium', 'High']
        response = self.client.post(f'/log_attempt/1', data={
            'comfort': random.choice(comfort_levels),
            'notes': f'Test attempt by user {self.user_id}'
        })
        assert response.status_code in [200, 302]
        self.actions_performed.append(('log_attempt', response.status_code))

    def toggle_list(self):
        """Simulate adding/removing from lists"""
        response = self.client.post(f'/toggle_list/1/{random.randint(1, 5)}')
        assert response.status_code in [200, 204]
        self.actions_performed.append(('toggle_list', response.status_code))

    def view_history(self):
        """Simulate viewing problem history"""
        response = self.client.get('/history/1')
        assert response.status_code == 200
        self.actions_performed.append(('history', response.status_code))

def verify_database_consistency(db):
    """Verify database is in a consistent state"""
    try:
        # Check problems exist
        problems = db.get_problems()
        assert problems['total'] > 0, "No problems found"

        # Verify list assignments
        for problem in problems['problems']:
            # Get lists for this problem
            problem_lists = db.get_connection().execute(
                'SELECT DISTINCT list_id FROM problem_lists WHERE problem_id = ?',
                [problem['id']]
            ).fetchall()
            
            # Verify no duplicate list assignments
            list_ids = [l[0] for l in problem_lists]
            assert len(list_ids) == len(set(list_ids)), "Duplicate list assignments found"

        # Verify attempts are properly linked
        attempts = db.get_connection().execute(
            'SELECT problem_id FROM attempts'
        ).fetchall()
        for attempt in attempts:
            # Verify problem exists for each attempt
            problem = db.get_connection().execute(
                'SELECT 1 FROM problems WHERE id = ?',
                [attempt[0]]
            ).fetchone()
            assert problem is not None, f"Orphaned attempt found for problem_id {attempt[0]}"

        return True
    except Exception as e:
        print(f"Consistency check failed: {e}")
        return False

def test_concurrent_users(init_database, test_db_path, test_client):
    """Test multiple users using the system concurrently"""
    NUM_USERS = 10
    ACTIONS_PER_USER = 20
    
    db = Database(test_db_path)
    simulators = []
    
    # Create user simulators
    for i in range(NUM_USERS):
        simulator = UserSimulator(test_client, i)
        simulators.append(simulator)
    
    # Run user actions concurrently
    with ThreadPoolExecutor(max_workers=NUM_USERS) as executor:
        futures = []
        for simulator in simulators:
            for _ in range(ACTIONS_PER_USER):
                futures.append(executor.submit(simulator.random_action))
        
        # Wait for all actions to complete
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Action failed: {e}")
    
    # Verify final database state
    assert verify_database_consistency(db), "Database inconsistency detected"
    
    # Report statistics
    total_actions = sum(len(s.actions_performed) for s in simulators)
    total_errors = sum(len(s.errors_encountered) for s in simulators)
    success_rate = (total_actions - total_errors) / total_actions * 100
    
    print(f"\nSimulation Statistics:")
    print(f"Total actions performed: {total_actions}")
    print(f"Total errors encountered: {total_errors}")
    print(f"Success rate: {success_rate:.2f}%")
    
    # Additional verification
    for simulator in simulators:
        if simulator.errors_encountered:
            print(f"\nUser {simulator.user_id} encountered errors:")
            for action, error in simulator.errors_encountered:
                print(f"  - {action}: {error}")

    assert total_errors == 0, f"Encountered {total_errors} errors during simulation"
