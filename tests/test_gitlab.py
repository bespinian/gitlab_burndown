from unittest.mock import patch

from gitlab_burndown.gitlab import get_gitlab


@patch("gitlab_burndown.gitlab.get_config")
@patch("gitlab_burndown.gitlab.Gitlab")
def test_get_gitlab(mock_gitlab, mock_get_config) -> None:
    # Mock config values
    mock_get_config.return_value.GITLAB_URL = "https://mock-gitlab-url.com"
    mock_get_config.return_value.GITLAB_ACCESS_TOKEN = "mock-access-token"

    # Call the function
    gitlab_instance = get_gitlab()

    # Assert that Gitlab was called with correct URL and token
    mock_gitlab.assert_called_once_with(
        url="https://mock-gitlab-url.com", private_token="mock-access-token"
    )

    # Assert the returned instance is what we expect
    assert gitlab_instance == mock_gitlab.return_value
