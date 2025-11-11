class AppException(Exception):
    """Custom exception for business logic errors."""

    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class DatabaseException(Exception):
    """Custom exception for database-related errors."""

    def __init__(self, message: str = "Database operation failed"):
        self.message = message
        self.status_code = 500
        super().__init__(message)
