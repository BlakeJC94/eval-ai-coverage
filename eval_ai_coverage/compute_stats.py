from pathlib import Path
from datetime import datetime, date
from pytz import utc, timezone
from pickle import dump
from typing import List, Tuple, Dict, Any

import pandas as pd
import numpy as np
import mne
from tqdm import tqdm


def compute_stats(
    filepaths,
    min_dropout=128 * 10,
):
    """Computes stats for a list of filepaths.

    Args:
        filepaths: List of filepaths to get data stats for.
        dropouts_and_data_stats: Whether to compute data stats.
        min_dropout: Minimum dropout length to be included.

    Returns:
        TODO

    """
    _log_level = mne.set_log_level(False)

    if min_dropout >= 0:
        print("Computing data stats as well, this will take longer to process")

    all_stats, all_coverage, all_dropouts = [], [], []
    for filepath in tqdm(filepaths):
        file = mne.io.read_raw_edf(str(filepath))

        # Compute metadata stats
        time_fp = datetime.fromtimestamp(int(filepath.parent.stem))
        stats = {
            'filepath': filepath,
            'time_fp': time_fp,  # Only some of these times are actually UTC?
            **get_metadata_stats(file),
        }

        # Compute coverage label
        coverage = {
            'filepath': filepath,
            'time_edf': stats['time_edf'],
            'time_fp': stats['time_fp'],
            'label_start': 0,
            'label_duration': stats['duration'],
        }

        if min_dropout >= 0:
            data, times = file.get_data(), file.times
            stats = {**stats, **get_data_stats(data)}

            file_dropouts = get_file_dropouts(data[0, :])
            for start_index, end_index in zip(*file_dropouts):
                dropout_duration = times[end_index] - times[start_index]
                if dropout_duration > min_dropout:
                    dropouts = {
                        'filepath': filepath,
                        'time_edf': stats['time_edf'],
                        'time_fp': stats['time_fp'],
                        'label_start': times[start_index],
                        'label_duration': dropout_duration,
                    }
                    all_dropouts.append(dropouts)

        all_stats.append(stats)
        all_coverage.append(coverage)

    filestats = pd.DataFrame.from_dict(all_stats)
    coverage = pd.DataFrame.from_dict(all_coverage)
    dropouts = pd.DataFrame.from_dict(all_dropouts)
    return filestats, coverage, dropouts


def get_metadata_stats(file: mne.io.Raw, ) -> pd.DataFrame:
    """Gets metadata stats for a list of filepaths.

    According to Daniel, the times on the EDF files are local time. I'm guessing this is US/Central
    time, but I'm not 100% sure.

    Args:
        file: EDF file object to get metadata stats for.
        apply_edf_tz: Whether to apply the timezone info to the edf times. If False, tzinfo will be
            removed.

    Returns:
        Dict with metadata stats.
    """
    time_edf = file.info.get('meas_date').replace(
        tzinfo=timezone('US/Central'))
    time_edf_utc = time_edf.astimezone(utc)

    stats = {
        'time_edf': time_edf,
        'time_edf_utc': time_edf_utc,
        'duration': (file.times[-1] - file.times[0]),
        'srate': file.info.get('sfreq'),
        'nchan': file.info.get('nchan'),
        'nsample': file.n_times,
    }
    return stats


def get_data_stats(
    data: np.array,
) -> Tuple[pd.DataFrame, Dict[Path, List[Tuple[int, int]]]]:
    """Gets data stats for a list of filepaths.

    Args:
        data: EDF data output of `mne.io.read_raw_edf(filepath).get_data()`.

    Returns:
        Dict with data stats.
    """
    data_min, data_max = np.min(data.flat), np.max(data.flat)
    data_range = data_max - data_min

    stats = {
        'nan_prop': np.sum(np.isnan(data[0, :])) / len(data[0, :]),
        'std': np.std(data.flat),
        'mean': np.mean(data.flat),
        'min': data_min,
        'max': data_max,
        'range': data_range,
    }
    return stats


def get_file_dropouts(data: np.array) -> List[Tuple[float, float]]:
    """Calculates dropouts (constant sections, after mapping NaNs to 0) in a data array.

    Args:
        data: 1D array of data from `mne.io.read_raw_edf(filepath).get_data()`.

    Returns:
        Dropout start/end indices as arrays.
    """
    assert len(data.shape) == 1, "Data must be 1D"

    data[np.isnan(data)] = 0
    diffs = np.diff(data, prepend=np.nan)  # diffs[i] is data[i] - data[i-1]
    const = (diffs == 0)

    if not np.any(const):
        return []

    changes = np.argwhere(np.diff(const) != 0).flatten()
    starts, ends = changes[::2], changes[1::2] + 1

    # Add the last end index when there's a dropout at the end of the file
    ends = np.append(ends, len(data) - 1) if len(ends) < len(starts) else ends
    return starts, ends
