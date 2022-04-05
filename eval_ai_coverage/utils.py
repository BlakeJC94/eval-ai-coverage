import warnings
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Union
from pickle import load

import mne

from .globals import RESULTS_DIR, OPTS


def check_inputs(vars):
    for k, v in vars:
        if k in OPTS.keys():
            assert v in OPTS[k], f"Invalid {k} = {v}"


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
    for k, v in locals().items():
        if k in OPTS.keys():
            assert v in OPTS[k], f"Invalid {k} = {v}"

    output_filename = f'{patient_id}_{data_type.lower()}_coverage'
    fp = Path(RESULTS_DIR) / Path(output_filename + '.pkl')

    if not fp.exists():
        print(f"No results found for {patient_id}")
        return {}

    print(f"Loading results from {fp}")
    with open(fp, 'rb') as f:
        results = load(f)

    return results
