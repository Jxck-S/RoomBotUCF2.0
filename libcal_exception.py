class LibCalError(Exception):
    """A custom exception."""

    def __init__(self, message="An error occurred."):
        self.message = message
        super().__init__(self.message)

class ExceedsDailyLimitError(LibCalError):
    """Exception raised when the daily limit is exceeded."""

    def __init__(self, message="Sorry, this exceeds the 240 minute per day limit across all locations"):
        super().__init__(message)

#Sorry, the selected times have become unavailable.
class TimesUnavailableError(LibCalError):
    """Exception raised when the selected times are unavailable."""

    def __init__(self, message="Sorry, the selected times have become unavailable."):
        super().__init__(message)

