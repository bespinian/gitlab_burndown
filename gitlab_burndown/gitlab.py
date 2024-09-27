from gitlab import Gitlab

from gitlab_burndown.config import get_config


def get_gitlab() -> Gitlab:
    """Return a Gitlab instance with the configured URL and access token."""

    return Gitlab(
        url=get_config().GITLAB_URL,
        private_token=get_config().GITLAB_ACCESS_TOKEN,
    )
