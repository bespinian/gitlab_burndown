import os

from dotenv import load_dotenv

load_dotenv()


CONFIG = None


class Config:
    """Class to store the configuration values."""

    def __init__(self) -> None:
        self.GITLAB_ACCESS_TOKEN = os.getenv("GITLAB_ACCESS_TOKEN", "")
        self.GITLAB_URL = os.getenv("GITLAB_URL", "")
        self.GITLAB_PROJECT_NAME = os.getenv("GITLAB_PROJECT_NAME", "")


def get_config() -> Config:
    """Return a Config instance with the configured values."""

    global CONFIG
    if CONFIG is None:
        CONFIG = Config()
    return CONFIG
