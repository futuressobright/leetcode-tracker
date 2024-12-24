# config.py
class Config:
    DATABASE_PATH = 'leetcode.db'

class TestConfig(Config):
    DATABASE_PATH = 'leetcode_test.db'
    TESTING = True
