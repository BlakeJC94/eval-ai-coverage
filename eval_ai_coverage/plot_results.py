from pathlib import Path
from typing import List, Tuple, Optional
from datetime import datetime

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

DAY_IN_HR = 24


def plot_results(
    coverage: pd.DataFrame,
    dropouts: pd.DataFrame,
    figsize: Tuple[float, float] = (18, 8)
) -> Tuple[plt.Figure, plt.Axes]:
    """Plot results.

    Args:
        coverage: Coverage dataframe.
        dropouts: Dropouts dataframe.

    Returns:
        Pyplot figure and axis of coverage and dropouts.
    """
    fig, ax = plt.subplots(figsize=figsize)
    width = 0.95  # the width of the bars: can also be len(x) sequence

    # get bounds of plot
    all_bars = pd.concat([coverage, dropouts]).sort_values(by=['ax_index'])
    # minimum_space = all_bars['ax_index'].sort_values().diff().min()

    start_index = all_bars['ax_index'].min()
    end_index = all_bars['ax_index'].max()
    max_val = all_bars[['start_time', 'duration']].sum(axis=1).max()

    x_lim = (start_index - 1.1 * width / 2, end_index + 1.1 * width / 2)
    y_lim = (0, max(2.5 * 24, 1.1 * max_val / (60 * 60)))

    ax.plot(x_lim, [1 * DAY_IN_HR, 1 * DAY_IN_HR], 'k--')
    ax.plot(x_lim, [2 * DAY_IN_HR, 2 * DAY_IN_HR], 'k--')

    if len(coverage) > 0:
        print("  Plotting coverage..")
        ax = plot_bars(
            coverage,
            ax,
            color='g',
            alpha=0.5,
            legend='COVERAGE',
            width=width,
        )

    if len(dropouts) > 0:
        print("  Plotting dropouts..")
        ax = plot_bars(
            dropouts,
            ax,
            color='r',
            alpha=0.5,
            legend='DROPOUT',
            width=width*0.9,
        )

    # Set all x-axis guff
    ticks = all_bars['ax_index']
    labels = all_bars['filepath'].apply(lambda x: x.parent.stem)
    ax.set_xticks(ticks, labels)
    ax.tick_params(axis='x', labelrotation=-90)
    ax.set_xlabel('Data directory timestamp')

    # fig.set_size_inches(figsize[0], figsize[1]/minimum_space)

    ax.legend()
    ax.set_xlim(x_lim)
    ax.set_ylim(y_lim)
    return fig, ax


def plot_bars(
    labels: List[Tuple[Path, float, float]],
    ax: plt.Axes,
    legend: Optional[str] = None,
    color: Optional[str] = None,
    alpha: float = 0.5,
    width: float = 0.8,
) -> plt.Axes:
    """Plots time labels as bar graphs on an axis.

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
    labels = labels.sort_values(by=['ax_index'])

    ax_index = labels['ax_index']
    offset = labels['start_time']  # start time (seconds)
    duration = labels['duration']  # duration (seconds)

    sec_in_hr = 3600

    ax.bar(
        ax_index,
        duration / sec_in_hr,
        width,
        bottom=offset / sec_in_hr,
        label=legend,
        color=color,
        alpha=alpha,
    )
    return ax
