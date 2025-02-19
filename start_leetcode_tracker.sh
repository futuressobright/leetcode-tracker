#!/bin/bash
cd /Users/ashish/Dropbox/programming/leetcode_tracker
source venv/bin/activate

# Check if already running
if pgrep -f "python3 app.py" > /dev/null; then
    echo "LeetCode Tracker is already running!"
    echo "To view running processes: ps aux | grep python"
    echo "To view logs: tail -f leetcode_tracker.log"
    exit 1
else
    python3 app.py >!leetcode_tracker.log 2>&1 &
    echo "LeetCode Tracker started. View logs with: tail -f leetcode_tracker.log"
fi
