from pathlib import Path
from typing import List, Tuple, Optional
from datetime import datetime

import numpy as np
import matplotlib.pyplot as plt


def plot_results(
    coverage_labels,
    dropout_labels,
    start_time_key,
) -> Tuple[plt.Figure, plt.Axes]:
    """Plot results.

    Args:
        coverage_labels: List of tuples containing coverage labels.
        dropout_labels: List of tuples containing dropout labels.
        start_time_key: Key for start time.

    Returns:
        Pyplot figure and axis.
    """
    fig, ax = plt.subplots(figsize=(18, 8))
    width = 0.98  # the width of the bars: can also be len(x) sequence
    n_bars = len(set(get_ax_labels(coverage_labels + dropout_labels)))
    max_val = max(label[1] + label[2]
                  for label in coverage_labels + dropout_labels)

    x_lim = (-1.1 * width / 2, n_bars - 1 + 1.1 * width / 2)
    y_lim = (0, max(2.5 * 24, 1.1 * max_val / (60 * 60)))

    day_in_hr = 24
    ax.plot(x_lim, [1 * day_in_hr, 1 * day_in_hr], 'k--')
    ax.plot(x_lim, [2 * day_in_hr, 2 * day_in_hr], 'k--')

    if len(coverage_labels) > 0:
        print("  Plotting coverage..")
        ax = plot_labels(
            coverage_labels,
            ax,
            color='g',
            alpha=0.5,
            legend='COVERAGE',
            width=width,
        )

    if len(dropout_labels) > 0:
        print("  Plotting dropouts..")
        ax = plot_labels(
            dropout_labels,
            ax,
            color='r',
            alpha=0.5,
            legend='DROPOUT',
            width=width,
        )

    ax.tick_params(axis='x', labelrotation=-90)
    ax.legend()
    ax.set_xlim(x_lim)
    ax.set_ylim(y_lim)

    if start_time_key == 'time_edf':
        ax.set_xlabel('Date from EDF file')
    elif start_time_key == 'time_fp':
        ax.set_xlabel('Date from directory')

    ax.set_ylabel('Hours since 00:00 of date (UTC)')
    return fig, ax


def plot_labels(
    labels: List[Tuple[Path, float, float]],
    ax: plt.Axes,
    legend: Optional[str] = None,
    color: Optional[str] = None,
    alpha: float = 0.5,
    width: float = 0.8,
) -> plt.Axes:
    """Plots labels on an axis.

    Args:
        labels: List of tuples containing labels (filepath, start time, duration).
        ax: Axis to plot on.
        legend: Legend to use.
        color: Color to use.
        alpha: Alpha to use.
        width: Width of bars.

    Returns:
        Axis with labels plotted.
    """
    ax_labels = get_ax_labels(labels)
    bar1 = np.array([label[1] for label in labels])  # start time (seconds)
    bar2 = np.array([label[2] for label in labels])  # duration (seconds)

    sec_in_hr = 3600

    ax.bar(
        ax_labels,
        bar2 / sec_in_hr,
        width,
        bottom=bar1 / sec_in_hr,
        label=legend,
        color=color,
        alpha=alpha,
    )
    ax.set_ylim(0, (max(bar1) + max(bar2)) / (sec_in_hr) * 1.1)
    return ax


def get_ax_labels(
    labels: List[Tuple[Path, float,
                       float]], ) -> List[Tuple[str, float, float]]:
    """Get labels from a list of tuples.

    Args:
        labels: List of tuples containing labels (filepath, start time, duration).

    Returns:
        List of strings to plot on the x axis.
    """
    return [
        datetime.fromtimestamp(int(label[0].parent.stem)).strftime('%d-%m-%Y')
        for label in labels
    ]
