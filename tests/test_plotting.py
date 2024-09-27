from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest

from gitlab_burndown.plotting import (
    _calculate_zero_burndown_date,
    _filter_and_sort_time_info,
    _filter_out_today_issues,
    draw_plot,
    interpolate_zero_burndown,
    prepare_burndown_data,
)
from gitlab_burndown.transformer import TimeInfo


# Helper function to create TimeInfo objects
def create_time_info(closed_at: datetime, time_estimate: int) -> TimeInfo:
    return TimeInfo(closed_at=closed_at, time_estimate=time_estimate)


def test_interpolate_zero_burndown():
    # Sample data for interpolation
    dates = [
        datetime(2024, 9, 1),
        datetime(2024, 9, 10),
        datetime(2024, 9, 20),
    ]
    remaining_estimates = [1000, 800, 200]  # in seconds

    # Call the function to test
    zero_burndown_date = interpolate_zero_burndown(dates, remaining_estimates)

    # Check that the zero burndown date is a datetime and reasonable (between last two points)
    assert isinstance(zero_burndown_date, datetime)
    assert zero_burndown_date > dates[-1]


def test_interpolate_zero_burndown_insufficient_data():
    with pytest.raises(ValueError, match="Need at least two data points"):
        interpolate_zero_burndown([datetime.now()], [1000])


def test_calculate_zero_burndown_date():
    # Test the interpolation of the zero burndown date
    date1 = datetime(2024, 9, 10)
    date2 = datetime(2024, 9, 20)
    remaining_time1 = 800
    remaining_time2 = 200

    zero_burndown_date = _calculate_zero_burndown_date(
        date1, date2, remaining_time1, remaining_time2
    )

    assert isinstance(zero_burndown_date, datetime)
    assert zero_burndown_date > date2  # It should be after the last date


def test_prepare_burndown_data():
    # Create mock TimeInfo objects
    time_info = [
        create_time_info(datetime(2024, 9, 1, tzinfo=timezone.utc), 1000),
        create_time_info(datetime(2024, 9, 5, tzinfo=timezone.utc), 500),
        create_time_info(datetime(2024, 9, 10, tzinfo=timezone.utc), 300),
    ]
    start_date = datetime(2024, 9, 1, tzinfo=timezone.utc)

    (
        dates,
        remaining_estimates,
        remaining_estimates_hours,
        total_time_estimate,
    ) = prepare_burndown_data(time_info, start_date)

    assert (
        len(dates) == len(remaining_estimates) == len(remaining_estimates_hours)
    )
    assert total_time_estimate == 1800
    assert dates[0] == datetime(2024, 9, 1, tzinfo=timezone.utc)


def test_filter_and_sort_time_info():
    start_date = datetime(2024, 9, 1)
    time_info = [
        create_time_info(datetime(2024, 8, 31), 1000),  # Should be filtered out
        create_time_info(datetime(2024, 9, 5), 500),
        create_time_info(datetime(2024, 9, 10), 300),
    ]

    filtered_sorted = _filter_and_sort_time_info(time_info, start_date)

    assert len(filtered_sorted) == 2
    assert filtered_sorted[0].closed_at == datetime(2024, 9, 5)


def test_filter_out_today_issues():
    # Set up a mixture of "today" and "past" issues
    today = datetime.now(timezone.utc)
    past_date = today - timedelta(days=1)

    time_info = [
        create_time_info(past_date, 1000),
        create_time_info(today, 500),
    ]

    filtered = _filter_out_today_issues(time_info)
    assert len(filtered) == 1
    assert filtered[0].closed_at == past_date


@patch("matplotlib.pyplot.savefig")
@patch("matplotlib.pyplot.fill_between")
@patch("matplotlib.pyplot.text")
def test_draw_plot(mock_text, mock_fill_between, mock_savefig):
    # Mock data for the plot
    dates = [datetime(2024, 9, 1), datetime(2024, 9, 5), datetime(2024, 9, 10)]
    remaining_estimates = [1000, 500, 300]
    remaining_estimates_hours = [x / 3600 for x in remaining_estimates]
    total_time_estimate = sum(remaining_estimates)

    # Call the draw_plot function
    draw_plot(
        dates,
        remaining_estimates,
        remaining_estimates_hours,
        total_time_estimate,
    )

    # Check if fill_between and savefig were called
    mock_fill_between.assert_called_once()
    mock_text.assert_called_once_with(
        (dates[0] + (dates[-1] - dates[0]) / 2),  # X-position at midpoint
        0.0,  # Y-position (plt.ylim()[0] was 0.0)
        "Estimated zero from interpolation: 17.09.2024",
        horizontalalignment="center",
        verticalalignment="bottom",
        fontsize=12,
        color="black",
    )
    mock_savefig.assert_called_once_with("burndown_chart.png")
