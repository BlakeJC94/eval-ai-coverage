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
    OPTS,
    PLOT_DIR,
    RESULTS_DIR,
)


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
        min_dropout: The minimum number of seconds to consider a dropout. -1 disables dropout
            detection

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
    all_stats, all_coverage, all_dropouts = compute_stats(
        filepaths,
        apply_edf_tz=True,
        start_time_key=start_time_key,
        min_dropout=min_dropout,
    )
    filestats = pd.DataFrame.from_dict(all_stats)
    coverage = pd.DataFrame.from_dict(all_coverage)
    dropouts = pd.DataFrame.from_dict(all_dropouts)

    print("Saving results...")
    output_filename = f'{patient_id}_coverage_{data_type.lower()}'
    results = {
        'filestats': filestats,
        'filepaths': filepaths,
        'dodgy_filepaths': dodgy_filepaths,
        'duplicate_filepaths': duplicate_filepaths,
        'coverage': coverage,
        'dropouts': dropouts,
        'output_filename': output_filename,
        'data_dir': data_dir,
        'patient_id': patient_id,
        'data_type': data_type,
        'start_time_key': start_time_key,
        'min_dropout': min_dropout,
    }

    fp = Path(RESULTS_DIR) / Path(output_filename + '.pkl')
    if not fp.parent.exists():
        fp.parent.mkdir(parents=True)

    with open(str(fp), 'wb') as f:
        dump(results, f)

    return results


if __name__ == '__main__':
    data_dir = './edf'
    patient_id = '2002'
    data_type = 'BVP'

    _results = main(data_dir=data_dir, patient_id=patient_id, data_type=data_type)  # Test
    # results = main(data_dir='./edf')  # Test
    # results = main(data_dir='/home/blake/Workspace/scratch/evalai/edf_sample')  # Test

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

    ax.set_title(title_str)
    plt.tight_layout()

    fp = Path(PLOT_DIR) / Path(output_filename + '.png')
    if not fp.parent.exists():
        fp.parent.mkdir(parents=True)

    plt.savefig(str(fp))
    plt.show()
