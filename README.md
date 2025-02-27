# START
./start_leetcode_tracker.sh
- This will persist until logout or reboot.
- output to ./leetcode_tracker.log
- ps aux | grep python

# LeetCode Tracker

A Flask web application to track your LeetCode problem-solving progress. Features include:
- Track completion and comfort level with problems
- Organize problems into custom lists
- Review problems based on spaced repetition
- Filter by topics and search problems

## Setup
1. Clone the repository
2. Install requirements: `pip install -r requirements.txt`
3. ./start_leetcode_tracker.sh
4. Access at http://localhost:5001

## Features
- Comfort level tracking (Easy/Medium/Hard)
- Custom notes for each attempt
- Topic-based filtering
- Custom problem lists
- Spaced repetition review system
