CREATE TABLE problems (
    id INTEGER PRIMARY KEY,
    leetcode_id TEXT UNIQUE,
    title TEXT,
    difficulty TEXT,
    topics TEXT
);

CREATE TABLE attempts (
    id INTEGER PRIMARY KEY,
    problem_id INTEGER,
    comfort_level TEXT,
    notes TEXT,
    next_review DATE,
    attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (problem_id) REFERENCES problems (id)
);

-- New tables for lists functionality
CREATE TABLE lists (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE,
    description TEXT
);

CREATE TABLE problem_lists (
    problem_id INTEGER,
    list_id INTEGER,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (problem_id) REFERENCES problems (id),
    FOREIGN KEY (list_id) REFERENCES lists (id),
    PRIMARY KEY (problem_id, list_id)
);

CREATE INDEX idx_problems_title ON problems(title);
CREATE INDEX idx_attempts_next_review ON attempts(next_review);
