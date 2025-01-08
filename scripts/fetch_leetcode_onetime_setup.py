def fetch_leetcode_problems():
    """Fetch all problems from LeetCode GraphQL API"""
    # ... (keep existing imports and setup) ...

    try:
        # ... (keep existing API call logic) ...

        # Connect to existing database
        print("Connecting to database...")
        with sqlite3.connect('leetcode.db') as conn:
            cursor = conn.cursor()
            
            # Clear existing problems
            print("Clearing existing problems...")
            cursor.execute("DELETE FROM problems")
            
            # Insert new problems
            print("Inserting problems into database...")
            for problem in all_problems:
                topics = ','.join(tag['name'] for tag in problem['topicTags'])
                # Include the ID in the title
                formatted_title = f"{problem['questionFrontendId']}. {problem['title']}"
                cursor.execute("""
                    INSERT INTO problems 
                    (leetcode_id, title, difficulty, topics)
                    VALUES (?, ?, ?, ?)
                """, (
                    problem['questionFrontendId'],
                    formatted_title,
                    problem['difficulty'],
                    topics
                ))

            conn.commit()

        print(f"Successfully imported {len(all_problems)} problems from LeetCode")
        return len(all_problems)

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        print(f"Full error details: {type(e).__name__}")
        return 0
