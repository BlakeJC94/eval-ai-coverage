from pathlib import Path
from pickle import dump

from ea_coverage.data import check_filepaths, get_coverage_dataframes
from .globals import EDF_PATH, INTERIM_PATH, PATIENT_IDS, DTYPES


def gen_stats(
    patient_id: str,
    data_type: str,
    min_dropout: int = 128 * 60,
):
    """Processes edf files for a given patient and dtype.

    Args:
        patient_id: The patient ID to process.
        data_type: The data type to process.
        min_dropout: The minimum number of seconds to consider a dropout. -1 disables dropout
            detection, 0 looks for all dropouts of any length.

    Returns:
        Dict containing the following keys:
            - 'filepaths': List of valid edf filepaths,
            - 'filestats': Pandas DataFrame containing stats about the data
            - 'dodgy_filepaths': Dict mapping filepaths to error messages,
            - 'duplicate_filepaths': List of filepaths that share the same "timestamp" on path,
            - 'coverage_labels': List of coverage labels,
            - 'dropout_labels': List of dropout labels (longer than `min_dropout`),
    """
    assert patient_id in PATIENT_IDS, "Invalid patient_id"
    assert data_type in DTYPES, "Invalid data_type"

    filepaths, dodgy_filepaths = check_filepaths(patient_id, data_type)

    print("Calulating file statistics from data...")
    filestats, coverage, dropouts = get_coverage_dataframes(filepaths, min_dropout)

    print("Saving results...")
    output_filename = f'{patient_id}_{data_type.lower()}_coverage'
    results = {
        'filestats': filestats,
        'filepaths': filepaths,
        'dodgy_filepaths': dodgy_filepaths,
        'coverage': coverage,
        'dropouts': dropouts,
        'output_filename': output_filename,
        'patient_id': patient_id,
        'data_type': data_type,
        'min_dropout': min_dropout,
    }

    fp = Path(INTERIM_PATH) / output_filename + '.pkl'
    fp.parent.mkdir(parents=True, exist_ok=True)

    with open(str(fp), 'wb') as f:
        dump(results, f)
