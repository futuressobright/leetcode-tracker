# database.py
from contextlib import contextmanager
import sqlite3
from typing import Generator, List, Optional


class Database:
    def __init__(self, db_path: str = 'leetcode.db'):
        self.db_path = db_path
        self._connection = None

    def get_connection(self):
        if self._connection is None:
            self._connection = sqlite3.connect(self.db_path)
            self._connection.row_factory = sqlite3.Row
        return self._connection

    def close(self):
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    def get_problems(self, search: Optional[str] = None,
                     list_filter: Optional[str] = None,
                     topic_filter: Optional[str] = None) -> List[sqlite3.Row]:
        """Get problems with optional filters"""
        conn = self.get_connection()

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
        if list_filter:
            base_query += '''
            WHERE EXISTS (
                SELECT 1 FROM problem_lists pl2 
                JOIN lists l2 ON pl2.list_id = l2.id 
                WHERE pl2.problem_id = p.id AND l2.slot = ?
            )'''
            params.append(list_filter)
        elif topic_filter:
            base_query += ' WHERE p.topics LIKE ?'
            params.append(f'%{topic_filter}%')
        elif search:
            base_query += ' WHERE (p.title LIKE ? OR p.topics LIKE ?)'
            params.extend([f'%{search}%', f'%{search}%'])

        base_query += ' GROUP BY p.id ORDER BY CAST(p.leetcode_id AS INTEGER)'

        try:
            return conn.execute(base_query, params).fetchall()
        except Exception as e:
            print(f"Error in get_problems: {e}")
            conn.rollback()
            raise

    def get_due_problems(self, search: Optional[str] = None,
                         list_filter: Optional[str] = None,
                         topic_filter: Optional[str] = None) -> List[sqlite3.Row]:
        """Get problems due for review with optional filters"""
        conn = self.get_connection()

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

        try:
            return conn.execute(base_query, params).fetchall()
        except Exception as e:
            print(f"Error in get_due_problems: {e}")
            conn.rollback()
            raise

    def get_lists(self) -> List[sqlite3.Row]:
        """Get all lists ordered by slot"""
        conn = self.get_connection()
        return conn.execute('SELECT * FROM lists ORDER BY slot').fetchall()

    def log_attempt(self, problem_id: int, comfort: str, notes: str, review_days: int) -> None:
        """Log a new problem attempt"""
        conn = self.get_connection()
        try:
            conn.execute('''
                INSERT INTO attempts (problem_id, comfort_level, notes, next_review)
                SELECT ?, ?, ?, date('now', '+' || ? || ' days')
                ''', (problem_id, comfort, notes, review_days))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise

    def get_problem_history(self, problem_id: int):
        """Get attempt history for a problem"""
        conn = self.get_connection()
        return conn.execute('''
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

    def toggle_list(self, problem_id: int, slot: int) -> bool:
        """Toggle a problem's presence in a list. Returns True if added, False if removed"""
        conn = self.get_connection()
        try:
            # Get list id for this slot
            list_id = conn.execute('SELECT id FROM lists WHERE slot = ?',
                                   [slot]).fetchone()
            if not list_id:
                raise ValueError("List not found")
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
        except Exception as e:
            conn.rollback()
            raise

    def rename_list(self, slot: int, name: str) -> None:
        """Rename a list"""
        if not 1 <= slot <= 5:
            raise ValueError("Invalid slot")
        if not name.strip():
            raise ValueError("Name required")

        conn = self.get_connection()
        try:
            conn.execute('''
                UPDATE lists 
                SET name = ? 
                WHERE slot = ?
            ''', (name, slot))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise