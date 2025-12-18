class AppError(Exception):
    """Base class for application errors."""
    pass


class NotFoundError(AppError):
    """Raised when an entity is not found."""
    pass


class ConflictError(AppError):
    """Raised when an operation conflicts with current state (e.g., duplicate)."""
    pass
