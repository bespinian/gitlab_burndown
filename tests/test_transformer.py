from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest
from freezegun import freeze_time
from gitlab.v4.objects import ProjectIssue

from gitlab_burndown.transformer import TimeInfo, transform_issue_to_time_info


def test_transform_issue_with_closed_at():
    # Mock the ProjectIssue with a closed_at field and time estimate
    issue = MagicMock(spec=ProjectIssue)
    issue.attributes = {
        "closed_at": "2024-09-20T12:00:00Z",
        "time_stats": {"time_estimate": 3600},
    }

    # Transform the issue into TimeInfo
    time_info = transform_issue_to_time_info(issue)

    # Check that the closed_at and time_estimate are correctly set
    assert time_info == TimeInfo(
        closed_at=datetime(2024, 9, 20, 12, 0, tzinfo=timezone.utc),
        time_estimate=3600,
    )


@freeze_time("2024-09-20 12:00:00")
def test_transform_issue_without_closed_at():
    # Mock the ProjectIssue with no closed_at field and a time estimate
    issue = MagicMock(spec=ProjectIssue)
    issue.attributes = {
        "closed_at": None,
        "time_stats": {"time_estimate": 7200},
    }

    # Transform the issue into TimeInfo
    time_info = transform_issue_to_time_info(issue)

    # Check that the closed_at is set to the frozen time
    assert time_info.closed_at == datetime(
        2024, 9, 20, 12, 0, tzinfo=timezone.utc
    )
    assert time_info.time_estimate == 7200


def test_transform_issue_with_missing_time_estimate():
    # Mock the ProjectIssue with closed_at but missing time estimate
    issue = MagicMock(spec=ProjectIssue)
    issue.attributes = {
        "closed_at": "2024-09-20T12:00:00Z",
        "time_stats": {},  # No time_estimate
    }

    # Transform the issue into TimeInfo
    time_info = transform_issue_to_time_info(issue)

    # Check that the closed_at is correctly set and time_estimate is None
    assert time_info == TimeInfo(
        closed_at=datetime(2024, 9, 20, 12, 0, tzinfo=timezone.utc),
        time_estimate=None,
    )


def test_transform_issue_with_invalid_closed_at_format():
    # Mock the ProjectIssue with an invalid closed_at format
    issue = MagicMock(spec=ProjectIssue)
    issue.attributes = {
        "closed_at": "invalid-date-format",
        "time_stats": {"time_estimate": 4800},
    }

    # Ensure that an error is raised for the invalid date format
    with pytest.raises(ValueError, match="Invalid isoformat string"):
        transform_issue_to_time_info(issue)
