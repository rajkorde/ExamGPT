class PromptNotFound(Exception):
    """Raised when prompt for a scenario is not found"""

    def __init__(self, message: str = "Prompt not found"):
        self.message = message

    def __str__(self):
        return self.message


class NotEnoughInformationInContext(Exception):
    """Raised when provided text chunk does not have enough information to create a question"""

    def __init__(
        self,
        message: str = "Provided text chunk does not have enough information to create a question",
    ):
        self.message = message

    def __str__(self):
        return self.message
