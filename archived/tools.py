# General structure of patient dir:
# edf/1110/
# ├── testing
# │   ├── 1588104564
# │   │   ├── Empatica-ACC.edf
# │   │   ├── Empatica-BVP.edf
# │   │   ├── Empatica-EDA.edf
# │   │   ├── Empatica-HR.edf
# │   │   └── Empatica-TEMP.edf
# │   ...
# └── training
#     ├── 1582758851
#     │   ├── Empatica-ACC.edf
#     │   ├── Empatica-BVP.edf
#     │   ├── Empatica-EDA.edf
#     │   ├── Empatica-HR.edf
#     │   └── Empatica-TEMP.edf
#     ...

import warnings
from copy import copy
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Tuple

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mne


def filter_dodgy_files(filepaths: list) -> Tuple[List, Dict[Path, str]]:
    """Filters filepaths to only contain paths with EDF files that are not dodgy.

    Requirements for non-dodgy edfs:
        - Can be opened with `mne.io.read_raw_edf` without warnings/errors
        - Has at least one channel of data
        - Has at least one sample point in the file

    Args:
        filepaths: List of filepaths to filter.

    Returns:
        List of filepaths that are not dodgy and a dictionary of dodgy files and errors.
    """
    dodgy_filepaths = {}
    old_log_level = mne.set_log_level(False)

    with warnings.catch_warnings():
        warnings.simplefilter('error')
        for filepath in filepaths:
            try:
                file = mne.io.read_raw_edf(str(filepath))
                # I can raise errors here if I want to, and it'll be caught below!
                if file.n_times == 0:
                    raise ValueError('No n_times in file')
                if len(file.ch_names) == 0:
                    raise ValueError('No ch_names')

            except Exception as e:
                print(f"{filepath} is dodgy: {e}")
                dodgy_filepaths[filepath] = str(e)
                filepaths.remove(filepath)

    mne.set_log_level(old_log_level)
    return filepaths, dodgy_filepaths


# TODO calculate coverage here?
def get_metadata_stats(filestats_dict: Dict) -> Dict:
    """TODO."""

    fields = [
        'time_fp',
        'time_edf',
        'duration',
        'srate',
        'nchan',
        'nsample',
    ]
    filestats_dict = {**filestats_dict, **{k: [] for k in fields}}

    filepaths = filestats_dict['filepaths']
    for i, filepath in enumerate(filepaths):
        print(f"  {i + 1}/{len(filepaths)}: {filepath}")
        file = mne.io.read_raw_edf(str(filepath))
        stats = {k: None for k in filestats_dict.keys() if k != 'filepath'}

        stats['time_fp'] = datetime.fromtimestamp(int(filepath.parent.stem))
        stats['time_edf'] = file.info.get('meas_date').replace(tzinfo=None)  # Thinks it's UTC?
        stats['duration'] = (file.times[-1] - file.times[0])
        stats['srate'] = file.info.get('sfreq')
        stats['nchan'] = file.info.get('nchan')
        stats['nsample'] = file.n_times

        for key, val in stats.items():
            assert val is not None, f"{key} has not been set"
            filestats_dict[key].append(val)

    return filestats_dict


def calculate_dropouts(data: np.array) -> List[Tuple[int, int]]:
    """Calculates dropouts (constant sections) in a data array."""
    assert len(data.shape) == 1, "Data must be 1D"
    differences = np.diff(data, prepend=np.nan)
    changes = np.where(np.diff((differences == 0)) != 0)[0]
    starts, ends = changes[::2], changes[1::2] + 1
    ends = np.append(ends, len(data)) if len(ends) < len(starts) else ends
    return list(zip(starts, ends))



def get_dropouts_and_data_stats(filestats_dict: Dict) -> Dict:
    """TODO."""
    fields = [
        'nan_prop',
        'std',
        'mean',
        'min',
        'max',
    ]
    filestats_dict = {**filestats_dict, **{k: [] for k in fields}}
    dropouts = [] # TODO

    filepaths = filestats_dict['filepaths']
    for i, filepath in enumerate(filepaths):
        print(f"  {i + 1}/{len(filepaths)}: {filepath}")
        file = mne.io.read_raw_edf(str(filepath))
        stats = {k: None for k in filestats_dict.keys() if k != 'filepath'}

        data = file.get_data()  # chs, times
        stats['nan_prop'] = np.sum(np.isnan(data[0,:])) / file.n_times
        stats['std'] = np.std(data.flat)
        stats['mean'] = np.mean(data.flat)
        stats['min'] = np.min(data.flat)
        stats['max'] = np.max(data.flat)

        # TODO compute dropouts by using pandas groupby method?
        dropouts[]

        for key, val in stats.items():
            assert val is not None, f"{key} has not been set"
            filestats_dict[key].append(val)

    return filestats_dict, dropouts




