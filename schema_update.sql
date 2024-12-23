-- schema_update.sql

-- Drop existing tables if they exist
DROP TABLE IF EXISTS problem_lists;
DROP TABLE IF EXISTS lists;

-- Create fresh tables
CREATE TABLE lists (
    id INTEGER PRIMARY KEY,
    slot INTEGER NOT NULL CHECK (slot BETWEEN 1 AND 5),
    name TEXT NOT NULL,
    description TEXT
);

-- Initialize the 5 default lists
INSERT INTO lists (slot, name) VALUES
    (1, 'List 1'),
    (2, 'List 2'),
    (3, 'List 3'),
    (4, 'List 4'),
    (5, 'List 5');

CREATE TABLE problem_lists (
    problem_id INTEGER,
    list_id INTEGER,
    FOREIGN KEY (problem_id) REFERENCES problems (id),
    FOREIGN KEY (list_id) REFERENCES lists (id),
    PRIMARY KEY (problem_id, list_id)
);