from itertools import product
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

from eval_ai_coverage import (
    plot_coverage_bars,
    load_results,
    PLOT_DIR,
    SPLIT,
)

def main(
    patient_id='2002',
    data_type='BVP',
):
    """TODO"""
    results = load_results(patient_id, data_type)

    coverage = results['coverage']
    dropouts = results['dropouts']
    min_dropout = results['min_dropout']
    output_filename = results['output_filename']
    coverage = results['coverage']

    print("Plotting results...")
    _fig, ax = plot_coverage_bars(
        coverage,
        dropouts,
        figsize=(36, 8),
    )

    ax.set_ylabel('Hours since 00:00 of date from EDF file')

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

    # TEST
    PATIENT_IDS = ['2002']
    DATA_TYPES = ['BVP']

    # PATIENT_IDS = ['1110', '1869', '1876', '1904', '1965', '2002']
    # DATA_TYPES = ['ACC', 'BVP', 'EDA', 'HR', 'TEMP']

    for pid, dtype in product(PATIENT_IDS, DATA_TYPES):
        print(f'-------- Processing patient {pid} ({dtype})')
        main(patient_id=pid, data_type=dtype)
        plt.show()
