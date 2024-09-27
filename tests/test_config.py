from unittest.mock import patch

from gitlab_burndown.config import get_config

mock_environment_variables: dict[str, str] = {
    "GITLAB_ACCESS_TOKEN": "123",
    "GITLAB_URL": "https://test-gitlab.com",
    "GITLAB_PROJECT_NAME": "test",
}


def mock_getenv(key, default=None):
    return mock_environment_variables.get(key, default)


@patch("gitlab_burndown.config.load_dotenv", None)
@patch("gitlab_burndown.config.os.getenv", mock_getenv)
def test_get_config():
    config = get_config()
    assert config.GITLAB_ACCESS_TOKEN == "123"
    assert config.GITLAB_URL == "https://test-gitlab.com"
    assert config.GITLAB_PROJECT_NAME == "test"
