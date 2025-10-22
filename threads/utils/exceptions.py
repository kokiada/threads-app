class ThreadsAPIError(Exception):
    pass

class RateLimitError(ThreadsAPIError):
    pass

class TokenExpiredError(ThreadsAPIError):
    pass

class ValidationError(Exception):
    pass
