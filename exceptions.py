
class ForbiddenCharacterError(Exception):
    """Exception raised for forbidden characters in a condition."""
    def __init__(self, *forbidden_chars):
        self.forbidden_chars = forbidden_chars
        super().__init__(f"Forbidden characters: {', '.join(forbidden_chars)}")

