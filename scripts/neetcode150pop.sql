-- Clear Neetcode 150 (List 5)
DELETE FROM problem_lists WHERE list_id IN (
    SELECT id FROM lists WHERE slot = 5
);

-- Populate Neetcode 150 (List 5)
INSERT INTO problem_lists (problem_id, list_id)
SELECT p.id, l.id
FROM problems p
CROSS JOIN lists l
WHERE l.slot = 5
AND p.leetcode_id IN (
    '1',    -- Two Sum
    '2',    -- Add Two Numbers
    '3',    -- Longest Substring Without Repeating Characters
    '4',    -- Median of Two Sorted Arrays
    '5',    -- Longest Palindromic Substring
    '518',  -- Coin Change II
    '7',    -- Reverse Integer
    '1448', -- Count Good Nodes in Binary Tree
    '10',   -- Regular Expression Matching
    '11',   -- Container With Most Water
    '994',  -- Rotting Oranges
    '15',   -- 3Sum
    '17',   -- Letter Combinations of a Phone Number
    '19',   -- Remove Nth Node From End of List
    '20',   -- Valid Parentheses
    '21',   -- Merge Two Sorted Lists
    '22',   -- Generate Parentheses
    '23',   -- Merge k Sorted Lists
    '25',   -- Reverse Nodes in k-Group
    '543',  -- Diameter of Binary Tree
    '33',   -- Search in Rotated Sorted Array
    '36',   -- Valid Sudoku
    '39',   -- Combination Sum
    '40',   -- Combination Sum II
    '42',   -- Trapping Rain Water
    '43',   -- Multiply Strings
    '45',   -- Jump Game II
    '46',   -- Permutations
    '48',   -- Rotate Image
    '49',   -- Group Anagrams
    '50',   -- Pow(x, n)
    '51',   -- N-Queens
    '53',   -- Maximum Subarray
    '54',   -- Spiral Matrix
    '55',   -- Jump Game
    '56',   -- Merge Intervals
    '57',   -- Insert Interval
    '567',  -- Permutation in String
    '572',  -- Subtree of Another Tree
    '62',   -- Unique Paths
    '66',   -- Plus One
    '70',   -- Climbing Stairs
    '72',   -- Edit Distance
    '73',   -- Set Matrix Zeroes
    '74',   -- Search a 2D Matrix
    '76',   -- Minimum Window Substring
    '78',   -- Subsets
    '79',   -- Word Search
    '84',   -- Largest Rectangle in Histogram
    '90',   -- Subsets II
    '91',   -- Decode Ways
    '97',   -- Interleaving String
    '98',   -- Validate Binary Search Tree
    '100',  -- Same Tree
    '102',  -- Binary Tree Level Order Traversal
    '104',  -- Maximum Depth of Binary Tree
    '105',  -- Construct Binary Tree from Preorder and Inorder
    '110',  -- Balanced Binary Tree
    '115',  -- Distinct Subsequences
    '121',  -- Best Time to Buy and Sell Stock
    '124',  -- Binary Tree Maximum Path Sum
    '125',  -- Valid Palindrome
    '127',  -- Word Ladder
    '128',  -- Longest Consecutive Sequence
    '130',  -- Surrounded Regions
    '131',  -- Palindrome Partitioning
    '133',  -- Clone Graph
    '134',  -- Gas Station
    '136',  -- Single Number
    '138',  -- Copy List with Random Pointer
    '139',  -- Word Break
    '141',  -- Linked List Cycle
    '143',  -- Reorder List
    '146',  -- LRU Cache
    '150',  -- Evaluate Reverse Polish Notation
    '152',  -- Maximum Product Subarray
    '153',  -- Find Minimum in Rotated Sorted Array
    '155',  -- Min Stack
    '167',  -- Two Sum II
    '678',  -- Valid Parenthesis String
    '190',  -- Reverse Bits
    '191',  -- Number of 1 Bits
    '198',  -- House Robber
    '199',  -- Binary Tree Right Side View
    '200',  -- Number of Islands
    '202',  -- Happy Number
    '206',  -- Reverse Linked List
    '207',  -- Course Schedule
    '208',  -- Implement Trie (Prefix Tree)
    '210',  -- Course Schedule II
    '211',  -- Design Add and Search Words Data Structure
    '212',  -- Word Search II
    '213',  -- House Robber II
    '217',  -- Contains Duplicate
    '226',  -- Invert Binary Tree
    '230',  -- Kth Smallest Element in a BST
    '235',  -- Lowest Common Ancestor of a BST
    '238',  -- Product of Array Except Self
    '239',  -- Sliding Window Maximum
    '242',  -- Valid Anagram
    '252',  -- Meeting Rooms
    '253',  -- Meeting Rooms II
    '261',  -- Graph Valid Tree
    '268',  -- Missing Number
    '269',  -- Alien Dictionary
    '271',  -- Encode and Decode Strings
    '286',  -- Walls and Gates
    '287',  -- Find the Duplicate Number
    '295',  -- Find Median from Data Stream
    '297',  -- Serialize and Deserialize Binary Tree
    '300',  -- Longest Increasing Subsequence
    '309',  -- Best Time to Buy and Sell Stock with Cooldown
    '312',  -- Burst Balloons
    '322',  -- Coin Change
    '323',  -- Number of Connected Components
    '329',  -- Longest Increasing Path in a Matrix
    '332',  -- Reconstruct Itinerary
    '338',  -- Counting Bits
    '347',  -- Top K Frequent Elements
    '355',  -- Design Twitter
    '371',  -- Sum of Two Integers
    '417',  -- Pacific Atlantic Water Flow
    '424',  -- Longest Repeating Character Replacement
    '435',  -- Non-overlapping Intervals
    '494',  -- Target Sum
    '647',  -- Palindromic Substrings
    '684',  -- Redundant Connection
    '695',  -- Max Area of Island
    '703',  -- Kth Largest Element in a Stream
    '739',  -- Daily Temperatures
    '743',  -- Network Delay Time
    '746',  -- Min Cost Climbing Stairs 
    '778',  -- Swim in Rising Water
    '787',  -- Cheapest Flights Within K Stops
    '846',  -- Hand of Straights
    '853',  -- Car Fleet
    '875',  -- Koko Eating Bananas
    '981',  -- Time Based Key-Value Store
    '1046', -- Last Stone Weight
    '1143', -- Longest Common Subsequence
    '1851', -- Minimum Interval to Include Each Query
    '1899', -- Merge Triplets to Form Target Triplet
    '2013'  -- Detect Squares
);
