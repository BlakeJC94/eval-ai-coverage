"""Script for generating statistics about the eval.ai data provided."""

from pathlib import Path
from pickle import dump

import pandas as pd
import matplotlib.pyplot as plt

from eval_ai_coverage import (
    plot_results,
    compute_stats,
    get_edf_filepaths,
    filter_dodgy_files,
    get_duplicates,
    load_results,
)

OPTS = {
    'data_dir': ['./edf', './edf_sample'],
    'patient_id': ['1110', '1869', '1876', '1904', '1965', '2002'],
    'data_type': ['ACC', 'BVP', 'EDA', 'HR', 'TEMP', None],
    'start_time_key': ['time_edf', 'time_fp'],
}

PLOT_DIR = './output/plots'
RESULTS_DIR = './output/results'

# EXPECTED DODGY FILES for 2002 training
# - edf/2002/training/1611462137/Empatica-HR.edf,
# - edf/2002/training/1611462137/Empatica-BVP.edf,
# - edf/2002/training/1611658350/Empatica-HR.edf,
# - edf/2002/training/1611658350/Empatica-BVP.edf


def main(
    data_dir='./edf',
    patient_id='2002',
    data_type='BVP',
    start_time_key='time_edf',
    dropouts_and_data_stats=True,
    min_dropout=128 * 60,
):
    """Main entry point for the script.

    A "Label" refers to a data structure given by a tuple of the form:
        `(filepath, start time (seconds), duration (seconds))`.

    Note that the `start time` is the number of seconds between the recording start time and 00:00
    of the date associated with the recording start time. This can either be the start time of the
    EDF file (`'time_edf'`) or the time of the containing directory (`'time_fp'`).

    This function will generate a bar plot of the coverage labels (and dropout labels) for the
    selected data type and patient ID. Plots and results are saved to the output directory.

    Args:
        data_dir: The directory containing the data (`'./edf_sample'` for testing).
        patient_id: The patient ID to process.
        data_type: The data type to process.
        start_time_key: The key to use for the start time of labels.
        dropouts_and_data_stats: Whether to compute dropouts.
        min_dropout: The minimum number of seconds to consider a dropout.

    Returns:
        Dict containing the following keys:
            - 'filepaths': List of valid edf filepaths,
            - 'filestats': Pandas DataFrame containing stats about the data
            - 'dodgy_filepaths': Dict mapping filepaths to error messages,
            - 'duplicate_filepaths': List of filepaths that share the same "timestamp" on path,
            - 'coverage_labels': List of coverage labels,
            - 'dropout_labels': List of dropout labels (longer than `min_dropout`),
    """

    # Verify the data parameters passed in are valid
    for k, v in locals().items():
        if k in OPTS.keys():
            assert v in OPTS[k], f"Invalid {k} = {v}"

    all_filepaths = get_edf_filepaths(
        data_dir,
        patient_id,
        data_type,
    )
    filepaths, dodgy_filepaths = filter_dodgy_files(all_filepaths)
    duplicate_filepaths = get_duplicates(filepaths)

    print("Calulating file statistics from data...")
    all_stats, coverage_labels, dropout_labels = compute_stats(
        filepaths,
        apply_edf_tz=True,
        dropouts_and_data_stats=dropouts_and_data_stats,
        start_time_key=start_time_key,
        min_dropout=min_dropout,
    )
    filestats = pd.DataFrame.from_dict(all_stats)
    filestats = filestats.set_index('filepath').sort_index()

    print("Plotting results...")
    fig, ax = plot_results(
        coverage_labels,
        dropout_labels,
        start_time_key=start_time_key,
    )
    title_str = f'Coverage of {data_type.lower()} files for patient {patient_id}'
    if dropouts_and_data_stats:
        title_str += f', min dropout = {min_dropout/128} sec'

    ax.set_title(title_str)
    plt.tight_layout()

    print("Saving results...")
    output_filename = f'{patient_id}_coverage_{data_type.lower()}'
    results = {
        'filestats': filestats,
        'filepaths': filepaths,
        'dodgy_filepaths': dodgy_filepaths,
        'duplicate_filepaths': duplicate_filepaths,
        'coverage_labels': coverage_labels,
        'dropout_labels': dropout_labels,
    }
    plot_filepath = Path(PLOT_DIR) / Path(output_filename + '.png')
    results_filepath = Path(RESULTS_DIR) / Path(output_filename + '.pkl')

    for fp in [plot_filepath, results_filepath]:
        if not fp.parent.exists():
            fp.parent.mkdir(parents=True)

    plt.savefig(str(plot_filepath))
    with open(str(results_filepath), 'wb') as f:
        dump(results, f)

    return results


if __name__ == '__main__':
    results = main(data_dir='./edf_sample')  # Test
    plt.show()
