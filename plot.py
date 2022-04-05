from pathlib import Path

import pandas as pd
# import matplotlib
# matplotlib.use('Agg')
import matplotlib.pyplot as plt

from eval_ai_coverage import (
    plot_results,
    load_results,
    OPTS,
    PLOT_DIR,
    RESULTS_DIR,
)

SPLIT = {
    '1110': '1588104564',
    '1869': '1581299804',
    '1876': '1585623889',
    '1904': '1597843971',
    '1965': '1602740282',
    '2002': '1612150126',
}

def plot_outputs(
    patient_id='2002',
    data_type='BVP',
):
    """TODO"""
    results = load_results(patient_id, data_type)

    coverage = results['coverage']
    dropouts = results['dropouts']
    start_time_key = results['start_time_key']
    min_dropout = results['min_dropout']
    output_filename = results['output_filename']
    coverage = results['coverage']

    print("Plotting results...")
    _fig, ax = plot_results(
        coverage,
        dropouts,
        figsize=(36, 8),
    )

    if start_time_key == 'time_edf':
        ax.set_ylabel('Hours since 00:00 of date from EDF file')
    elif start_time_key == 'time_fp':
        ax.set_ylabel('Hours since 00:00 of date from directory')

    title_str = f'Coverage of {data_type.lower()} files for patient {patient_id}'
    if min_dropout >= 0:
        title_str += f', min dropout = {min_dropout/128} sec'

    testing_start = int(SPLIT[patient_id]) / (60*60*24)
    ax.plot([testing_start, testing_start], [0, 3*24], 'k-', alpha=0.25)
    ax.set_title(title_str)
    plt.tight_layout()

    fp = Path(PLOT_DIR) / Path(output_filename + '.png')
    if not fp.parent.exists():
        fp.parent.mkdir(parents=True)

    plt.savefig(str(fp))


if __name__ == '__main__':
    plot_outputs()
    plt.show()
