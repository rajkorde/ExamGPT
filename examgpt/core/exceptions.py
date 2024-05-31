class PromptNotFound(Exception):
    """Raised when prompt for a scenario is not found"""

    def __init__(self, message: str = "Prompt not found"):
        self.message = message

    def __str__(self):
        return self.message
