import sqlite3

def migrate_titles():
    """Add leetcode_id to the beginning of each problem title"""
    print("Starting title migration...")
    
    with sqlite3.connect('leetcode.db') as conn:
        cursor = conn.cursor()
        
        # First get all problems
        cursor.execute('SELECT id, leetcode_id, title FROM problems')
        problems = cursor.fetchall()
        
        # Update each problem's title to include the ID
        for problem_id, leetcode_id, title in problems:
            # Skip if title already starts with the ID
            if title.startswith(f"{leetcode_id}."):
                continue
                
            new_title = f"{leetcode_id}. {title}"
            cursor.execute('''
                UPDATE problems 
                SET title = ? 
                WHERE id = ?
            ''', (new_title, problem_id))
        
        conn.commit()
        print(f"Updated {len(problems)} problem titles")

if __name__ == '__main__':
    migrate_titles()
