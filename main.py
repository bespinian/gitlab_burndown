from datetime import datetime, timedelta, timezone

import typer
from gitlab.v4.objects import ProjectIssue

from gitlab_burndown.config import get_config
from gitlab_burndown.discovery import (
    get_issues_for_project,
    search_project_id_by_project_name,
)
from gitlab_burndown.plotting import draw_plot, prepare_burndown_data
from gitlab_burndown.transformer import TimeInfo, transform_issue_to_time_info

app = typer.Typer()


def parse_duration(duration_str: str) -> datetime:
    """Parse a string like '30d', '2m' and return a timezone-aware datetime object."""
    now = datetime.now(timezone.utc)  # Use timezone-aware datetime (UTC)

    if duration_str.endswith("d"):
        days = int(duration_str[:-1])
        return now - timedelta(days=days)
    elif duration_str.endswith("m"):
        months = int(duration_str[:-1])
        return now - timedelta(days=months * 30)
    else:
        raise ValueError(
            "Invalid duration format. Use 'Xd' for days or 'Xm' for months."
        )


@app.command()
def burndown(
    duration: str = typer.Argument(
        "30d", help="Duration string like '30d' for 30 days, '2m' for 2 months."
    ),
):
    """Main function to run the burndown chart generation."""
    project_id: int = search_project_id_by_project_name(
        get_config().GITLAB_PROJECT_NAME
    )
    issues: list[ProjectIssue] = get_issues_for_project(project_id)

    time_info: list[TimeInfo] = [
        transform_issue_to_time_info(issue) for issue in issues
    ]

    start_date = parse_duration(duration)

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
    app()
