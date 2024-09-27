from unittest.mock import MagicMock, patch

import pytest
from gitlab.v4.objects import Project

from gitlab_burndown.discovery import search_project_id_by_project_name
from gitlab_burndown.exceptions import (
    MultipleProjectsFoundException,
    ProjectNotFoundException,
)


def mock_project(id, name) -> MagicMock:
    project: MagicMock = MagicMock(spec=Project)
    project.id = id
    project.name = name
    return project


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
