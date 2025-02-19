from flask import Flask, render_template, request, redirect, flash, g
import sqlite3
from datetime import datetime, date
from comfort_config import COMFORT_LEVELS
import os
from database import Database
from dotenv import load_dotenv
load_dotenv()  # take environment variables from .env

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
    import time
    start_total = time.time()

    db = get_db()
    search = request.args.get('search', '').strip()
    list_filter = request.args.get('list')
    topic_filter = request.args.get('topic', '').strip()
    sort_by_difficulty = request.args.get('difficulty_sort')
    never_attempted = request.args.get('never_attempted') == 'true'

    page = request.args.get('page', 1, type=int)
    per_page = 12

    try:
        start_query = time.time()
        problems_data = db.get_problems(search, list_filter, topic_filter, page, per_page, sort_by_difficulty)
        all_problems = problems_data['problems']

        # Filter never attempted problems in memory if requested
        # Handle never attempted problems
        # Handle never attempted problems
        if never_attempted:
            # First get ALL never attempted problems before pagination
            all_never_attempted = db.get_problems(
                search=search,
                list_filter=list_filter,
                topic_filter=topic_filter,
                page=1,
                per_page=9999999,  # Large number to get all problems
                sort_by_difficulty=sort_by_difficulty
            )['problems']

            # Filter for never attempted
            filtered_problems = [p for p in all_never_attempted if not p.get('comfort_level')]
            total_filtered = len(filtered_problems)

            # Then apply pagination
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page

            problems_data.update({
                'problems': filtered_problems[start_idx:end_idx],
                'total': total_filtered,
                'total_pages': (total_filtered + per_page - 1) // per_page,
                'page': page
            })
            all_problems = problems_data['problems']



        # Only get due problems if not in never_attempted mode
        start_due = time.time()  # Moved this before the if statement
        due_problems = [] if never_attempted else db.get_due_problems(search, list_filter, topic_filter)

        start_lists = time.time()
        lists = [dict(row) for row in db.get_lists()]

        start_render = time.time()

        # For AJAX "Load More" requests, just return problem cards
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            html = ''
            for problem in all_problems:
                html += render_template('partials/problem_card.html',
                                        problem=problem,
                                        lists=db.get_lists())
            return html



        if list_filter is not None:
            list_filter = str(list_filter)

        due_problem_ids = {p['id'] for p in due_problems}
        filtered_problems = [p for p in all_problems if p['id'] not in due_problem_ids]

        response = render_template('index.html',
                                   lists=lists,
                                   due_problems=due_problems,
                                   all_problems=filtered_problems,
                                   pagination=problems_data,
                                   search=search,
                                   list_filter=list_filter,
                                   topic=topic_filter,
                                   today=date.today().isoformat())


        return response

    except Exception as e:
        flash(f"Error loading problems: {str(e)}")
        return render_template('index.html',
                               lists=[],
                               due_problems=[],
                               all_problems=[],
                               pagination={'page': 1, 'total_pages': 1},
                               search=search,
                               topic=topic_filter,
                               today=date.today().isoformat())


@app.route('/log_attempt/<int:problem_id>', methods=['POST'])
def log_attempt(problem_id):

    comfort = request.form['comfort']
    notes = request.form.get('notes', '')

    try:
        db = get_db()
        review_days = COMFORT_LEVELS[comfort]['review_days']
        db.log_attempt(problem_id, comfort, notes, review_days)
        return redirect('/')
    except Exception as e:
        flash(f"Error logging attempt: {str(e)}")
        return redirect('/')


@app.route('/history/<int:problem_id>')
def problem_history(problem_id):
    db = get_db()
    try:
        problem = db.get_connection().execute(
            'SELECT title, leetcode_id FROM problems WHERE id = ?',
            [problem_id]
        ).fetchone()

        if not problem:
            return render_template('error.html',
                                   error_title="Problem Not Found",
                                   error_message="This problem could not be found.")

        attempts = db.get_problem_history(problem_id)

        problem_info = {
            'title': problem['title'],
            'leetcode_id': problem['leetcode_id'],
            'attempts': [{
                'comfort_level': a['comfort_level'],
                'notes': a['notes'],
                'next_review': a['next_review'],
                'attempted_at': a['attempted_at']
            } for a in attempts] if attempts else []
        }

        if not attempts:
            return render_template('error.html',
                                   error_title="No History",
                                   error_message="No attempts recorded for this problem yet. Try solving it first!")

        return render_template('history.html', problem=problem_info)
    except Exception as e:
        return render_template('error.html',
                               error_title="Error",
                               error_message=f"Could not retrieve problem history: {str(e)}")


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


@app.route('/add_to_list/<int:problem_id>', methods=['POST'])
def add_to_list(problem_id):
    try:
        list_name = request.form['list_name']
        slot = int(list_name.split()[-1]) if list_name != 'Quick50' else 1

        db = get_db()
        db.toggle_list(problem_id, slot)

        # Get the current list from the referer URL
        referer = request.headers.get('Referer')
        if referer and 'list=' in referer:
            list_param = referer.split('list=')[1].split('&')[0]
            return redirect(f'/?list={list_param}')
        return redirect('/')
    except Exception as e:
        flash(f"Error modifying list: {str(e)}")
        return redirect('/')

if __name__ == '__main__':
    host = '0.0.0.0' if os.environ.get('ALLOW_REMOTE') else '127.0.0.1'
    app.run(debug=True, host=host, port=5001)


