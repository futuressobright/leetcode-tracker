from flask import Flask, render_template, request, redirect, flash, g
import sqlite3
from datetime import datetime, date
from comfort_config import COMFORT_LEVELS
import os
from database import Database

app = Flask(__name__)
app.jinja_env.auto_reload = True
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.secret_key = 'dev'
app.jinja_env.globals['COMFORT_LEVELS'] = COMFORT_LEVELS


def get_db():
    if not hasattr(g, 'db'):
        g.db = Database()
    return g.db


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'db'):
        g.db.close()


@app.route('/')
def index():
    db = get_db()
    search = request.args.get('search', '').strip()
    list_filter = request.args.get('list')
    topic_filter = request.args.get('topic', '').strip()

    try:
        all_problems = db.get_problems(search, list_filter, topic_filter)
        due_problems = db.get_due_problems(search, list_filter, topic_filter)
        lists = db.get_lists()

        return render_template('index.html',
                               lists=lists,
                               due_problems=due_problems,
                               all_problems=all_problems,
                               search=search,
                               topic=topic_filter,
                               today=date.today().isoformat())
    except Exception as e:
        print(f"Error in index route: {str(e)}")  # Debug print
        flash(f"Error loading problems: {str(e)}")
        return render_template('index.html',
                               lists=[],
                               due_problems=[],
                               all_problems=[],
                               search=search,
                               topic=topic_filter,
                               today=date.today().isoformat())


@app.route('/log_attempt/<int:problem_id>', methods=['POST'])
def log_attempt(problem_id):
    comfort = request.form['comfort']
    notes = request.form.get('notes', '')

    try:
        db = get_db()
        db.log_attempt(problem_id, comfort, notes,
                       COMFORT_LEVELS[comfort]['review_days'])
        return redirect('/')
    except Exception as e:
        flash(f"Error logging attempt: {str(e)}")
        return redirect('/')


@app.route('/history/<int:problem_id>')
def problem_history(problem_id):
    db = get_db()
    try:
        attempts = db.get_problem_history(problem_id)

        if not attempts:
            return "No attempts found for this problem", 404

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
    except Exception as e:
        flash(f"Error getting problem history: {str(e)}")
        return redirect('/')


@app.route('/toggle_list/<int:problem_id>/<int:slot>', methods=['POST'])
def toggle_list(problem_id, slot):
    try:
        db = get_db()
        was_added = db.toggle_list(problem_id, slot)
        return "", 204
    except Exception as e:
        return str(e), 400


@app.route('/rename_list/<int:slot>', methods=['POST'])
def rename_list(slot):
    name = request.form['name'].strip()
    try:
        db = get_db()
        db.rename_list(slot, name)
        return redirect('/')
    except ValueError as e:
        return str(e), 400
    except Exception as e:
        flash(f"Error renaming list: {str(e)}")
        return redirect('/')


if __name__ == '__main__':
    host = '0.0.0.0' if os.environ.get('ALLOW_REMOTE') else '127.0.0.1'
    app.run(debug=True, host=host, port=5001)