from unittest.mock import MagicMock, patch

import pytest
from gitlab.v4.objects import Project, ProjectIssue

from gitlab_burndown.discovery import (
    get_issues_for_project,
    search_project_id_by_project_name,
)
from gitlab_burndown.exceptions import (
    MultipleProjectsFoundException,
    ProjectNotFoundException,
)


def mock_issue(id, title) -> MagicMock:
    issue = MagicMock(spec=ProjectIssue)
    issue.id = id
    issue.title = title
    return issue


def mock_project(id, name) -> MagicMock:
    project: MagicMock = MagicMock(spec=Project)
    project.id = id
    project.name = name
    return project


@patch("gitlab_burndown.discovery.get_gitlab")
def test_get_issues_for_project(mock_get_gitlab) -> None:
    # Mocking the GitLab project and issues
    project_id = 1
    mock_project = MagicMock()

    # Creating mock issues (2 valid ProjectIssues, 1 invalid object)
    mock_issues = [
        mock_issue(1, "Issue 1"),
        mock_issue(2, "Issue 2"),
        MagicMock(),  # This will simulate an invalid object that's not ProjectIssue
    ]

    # Mock the project.issues.list to return our mock issues
    mock_project.issues.list.return_value = mock_issues
    mock_gitlab = MagicMock()
    mock_gitlab.projects.get.return_value = mock_project
    mock_get_gitlab.return_value = mock_gitlab

    # Call the function we're testing
    issues = get_issues_for_project(project_id)

    # Assert that the correct issues (ProjectIssue instances) are returned
    assert len(issues) == 2  # Only two valid ProjectIssue objects
    assert all(isinstance(issue, ProjectIssue) for issue in issues)

    # Check that the GitLab API was called with the correct project ID
    mock_gitlab.projects.get.assert_called_once_with(project_id)
    mock_project.issues.list.assert_called_once_with(all=True)


@patch("gitlab_burndown.discovery.get_gitlab")
def test_search_project_single_match(mock_get_gitlab) -> None:
    project_name = "test_project"
    mock_gitlab: MagicMock = MagicMock()
    mock_gitlab.projects.list.return_value = [mock_project(1, project_name)]
    mock_get_gitlab.return_value = mock_gitlab

    project_id: int = search_project_id_by_project_name(project_name)

    assert project_id == 1
    mock_gitlab.projects.list.assert_called_once_with(search=project_name)


@patch("gitlab_burndown.discovery.get_gitlab")
def test_search_project_no_match(mock_get_gitlab) -> None:
    project_name = "nonexistent_project"
    mock_gitlab: MagicMock = MagicMock()
    mock_gitlab.projects.list.return_value = []
    mock_get_gitlab.return_value = mock_gitlab

    with pytest.raises(
        ProjectNotFoundException,
        match=f"No project found with the name '{project_name}'",
    ):
        search_project_id_by_project_name(project_name)

    mock_gitlab.projects.list.assert_called_once_with(search=project_name)


@patch("gitlab_burndown.discovery.get_gitlab")
def test_search_project_multiple_matches(mock_get_gitlab) -> None:
    project_name = "duplicate_project"
    mock_gitlab: MagicMock = MagicMock()
    mock_gitlab.projects.list.return_value = [
        mock_project(1, project_name),
        mock_project(2, project_name),
    ]
    mock_get_gitlab.return_value = mock_gitlab

    with pytest.raises(
        MultipleProjectsFoundException,
        match=f"Multiple projects found with the name '{project_name}'",
    ):
        search_project_id_by_project_name(project_name)

    mock_gitlab.projects.list.assert_called_once_with(search=project_name)
