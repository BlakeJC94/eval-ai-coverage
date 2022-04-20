import warnings
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Union
from pickle import load

import mne

from .globals import INTERIM_PATH, PATIENT_IDS, DTYPES


def load_results(
    patient_id: str = '2002',
    data_type: str = 'BVP',
) -> dict:
    """Loads results from a pickle file.

    Args:
        results_filepath: Path to the pickle file.

    Returns:
        Dictionary of results. See docs for `main` for more info.
    """
    assert patient_id in PATIENT_IDS, "Invalid patient_id"
    assert data_type in DTYPES, "Invalid data_type"

    output_filename = f'{patient_id}_{data_type.lower()}_coverage'
    fp = Path(INTERIM_PATH) / Path(output_filename + '.pkl')

    if not fp.exists():
        print(f"No results found for {patient_id}")
        return {}

    print(f"Loading results from {fp}")
    with open(fp, 'rb') as f:
        results = load(f)

    return results
