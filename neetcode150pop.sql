-- Clear existing problems from List 5
DELETE FROM problem_lists 
WHERE list_id = (SELECT id FROM lists WHERE slot = 5);

-- Insert Neetcode 150 problems into List 5 (excluding those in List 4)
INSERT INTO problem_lists (problem_id, list_id)
SELECT p.id, l.id
FROM problems p
CROSS JOIN lists l
WHERE l.slot = 5
AND p.leetcode_id IN (
    '36',   -- Valid Sudoku
    '271',  -- Encode and Decode Strings
    '128',  -- Longest Consecutive Sequence
    '42',   -- Trapping Rain Water
    '84',   -- Largest Rectangle in Histogram
    '40',   -- Combination Sum II
    '131',  -- Palindrome Partitioning
    '46',   -- Permutations
    '78',   -- Subsets
    '213',  -- House Robber II
    '5',    -- Longest Palindromic Substring
    '45',   -- Jump Game II
    '134',  -- Gas Station
    '152',  -- Maximum Product Subarray
    '435',  -- Non-overlapping Intervals
    '678',  -- Valid Parenthesis String
    '235',  -- Lowest Common Ancestor of a BST
    '1448', -- Count Good Nodes in Binary Tree
    '98',   -- Validate Binary Search Tree
    '230',  -- Kth Smallest Element in a BST
    '100',  -- Same Tree
    '572',  -- Subtree of Another Tree
    '199',  -- Binary Tree Right Side View
    '1046', -- Last Stone Weight
    '703',  -- Kth Largest Element in a Stream
    '875',  -- Koko Eating Bananas
    '22',   -- Generate Parentheses
    '150',  -- Evaluate Reverse Polish Notation
    '207',  -- Course Schedule
    '210',  -- Course Schedule II
    '684',  -- Redundant Connection
    '323',  -- Number of Connected Components in an Undirected Graph
    '261',  -- Graph Valid Tree
    '994',  -- Rotting Oranges
    '286',  -- Walls and Gates
    '127',  -- Word Ladder
    '417',  -- Pacific Atlantic Water Flow
    '130',  -- Surrounded Regions
    '695',  -- Max Area of Island
    '743',  -- Network Delay Time
    '787',  -- Cheapest Flights Within K Stops
    '73',   -- Set Matrix Zeroes
    '54',   -- Spiral Matrix
    '48',   -- Rotate Image
    '435',  -- Non-overlapping Intervals
    '179',  -- Largest Number
    '2013', -- Detect Squares
    '74',   -- Search a 2D Matrix
    '33',   -- Search in Rotated Sorted Array
    '153',  -- Find Minimum in Rotated Sorted Array
    '981',  -- Time Based Key-Value Store
    '4',    -- Median of Two Sorted Arrays
    '49',   -- Group Anagrams
    '347',  -- Top K Frequent Elements
    '211',  -- Design Add and Search Words Data Structure
    '146',  -- LRU Cache
    '23',   -- Merge k Sorted Lists
    '25',   -- Reverse Nodes in k-Group
    '124',  -- Binary Tree Maximum Path Sum
    '105',  -- Construct Binary Tree from Preorder and Inorder
    '698',  -- Partition to K Equal Sum Subsets
    '312',  -- Burst Balloons
    '72',   -- Edit Distance
    '10',   -- Regular Expression Matching
    '295'   -- Find Median from Data Stream
)
AND p.id NOT IN (
    SELECT problem_id 
    FROM problem_lists pl
    JOIN lists l ON pl.list_id = l.id
    WHERE l.slot = 4
);
