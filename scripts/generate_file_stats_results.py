"""Script for generating statistics about the eval.ai data provided."""
from itertools import product
from pathlib import Path
from pickle import dump

from eval_ai_coverage import (
    check_inputs,
    check_filepaths,
    compute_stats,
    RESULTS_DIR,
    OPTS,
)


def main(
    data_dir='./edf',
    patient_id='2002',
    data_type='BVP',
    min_dropout=128 * 60,
):
    """TODO

    Args:
        data_dir: The directory containing the data (`'./edf_sample'` for testing).
        patient_id: The patient ID to process.
        data_type: The data type to process.
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
    check_inputs(vars=locals().items())
    filepaths, dodgy_filepaths = check_filepaths(data_dir, patient_id, data_type)

    print("Calulating file statistics from data...")
    filestats, coverage, dropouts = compute_stats(filepaths, min_dropout)

    print("Saving results...")
    output_filename = f'{patient_id}_{data_type.lower()}_coverage'
    results = {
        'filestats': filestats,
        'filepaths': filepaths,
        'dodgy_filepaths': dodgy_filepaths,
        'coverage': coverage,
        'dropouts': dropouts,
        'output_filename': output_filename,
        'data_dir': data_dir,
        'patient_id': patient_id,
        'data_type': data_type,
        'min_dropout': min_dropout,
    }

    fp = Path(RESULTS_DIR) / Path(output_filename + '.pkl')
    if not fp.parent.exists():
        fp.parent.mkdir(parents=True)

    with open(str(fp), 'wb') as f:
        dump(results, f)

    return results


if __name__ == '__main__':

    # TEST
    # DATA_DIR = './edf_sample'
    # PATIENT_IDS = ['2002']
    # DATA_TYPES = ['BVP']

    # FULL SET
    DATA_DIR = './edf'
    PATIENT_IDS = OPTS['patient_id']
    DATA_TYPES = OPTS['data_type']

    all_results = []
    for pid, dtype in product(PATIENT_IDS, DATA_TYPES):
        print(f'-------- Processing patient {pid} ({dtype})')
        results = main(data_dir=DATA_DIR, patient_id=pid, data_type=dtype)
        all_results.append(results)

