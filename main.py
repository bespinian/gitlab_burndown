from datetime import datetime

from gitlab.v4.objects import ProjectIssue

from gitlab_burndown.config import get_config
from gitlab_burndown.discovery import (
    get_issues_for_project,
    search_project_id_by_project_name,
)
from gitlab_burndown.plotting import draw_plot, prepare_burndown_data
from gitlab_burndown.transformer import TimeInfo, transform_issue_to_time_info


def main():
    """Main function to find and print the project ID."""
    project_id: int = search_project_id_by_project_name(
        get_config().GITLAB_PROJECT_NAME
    )
    issues: list[ProjectIssue] = get_issues_for_project(project_id)

    time_info: list[TimeInfo] = [
        transform_issue_to_time_info(issue) for issue in issues
    ]

    start_date = datetime.fromisoformat("2024-09-01T00:00:00+00:00")
    (
        dates,
        remaining_estimates,
        remaining_estimates_hours,
        total_time_estimate,
    ) = prepare_burndown_data(time_info, start_date)

    draw_plot(
        dates,
        remaining_estimates,
        remaining_estimates_hours,
        total_time_estimate,
    )


if __name__ == "__main__":
    main()
