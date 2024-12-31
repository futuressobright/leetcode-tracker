import sqlite3

def fix_dates():
    with sqlite3.connect('leetcode.db') as db:
        # First, let's see what we have
        attempts = db.execute('SELECT id, next_review FROM attempts').fetchall()
        print(f"Found {len(attempts)} attempts to fix")
        
        # For each attempt that has the old format
        for attempt_id, next_review in attempts:
            if isinstance(next_review, str) and "date('now'" in next_review:
                # Extract the days number
                days = next_review.split("+")[1].split()[0]
                # Create proper date
                db.execute('''
                    UPDATE attempts 
                    SET next_review = date('now', '+' || ? || ' days')
                    WHERE id = ?
                ''', (days, attempt_id))
        
        db.commit()
        print("Database updated!")

if __name__ == "__main__":
    fix_dates()
