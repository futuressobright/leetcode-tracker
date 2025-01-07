-- Clear Grind 75 (List 4)
DELETE FROM problem_lists WHERE list_id IN (
    SELECT id FROM lists WHERE slot = 4
);

-- Populate Grind 75 (List 4)
INSERT INTO problem_lists (problem_id, list_id)
SELECT p.id, l.id
FROM problems p
CROSS JOIN lists l
WHERE l.slot = 4
AND p.leetcode_id IN (
    '1',    -- Two Sum
    '20',   -- Valid Parentheses
    '21',   -- Merge Two Sorted Lists 
    '121',  -- Best Time to Buy and Sell Stock
    '125',  -- Valid Palindrome
    '226',  -- Invert Binary Tree
    '242',  -- Valid Anagram
    '704',  -- Binary Search
    '733',  -- Flood Fill
    '235',  -- Lowest Common Ancestor of a BST
    '110',  -- Balanced Binary Tree
    '141',  -- Linked List Cycle
    '232',  -- Implement Queue using Stacks
    '278',  -- First Bad Version
    '383',  -- Ransom Note
    '70',   -- Climbing Stairs
    '409',  -- Longest Palindrome
    '206',  -- Reverse Linked List
    '169',  -- Majority Element
    '67',   -- Add Binary
    '543',  -- Diameter of Binary Tree
    '876',  -- Middle of the Linked List
    '104',  -- Maximum Depth of Binary Tree
    '217',  -- Contains Duplicate
    '53',   -- Maximum Subarray
    '542',  -- 01 Matrix
    '973',  -- K Closest Points to Origin
    '3',    -- Longest Substring Without Repeating Characters
    '15',   -- 3Sum
    '102',  -- Binary Tree Level Order Traversal
    '133',  -- Clone Graph
    '150',  -- Evaluate Reverse Polish Notation
    '207',  -- Course Schedule
    '208',  -- Implement Trie (Prefix Tree)
    '322',  -- Coin Change
    '238',  -- Product of Array Except Self
    '155',  -- Min Stack
    '98',   -- Validate Binary Search Tree
    '200',  -- Number of Islands
    '191',  -- Number of 1 Bits
    '33',   -- Search in Rotated Sorted Array
    '39',   -- Combination Sum
    '75',   -- Sort Colors
    '62',   -- Unique Paths
    '128',  -- Longest Consecutive Sequence
    '424',  -- Longest Repeating Character Replacement
    '76',   -- Minimum Window Substring
    '212',  -- Word Search II
    '297',  -- Serialize and Deserialize Binary Tree
    '57',   -- Insert Interval
    '56',   -- Merge Intervals
    '295',  -- Find Median from Data Stream
    '139',  -- Word Break
    '338',  -- Counting Bits
    '2',    -- Add Two Numbers
    '230',  -- Kth Smallest Element in a BST
    '236',  -- Lowest Common Ancestor of Binary Tree
    '981',  -- Time Based Key-Value Store
    '23',   -- Merge k Sorted Lists
    '347',  -- Top K Frequent Elements
    '5',    -- Longest Palindromic Substring
    '417',  -- Pacific Atlantic Water Flow
    '11',   -- Container With Most Water
    '91',   -- Decode Ways
    '438',  -- Find All Anagrams in a String
    '54',   -- Spiral Matrix
    '105',  -- Construct Binary Tree from Preorder and Inorder
    '416',  -- Partition Equal Subset Sum
    '8',    -- String to Integer (atoi)
    '17',   -- Letter Combinations of a Phone Number
    '124',  -- Binary Tree Maximum Path Sum
    '269',  -- Alien Dictionary
    '198',  -- House Robber
    '55',   -- Jump Game
    '49',   -- Group Anagrams
    '146',  -- LRU Cache
    '153',  -- Find Minimum in Rotated Sorted Array
    '300',  -- Longest Increasing Subsequence
    '79',   -- Word Search
    '19',   -- Remove Nth Node From End of List
    '647',  -- Palindromic Substrings
    '271',  -- Encode and Decode Strings
    '143',  -- Reorder List
    '199'   -- Binary Tree Right Side View
);
