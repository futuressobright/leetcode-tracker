# exceptions.py
class DatabaseError(Exception):
    """Base exception for database operations"""
    pass

class RecordNotFoundError(DatabaseError):
    """Raised when a database record is not found"""
    pass

class DatabaseConnectionError(DatabaseError):
    """Raised when database connection fails"""
    pass
