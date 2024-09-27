import datetime
from dataclasses import dataclass

from gitlab.v4.objects import ProjectIssue


@dataclass
class TimeInfo:
    closed_at: datetime.datetime
    time_estimate: int


def transform_issue_to_time_info(issue: ProjectIssue) -> TimeInfo:
    closed_at_str: str | None = issue.attributes.get("closed_at")
    return TimeInfo(
        closed_at=(
            datetime.datetime.fromisoformat(
                closed_at_str.replace("Z", "+00:00")
            )
            if closed_at_str
            else datetime.datetime.now(datetime.timezone.utc)
        ),
        time_estimate=issue.attributes.get("time_stats", {}).get(
            "time_estimate"
        ),
    )
