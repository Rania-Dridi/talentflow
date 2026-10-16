class DomainError(Exception):
    """Base class for business-rule violations. The API layer maps these to HTTP errors."""

    status_code = 422


class NotFound(DomainError):
    status_code = 404


class Conflict(DomainError):
    status_code = 409
