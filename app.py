from flask import Flask, render_template, request, redirect, flash
import sqlite3
from datetime import datetime, date
from comfort_config import COMFORT_LEVELS


app = Flask(__name__)
app.jinja_env.auto_reload = True
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.secret_key = 'dev'  # Required for flash messages
app.jinja_env.globals['COMFORT_LEVELS'] = COMFORT_LEVELS


def get_db():
    db = sqlite3.connect('leetcode.db')
    db.row_factory = sqlite3.Row
    return db


@app.route('/')
def index():
    from datetime import date
    db = get_db()
    search = request.args.get('search', '').strip()
    list_filter = request.args.get('list')
    topic_filter = request.args.get('topic', '').strip()  # New parameter

    # Get latest attempt for each problem
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
    elif topic_filter:  # Only apply if no list filter
        base_query += ' WHERE p.topics LIKE ?'
        params.append(f'%{topic_filter}%')
    elif search:  # Only apply if no list or topic filter
        base_query += ' WHERE (p.title LIKE ? OR p.topics LIKE ?)'
        params.extend([f'%{search}%', f'%{search}%'])

    base_query += ' GROUP BY p.id ORDER BY CAST(p.leetcode_id AS INTEGER)'
    all_problems = db.execute(base_query, params).fetchall()

    # For due problems, modify the query correctly
    due_base_query = base_query.replace('ORDER BY CAST(p.leetcode_id AS INTEGER)', '')
    due_query = due_base_query + ' AND a.next_review IS NOT NULL AND date(a.next_review) <= date("now")'
    due_problems = db.execute(due_query + ' ORDER BY a.next_review ASC', params).fetchall()

    lists = db.execute('SELECT * FROM lists ORDER BY slot').fetchall()
    return render_template('index.html',
                         lists=lists,
                         due_problems=due_problems,
                         all_problems=all_problems,
                         search=search,
                         topic=topic_filter,  # Pass topic to template
                         today=date.today().isoformat())



@app.route('/log_attempt/<int:problem_id>', methods=['POST'])
def log_attempt(problem_id):
    comfort = request.form['comfort']
    notes = request.form.get('notes', '')

    db = get_db()

    # Execute an insert with the date calculation done by SQLite
    db.execute('''
        INSERT INTO attempts (problem_id, comfort_level, notes, next_review)
        SELECT 
            ?,
            ?,
            ?,
            date('now', '+' || ? || ' days')
        ''', (problem_id, comfort, notes, COMFORT_LEVELS[comfort]['review_days']))
    db.commit()

    return redirect('/')


@app.route('/history/<int:problem_id>')
def problem_history(problem_id):
    db = get_db()
    attempts = db.execute('''
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
        return "No attempts found for this problem", 404

    # Debug prints
    print("\nDEBUG DATA:")
    first_attempt = dict(attempts[0])
    print("Next review date:", first_attempt.get('next_review'))

    problem_info = {
        'title': attempts[0]['title'],
        'leetcode_id': attempts[0]['leetcode_id'],
        'attempts': [{
            'comfort_level': a['comfort_level'],
            'notes': a['notes'],
            'next_review': a['next_review'],
            'attempted_at': a['attempted_at']
        } for a in attempts]
    }

    return render_template('history.html', problem=problem_info)





@app.route('/toggle_list/<int:problem_id>/<int:slot>', methods=['POST'])
def toggle_list(problem_id, slot):
    db = get_db()

    # Get list id for this slot
    list_id = db.execute('SELECT id FROM lists WHERE slot = ?', [slot]).fetchone()
    if not list_id:
        return "List not found", 404
    list_id = list_id[0]

    # Check if problem is in list
    exists = db.execute('''
        SELECT 1 FROM problem_lists 
        WHERE problem_id = ? AND list_id = ?
    ''', [problem_id, list_id]).fetchone()

    print(f"Toggle list - Problem: {problem_id}, Slot: {slot}, List ID: {list_id}, Exists: {exists is not None}")

    if exists:
        # Remove from list
        db.execute('''
            DELETE FROM problem_lists 
            WHERE problem_id = ? AND list_id = ?
        ''', [problem_id, list_id])
    else:
        # Add to list
        db.execute('''
            INSERT INTO problem_lists (problem_id, list_id)
            VALUES (?, ?)
        ''', [problem_id, list_id])

    db.commit()
    return "", 204  # Success, no content response


@app.route('/rename_list/<int:slot>', methods=['POST'])
def rename_list(slot):
    if not 1 <= slot <= 5:
        return "Invalid slot", 400

    name = request.form['name'].strip()
    if not name:
        return "Name required", 400

    db = get_db()
    db.execute('''
        UPDATE lists 
        SET name = ? 
        WHERE slot = ?
    ''', (name, slot))
    print(f"Updated list {slot} to name: {name}")  # Add this one line
    db.commit()

    return redirect('/')



import os
if __name__ == '__main__':
    host = '0.0.0.0' if os.environ.get('ALLOW_REMOTE') else '127.0.0.1'
    app.run(debug=True, host=host, port=5001)