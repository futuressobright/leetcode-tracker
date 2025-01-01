from contextlib import contextmanager
import sqlite3
from typing import Generator, List, Optional
from exceptions import DatabaseError, RecordNotFoundError, DatabaseConnectionError
import logging


class Database:
    def __init__(self, db_path: str = 'leetcode.db'):
        self.db_path = db_path
        self._connection = None

    def get_connection(self):
        if self._connection is None:
            try:
                self._connection = sqlite3.connect(self.db_path)
                self._connection.row_factory = sqlite3.Row
            except sqlite3.Error as e:
                logging.error(f"Failed to connect to database at {self.db_path}: {e}")
                raise DatabaseConnectionError(f"Failed to connect to database: {e}")
        return self._connection

    def close(self):
        if self._connection is not None:
            try:
                self._connection.close()
            except sqlite3.Error as e:
                logging.error(f"Error closing database connection: {e}")
            finally:
                self._connection = None

    def get_problems(self, search: Optional[str] = None,
                     list_filter: Optional[str] = None,
                     topic_filter: Optional[str] = None,
                     page: int = 1,
                     per_page: int = 12,
                     sort_by_difficulty: Optional[str] = None,
                     never_attempted: Optional[bool] = None) -> dict:
        """Get problems with optional filters and pagination"""
        conn = self.get_connection()
        offset = (page - 1) * per_page

        try:
            # First get total count for pagination
            count_query = '''
                SELECT COUNT(DISTINCT p.id) as total
                FROM problems p
            '''

            # Your existing base query with LIMIT and OFFSET
            base_query = '''
                WITH LatestAttempts AS (
                    SELECT problem_id,
                           comfort_level,
                           next_review,
                           ROW_NUMBER() OVER (PARTITION BY problem_id ORDER BY attempted_at DESC) as rn
                    FROM attempts
                )
                SELECT 
                    p.*,
                    a.comfort_level,
                    a.next_review,
                    GROUP_CONCAT(l.name) as list_names
                FROM problems p
                LEFT JOIN LatestAttempts a ON p.id = a.problem_id AND a.rn = 1
                LEFT JOIN problem_lists pl ON p.id = pl.problem_id
                LEFT JOIN lists l ON pl.list_id = l.id
            '''

            params = []
            where_clause = ''

            if never_attempted:
                where_clause = '''
                    WHERE NOT EXISTS (
                        SELECT 1 FROM attempts a 
                        WHERE a.problem_id = p.id
                    )'''
            elif list_filter:
                where_clause = '''
                    WHERE EXISTS (
                        SELECT 1 FROM problem_lists pl2 
                        JOIN lists l2 ON pl2.list_id = l2.id 
                        WHERE pl2.problem_id = p.id AND l2.slot = ?
                    )'''
                params.append(list_filter)
            elif topic_filter:
                where_clause = ' WHERE p.topics LIKE ?'
                params.append(f'%{topic_filter}%')
            elif search:
                where_clause = ' WHERE (p.title LIKE ? OR p.topics LIKE ?)'
                params.extend([f'%{search}%', f'%{search}%'])

            # Add where clause to count query if needed
            if where_clause:
                count_query += where_clause

            # Get total count
            total = conn.execute(count_query, params).fetchone()['total']

            # Add pagination to main query
            # Add pagination to main query
            base_query += where_clause + ' GROUP BY p.id'

            # Add difficulty sorting
            if sort_by_difficulty == 'asc':
                base_query += ''' ORDER BY 
                                CASE p.difficulty 
                                    WHEN 'Easy' THEN 1 
                                    WHEN 'Medium' THEN 2 
                                    WHEN 'Hard' THEN 3 
                                    ELSE 4 
                                END'''
            elif sort_by_difficulty == 'desc':
                base_query += ''' ORDER BY 
                                CASE p.difficulty 
                                    WHEN 'Hard' THEN 1 
                                    WHEN 'Medium' THEN 2 
                                    WHEN 'Easy' THEN 3 
                                    ELSE 4 
                                END'''
            else:
                base_query += ' ORDER BY CAST(p.leetcode_id AS INTEGER)'

            base_query += ' LIMIT ? OFFSET ?'

            params.extend([per_page, offset])

            problems = conn.execute(base_query, params).fetchall()

            # Convert each SQLite Row to a dict to preserve attribute access
            problem_dicts = [dict(row) for row in problems]

            return {
                'problems': problem_dicts,  # Now sending list of dicts instead of Row objects
                'total': total,
                'page': page,
                'per_page': per_page,
                'total_pages': (total + per_page - 1) // per_page
            }

        except sqlite3.Error as e:
            logging.error(f"Error fetching problems: {e}")
            conn.rollback()
            raise DatabaseError(f"Failed to fetch problems: {e}")







    def get_due_problems(self, search: Optional[str] = None,
                         list_filter: Optional[str] = None,
                         topic_filter: Optional[str] = None) -> List[sqlite3.Row]:
        """Get problems due for review with optional filters"""
        conn = self.get_connection()

        try:
            base_query = '''
                WITH LatestAttempts AS (
                    SELECT problem_id,
                           comfort_level,
                           next_review,
                           ROW_NUMBER() OVER (PARTITION BY problem_id ORDER BY attempted_at DESC) as rn
                    FROM attempts
                )
                SELECT 
                    p.*,
                    a.comfort_level,
                    a.next_review,
                    GROUP_CONCAT(l.name) as list_names
                FROM problems p
                LEFT JOIN LatestAttempts a ON p.id = a.problem_id AND a.rn = 1
                LEFT JOIN problem_lists pl ON p.id = pl.problem_id
                LEFT JOIN lists l ON pl.list_id = l.id
                WHERE a.next_review IS NOT NULL 
                AND date(a.next_review) <= date('now')
            '''

            params = []
            if list_filter:
                base_query += '''
                AND EXISTS (
                    SELECT 1 FROM problem_lists pl2 
                    JOIN lists l2 ON pl2.list_id = l2.id 
                    WHERE pl2.problem_id = p.id AND l2.slot = ?
                )'''
                params.append(list_filter)
            elif topic_filter:
                base_query += ' AND p.topics LIKE ?'
                params.append(f'%{topic_filter}%')
            elif search:
                base_query += ' AND (p.title LIKE ? OR p.topics LIKE ?)'
                params.extend([f'%{search}%', f'%{search}%'])

            base_query += ' GROUP BY p.id ORDER BY a.next_review ASC'

            return conn.execute(base_query, params).fetchall()
        except sqlite3.Error as e:
            logging.error(f"Error fetching due problems: {e}")
            conn.rollback()
            raise DatabaseError(f"Failed to fetch due problems: {e}")

    def get_lists(self) -> List[sqlite3.Row]:
        """Get all lists ordered by slot"""
        conn = self.get_connection()
        try:
            return conn.execute('SELECT * FROM lists ORDER BY slot').fetchall()
        except sqlite3.Error as e:
            logging.error(f"Error fetching lists: {e}")
            raise DatabaseError(f"Failed to fetch lists: {e}")

    def log_attempt(self, problem_id: int, comfort: str, notes: str, review_days: int) -> None:
        """Log a new problem attempt"""
        conn = self.get_connection()
        try:
            # First verify the problem exists
            problem = conn.execute('SELECT 1 FROM problems WHERE id = ?', [problem_id]).fetchone()
            if not problem:
                raise RecordNotFoundError(f"Problem with id {problem_id} not found")

            conn.execute('''
                INSERT INTO attempts (problem_id, comfort_level, notes, next_review)
                SELECT ?, ?, ?, date('now', '+' || ? || ' days')
                ''', (problem_id, comfort, notes, review_days))
            conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Error logging attempt: {e}")
            conn.rollback()
            raise DatabaseError(f"Failed to log attempt: {e}")

    def get_problem_history(self, problem_id: int):
        """Get attempt history for a problem"""
        conn = self.get_connection()
        try:
            attempts = conn.execute('''
                SELECT 
                    a.comfort_level,
                    a.notes,
                    a.next_review,
                    datetime(a.attempted_at) as attempted_at,
                    p.title,
                    CAST(p.leetcode_id AS TEXT) as leetcode_id
                FROM attempts a
                JOIN problems p ON a.problem_id = p.id
                WHERE a.problem_id = ?
                ORDER BY a.attempted_at DESC
            ''', [problem_id]).fetchall()

            if not attempts:
                raise RecordNotFoundError(f"No history found for problem {problem_id}")
            return attempts
        except sqlite3.Error as e:
            logging.error(f"Error fetching problem history: {e}")
            raise DatabaseError(f"Failed to fetch problem history: {e}")

    def toggle_list(self, problem_id: int, slot: int) -> bool:
        """Toggle a problem's presence in a list. Returns True if added, False if removed"""
        conn = self.get_connection()
        try:
            # Verify the problem exists
            problem = conn.execute('SELECT 1 FROM problems WHERE id = ?', [problem_id]).fetchone()
            if not problem:
                raise RecordNotFoundError(f"Problem with id {problem_id} not found")

            # Get list id for this slot
            list_id = conn.execute('SELECT id FROM lists WHERE slot = ?', [slot]).fetchone()
            if not list_id:
                raise RecordNotFoundError(f"List with slot {slot} not found")
            list_id = list_id[0]

            # Check if problem is in list
            exists = conn.execute('''
                SELECT 1 FROM problem_lists 
                WHERE problem_id = ? AND list_id = ?
            ''', [problem_id, list_id]).fetchone()

            if exists:
                conn.execute('''
                    DELETE FROM problem_lists 
                    WHERE problem_id = ? AND list_id = ?
                ''', [problem_id, list_id])
                result = False
            else:
                conn.execute('''
                    INSERT INTO problem_lists (problem_id, list_id)
                    VALUES (?, ?)
                ''', [problem_id, list_id])
                result = True

            conn.commit()
            return result
        except sqlite3.Error as e:
            logging.error(f"Error toggling list: {e}")
            conn.rollback()
            raise DatabaseError(f"Failed to toggle list: {e}")

    def rename_list(self, slot: int, name: str) -> None:
        """Rename a list"""
        if not 1 <= slot <= 5:
            raise ValueError("Invalid slot number")
        if not name.strip():
            raise ValueError("Name cannot be empty")

        conn = self.get_connection()
        try:
            result = conn.execute('SELECT 1 FROM lists WHERE slot = ?', [slot]).fetchone()
            if not result:
                raise RecordNotFoundError(f"List with slot {slot} not found")

            conn.execute('''
                UPDATE lists 
                SET name = ? 
                WHERE slot = ?
            ''', (name, slot))
            conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Error renaming list: {e}")
            conn.rollback()
            raise DatabaseError(f"Failed to rename list: {e}")