from datetime import datetime, timedelta, timezone
from typing import List, Tuple

import matplotlib.pyplot as plt

from gitlab_burndown.transformer import TimeInfo


def interpolate_zero_burndown(
    dates: List[datetime], remaining_estimates: List[int]
) -> datetime:
    """
    Interpolates the date when the burndown chart would reach zero remaining time.

    Args:
        dates (List[datetime]): List of dates corresponding to the burndown data points.
        remaining_estimates (List[int]): List of remaining time estimates (in seconds).

    Returns:
        datetime: The interpolated date when the remaining estimate would reach zero.

    Raises:
        ValueError: If there are not enough data points to interpolate, or if the
                    burndown does not show a decreasing trend.
    """
    if len(remaining_estimates) < 2:
        raise ValueError("Need at least two data points to interpolate.")

    for i in range(len(remaining_estimates) - 1, 0, -1):
        if remaining_estimates[i] < remaining_estimates[i - 1]:
            return _calculate_zero_burndown_date(
                dates[i - 1],
                dates[i],
                remaining_estimates[i - 1],
                remaining_estimates[i],
            )

    raise ValueError(
        "Unable to interpolate; the burndown does not show a decreasing trend."
    )


def _calculate_zero_burndown_date(
    x1: datetime, x2: datetime, y1: int, y2: int
) -> datetime:
    """
    Helper function to calculate the zero burndown date using linear interpolation.

    Args:
        x1 (datetime): Date of the first point.
        x2 (datetime): Date of the second point.
        y1 (int): Remaining time at the first point (in seconds).
        y2 (int): Remaining time at the second point (in seconds).

    Returns:
        datetime: The interpolated zero burndown date.
    """
    slope = (y2 - y1) / (x2 - x1).total_seconds()
    time_to_zero = -y2 / slope
    zero_burndown_date = x2 + timedelta(seconds=time_to_zero)
    return zero_burndown_date


def prepare_burndown_data(
    time_info: List[TimeInfo],
    start_date: datetime,
) -> Tuple[List[datetime], List[int], List[float], int]:
    """
    Prepares the burndown data for plotting.

    Args:
        time_info (List[TimeInfo]): List of TimeInfo objects containing issue data.

    Returns:
        Tuple[List[datetime], List[int], List[float], int]: Tuple containing lists of dates,
        remaining time estimates, remaining time estimates in hours, and total time estimate.
    """

    time_info_sorted = _filter_and_sort_time_info(time_info, start_date)
    total_time_estimate = sum(info.time_estimate for info in time_info_sorted)

    dates, remaining_estimates = _calculate_remaining_estimates(
        time_info_sorted, total_time_estimate
    )

    remaining_estimates_hours = [x / 3600 for x in remaining_estimates]
    return (
        dates,
        remaining_estimates,
        remaining_estimates_hours,
        total_time_estimate,
    )


def _filter_and_sort_time_info(
    time_info: List[TimeInfo], start_date: datetime
) -> List[TimeInfo]:
    """
    Filters and sorts the time info data by closed_at date, excluding items before the start date.

    Args:
        time_info (List[TimeInfo]): List of TimeInfo objects.
        start_date (datetime): The date to filter issues that were closed after.

    Returns:
        List[TimeInfo]: Sorted and filtered list of TimeInfo objects.
    """
    time_info_sorted = sorted(time_info, key=lambda x: x.closed_at)
    return [info for info in time_info_sorted if info.closed_at >= start_date]


def _calculate_remaining_estimates(
    time_info_sorted: List[TimeInfo], total_time_estimate: int
) -> Tuple[List[datetime], List[int]]:
    """
    Calculates the remaining estimates for the burndown chart based on time_info_sorted.

    Args:
        time_info_sorted (List[TimeInfo]): Sorted list of TimeInfo objects.
        total_time_estimate (int): The total time estimate at the beginning.

    Returns:
        Tuple[List[datetime], List[int]]: List of dates and remaining time estimates.
    """
    dates: List[datetime] = []
    remaining_estimates: List[int] = []
    remaining_time = total_time_estimate

    without_opened_issues = _filter_out_today_issues(time_info_sorted)

    for info in without_opened_issues:
        dates.append(info.closed_at)
        remaining_time -= info.time_estimate
        remaining_estimates.append(remaining_time)

    # Include the starting point in the burndown chart
    start_date = datetime.fromisoformat("2024-09-01T00:00:00+00:00")
    dates.insert(0, start_date)
    remaining_estimates.insert(0, total_time_estimate)

    return dates, remaining_estimates


def _filter_out_today_issues(
    time_info_sorted: List[TimeInfo],
) -> List[TimeInfo]:
    """
    Filters out issues that were closed today from the sorted time info.

    Args:
        time_info_sorted (List[TimeInfo]): Sorted list of TimeInfo objects.

    Returns:
        List[TimeInfo]: List of issues excluding the ones closed today.
    """
    return [
        x
        for x in time_info_sorted
        if x.closed_at.date() != datetime.now(timezone.utc).date()
    ]


def draw_plot(
    dates: List[datetime],
    remaining_estimates: List[int],
    remaining_estimates_hours: List[float],
    total_time_estimate: int,
) -> None:
    """
    Draws the burndown chart using matplotlib.

    Args:
        dates (List[datetime]): List of dates for the x-axis.
        remaining_estimates (List[int]): List of remaining estimates for y-axis.
        remaining_estimates_hours (List[float]): List of remaining time estimates in hours.
        total_time_estimate (int): The total time estimate in seconds.
    """
    estimated_zero_date = interpolate_zero_burndown(dates, remaining_estimates)

    plt.figure(figsize=(10, 6))
    plt.fill_between(dates, remaining_estimates_hours, color="b", alpha=0.5)
    plt.ylim(0, total_time_estimate / 3600 + 10)
    plt.text(
        (dates[0] + (dates[-1] - dates[0]) / 2),
        plt.ylim()[0],
        f'Estimated zero from interpolation: {estimated_zero_date.strftime("%d.%m.%Y")}',
        horizontalalignment="center",
        verticalalignment="bottom",
        fontsize=12,
        color="black",
    )
    plt.title("Burndown Chart")
    plt.xlabel("Date")
    plt.ylabel("Remaining Time Estimate [h]")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("burndown_chart.png")
