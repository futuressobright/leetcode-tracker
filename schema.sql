-- Problems table with index
CREATE TABLE problems (
    id INTEGER PRIMARY KEY,
    leetcode_id TEXT UNIQUE,
    title TEXT,
    difficulty TEXT,
    topics TEXT
);
CREATE INDEX idx_problems_title ON problems(title);

-- Attempts table with index and foreign key
CREATE TABLE attempts (
    id INTEGER PRIMARY KEY,
    problem_id INTEGER,
    comfort_level TEXT,
    notes TEXT,
    next_review DATE,
    attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (problem_id) REFERENCES problems (id)
);
CREATE INDEX idx_attempts_next_review ON attempts(next_review);

-- Lists table with constraints
CREATE TABLE lists (
    id INTEGER PRIMARY KEY,
    slot INTEGER NOT NULL CHECK (slot BETWEEN 1 AND 5),
    name TEXT NOT NULL,
    description TEXT
);

-- Problem-lists relationship table with foreign keys
CREATE TABLE problem_lists (
    problem_id INTEGER,
    list_id INTEGER,
    FOREIGN KEY (problem_id) REFERENCES problems (id),
    FOREIGN KEY (list_id) REFERENCES lists (id),
    PRIMARY KEY (problem_id, list_id)
);

-- Initialize default lists
INSERT INTO lists (slot, name) VALUES
    (1, 'List 1'),
    (2, 'List 2'),
    (3, 'List 3'),
    (4, 'List 4'),
    (5, 'List 5');