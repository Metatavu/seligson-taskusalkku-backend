class MigrationException(Exception):
    """
    Migration exception
    """
    pass


class MissingEntityException(MigrationException):
    """
    Exception for missing entity
    """
    original_id: str
    target_task: str
    message: str

    def __init__(self, original_id: str, target_task: str, message: str):
        """
        Constructor

        Args:
            original_id: original id
            target_task: target task
            message: message
        """
        self.original_id = original_id
        self.target_task = target_task
        self.message = message


class MissingSecurityException(MissingEntityException):
    """
    Exception for missing security
    """
    def __init__(self, original_id):
        """
        Constructor
        Args:
            original_id: original security id
        """
        super().__init__(
            original_id=original_id,
            target_task="securities",
            message=f"Could not find security with original id {original_id}"
        )


class MissingCompanyException(MissingEntityException):
    """
    Exception for missing company
    """
    def __init__(self, original_id):
        """
        Constructor

        Args:
            original_id: original company id
        """
        super().__init__(
            original_id=original_id,
            target_task="companies",
            message=f"Could not find company with original id {original_id}"
        )


class MissingPortfolioException(MissingEntityException):
    """
    Exception for missing portfolio
    """
    def __init__(self, original_id):
        """
        Constructor

        Args:
            original_id: original portfolio id
        """
        super().__init__(
            original_id=original_id,
            target_task="portfolios",
            message=f"Could not find portfolio with original id {original_id}"
        )
