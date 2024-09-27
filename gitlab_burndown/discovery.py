from gitlab.base import RESTObject, RESTObjectList
from gitlab.v4.objects import Project, ProjectIssue

from gitlab_burndown.exceptions import (
    MultipleProjectsFoundException,
    ProjectNotFoundException,
)
from gitlab_burndown.gitlab import get_gitlab


def get_issues_for_project(project_id: int) -> list[ProjectIssue]:
    project = get_gitlab().projects.get(project_id)
    issues = project.issues.list(all=True)
    typesave_issues = [
        issue for issue in issues if isinstance(issue, ProjectIssue)
    ]
    return typesave_issues


def get_time_estimate_for_issue(issue: ProjectIssue) -> int:
    return issue.attributes.get("time_stats", {}).get("time_estimate")


def search_project_id_by_project_name(project_name: str) -> int:
    """Search for a Gitlab project by name and return its ID.

    Raises:
        ProjectNotFoundException: If no project is found.
        MultipleProjectsFoundException: If more than one project is found.
    """

    projects: RESTObjectList | list[RESTObject] = get_gitlab().projects.list(
        search=project_name
    )
    matching_projects = [
        project
        for project in projects
        if isinstance(project, Project) and project.name == project_name
    ]
    if len(matching_projects) == 0:
        raise ProjectNotFoundException(
            f"No project found with the name '{project_name}'."
        )
    elif len(matching_projects) > 1:
        raise MultipleProjectsFoundException(
            f"Multiple projects found with the name '{project_name}'."
        )
    return matching_projects[0].id
