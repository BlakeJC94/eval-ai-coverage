from pathlib import Path
from typing import List, Tuple, Optional
from datetime import datetime

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from ea_coverage.vis import add_bars, add_ax_index
from .globals import SPLIT, OUTPUT_PATH
from .utils import load_results


def plot_bars(
        patient_id: str,
        data_type: str,
        figsize: Tuple[float, float] = (18, 8),
) -> Tuple[plt.Figure, plt.Axes]:
    """Plot results.

    Args:
        patient_id: Patient ID.
        data_type: Data type.
    """
    _, ax = plt.subplots(figsize=figsize)
    width = 0.95  # the width of the bars: can also be len(x) sequence

    print(f"Loading results {patient_id}, {data_type}...")
    results = load_results(patient_id, data_type)
    coverage = results['coverage']
    dropouts = results['dropouts']
    min_dropout = results['min_dropout']

    # Create x-axis index for each bar
    coverage = add_ax_index(coverage)
    dropouts = add_ax_index(dropouts)

    # get bounds of plot
    all_bars = pd.concat([coverage, dropouts]).sort_values(by=['ax_index'])

    start_index = all_bars['ax_index'].min()
    end_index = all_bars['ax_index'].max()
    max_val = all_bars[['label_start', 'label_duration']].sum(axis=1).max()

    x_lim = (start_index - 1.1 * width / 2, end_index + 1.1 * width / 2)
    y_lim = (0, max(2.5 * 24, 1.1 * max_val / (60 * 60)))

    ax.plot(x_lim, [1 * DAY_IN_HR, 1 * DAY_IN_HR], 'k--')
    ax.plot(x_lim, [2 * DAY_IN_HR, 2 * DAY_IN_HR], 'k--')

    if len(coverage) > 0:
        print("  Plotting coverage..")
        ax = add_bars(
            coverage,
            ax,
            color='g',
            alpha=0.5,
            legend='COVERAGE',
            width=width,
        )

    if len(dropouts) > 0:
        print("  Plotting dropouts..")
        ax = add_bars(
            dropouts,
            ax,
            color='r',
            alpha=0.5,
            legend='DROPOUT',
            width=width * 0.9,
        )

    # Set all x-axis guff
    ticks = all_bars['ax_index']
    labels = all_bars['filepath'].apply(lambda x: x.parent.stem)
    ax.set_xticks(ticks, labels)
    ax.tick_params(axis='x', labelrotation=-90)
    ax.set_xlabel('Data directory timestamp')

    ax.legend()
    ax.set_xlim(x_lim)
    ax.set_ylim(y_lim)

    ax.set_ylabel('Hours since 00:00 of date from EDF file')

    title_str = f'Coverage of {data_type.lower()} files for patient {patient_id}'
    if min_dropout >= 0:
        title_str += f', min dropout = {min_dropout/128} sec'

    testing_start = int(SPLIT[patient_id]) / (60*60*24)
    ax.plot([testing_start, testing_start], [0, 3*24], 'k-', alpha=0.25)
    ax.set_title(title_str)
    plt.tight_layout()

    fp = Path(OUTPUT_PATH) / f'{patient_id}_{data_type.lower()}_coverage.png'
    fp.parent.mkdir(parents=True, exist_ok=True)

    plt.savefig(str(fp))
