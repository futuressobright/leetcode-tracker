import requests
import json
import sqlite3
from datetime import datetime


def fetch_leetcode_problems():
    """Fetch all problems from LeetCode GraphQL API"""
    url = 'https://leetcode.com/graphql'

    # Updated query to match current LeetCode GraphQL schema
    query = """
    query problemsetQuestionList($categorySlug: String, $limit: Int, $skip: Int, $filters: QuestionListFilterInput) {
        problemsetQuestionList: questionList(
            categorySlug: $categorySlug
            limit: $limit
            skip: $skip
            filters: $filters
        ) {
            total: totalNum
            questions: data {
                questionId
                title
                titleSlug
                difficulty
                topicTags {
                    name
                    slug
                }
            }
        }
    }
    """

    print("Fetching problems from LeetCode API...")
    all_problems = []
    skip = 0
    limit = 100

    try:
        # First request to get total number of problems
        response = requests.post(url, json={
            'query': query,
            'variables': {
                'categorySlug': "",
                'limit': limit,
                'skip': skip,
                'filters': {}
            }
        })

        print("Response status:", response.status_code)
        data = response.json()

        if 'errors' in data:
            print("API Errors:", data['errors'])
            return 0

        total_problems = data['data']['problemsetQuestionList']['total']
        print(f"Total problems to fetch: {total_problems}")

        # Fetch all problems in batches
        while skip < total_problems:
            print(f"Fetching problems {skip} to {skip + limit}...")
            response = requests.post(url, json={
                'query': query,
                'variables': {
                    'categorySlug': "",
                    'limit': limit,
                    'skip': skip,
                    'filters': {}
                }
            })

            data = response.json()
            if 'errors' in data:
                print("API Errors:", data['errors'])
                continue

            batch = data['data']['problemsetQuestionList']['questions']
            all_problems.extend(batch)
            skip += limit

        # Store in database
        with sqlite3.connect('leetcode.db') as conn:
            cursor = conn.cursor()
            for problem in all_problems:
                # Convert topic tags to comma-separated string
                topics = ','.join(tag['name'] for tag in problem['topicTags'])

                cursor.execute("""
                    INSERT OR REPLACE INTO problems 
                    (leetcode_id, title, difficulty, topics)
                    VALUES (?, ?, ?, ?)
                """, (
                    problem['questionId'],
                    problem['title'],
                    problem['difficulty'],
                    topics
                ))

            conn.commit()

        return len(all_problems)

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        print(f"Full error details: {type(e).__name__}")
        return 0


if __name__ == '__main__':
    print("Starting LeetCode problem fetch...")
    count = fetch_leetcode_problems()
    print(f"Successfully imported {count} problems from LeetCode")