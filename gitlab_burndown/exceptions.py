class ProjectNotFoundException(Exception):
    """Raised when no project is found with the given name."""

    pass


class MultipleProjectsFoundException(Exception):
    """Raised when multiple projects with the same name are found."""

    pass
