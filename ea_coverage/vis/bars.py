from pathlib import Path
from typing import List, Tuple, Optional

import pandas as pd
import matplotlib.pyplot as plt

SEC_IN_HR = 60 * 60
SEC_IN_DAY = 60 * 60 * 24


def add_bars(
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
    duration = labels['label_duration']  # duration (seconds)

    ax.bar(
        ax_index,
        duration / SEC_IN_HR,
        width,
        bottom=offset / SEC_IN_HR,
        label=legend,
        color=color,
        alpha=alpha,
    )
    return ax


def add_ax_index(labels: pd.DataFrame) -> pd.DataFrame:
    """Adds `ax_index` and `file_start` to the dataframe.

    Args:
        labels: Dataframe with labels.

    Returns:
        Dataframe with `ax_index` and `file_start` added.
    """
    if len(labels) == 0:
        return labels

    start_time = labels['time_edf'].dt.tz_localize(None)
    zero_point = start_time.dt.normalize()
    file_start = (start_time - zero_point).dt.total_seconds()

    labels['start_time'] = file_start + labels['label_start']
    labels['ax_index'] = labels['filepath'].apply(lambda fp: int(fp.parent.stem) / SEC_IN_DAY)
    return labels
