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
    apply_edf_tz=False,
    dropouts_and_data_stats=True,
    start_time_key='time_edf',
    min_dropout=128 * 10,
):
    """Computes stats for a list of filepaths.

    Args:
        filepaths: List of filepaths to get data stats for.
        apply_edf_tz: Whether to apply the timezone info to the edf times. If False, tzinfo will be
            removed.
        dropouts_and_data_stats: Whether to compute data stats.
        start_time_key: The key in the metadata stats dict to use as the start time.
        min_dropout: Minimum dropout length to be included.

    """
    if dropouts_and_data_stats:
        print("Computing data stats as well, this will take longer to process")

    _log_level = mne.set_log_level(False)
    all_stats = []
    dropout_labels, coverage_labels = [], []
    for filepath in tqdm(filepaths):

        file = mne.io.read_raw_edf(str(filepath))

        time_fp = datetime.fromtimestamp(int(filepath.parent.stem))
        stats = {
            'filepath': filepath,
            'time_fp': time_fp,  # Only some of these times are actually UTC?
            **get_metadata_stats(file, apply_edf_tz=apply_edf_tz),
        }
        stats['time_diff_fp_edfs'] = stats['time_fp'] - stats[
            'time_edf'].replace(tzinfo=None)

        coverage = get_coverage(
            stats,
            start_time=stats[start_time_key].replace(tzinfo=None),
        )
        coverage_labels.append((filepath, *coverage))

        if dropouts_and_data_stats:
            data, times = file.get_data(), file.times
            stats = {**stats, **get_data_stats(data)}
            stats['range'] = stats['max'] - stats['min']

            dropouts = get_dropouts(
                data[0, :],
                times,
                start_time=stats[start_time_key].replace(tzinfo=None),
                min_dropout=min_dropout,
            )
            if len(dropouts) > 0:
                dropouts = [(filepath, *dropout) for dropout in dropouts]
                dropout_labels.extend(dropouts)

        all_stats.append(stats)

    return all_stats, coverage_labels, dropout_labels


def get_metadata_stats(
    file: mne.io.Raw,
    apply_edf_tz: bool = False,
) -> pd.DataFrame:
    """Gets metadata stats for a list of filepaths.

    According to Daniel, the times on the EDF files are local time. I'm guessing this is US/Central
    time, but I'm not 100% sure.

    Args:
        file: EDF file object to get metadata stats for.
        apply_tz: Whether to apply the timezone info to the edf times. If False, tzinfo will be
            removed.

    Returns:
        Dict with metadata stats.
    """
    stats = {
        'time_edf': file.info.get('meas_date').replace(tzinfo=None),
        'duration': (file.times[-1] - file.times[0]),
        'srate': file.info.get('sfreq'),
        'nchan': file.info.get('nchan'),
        'nsample': file.n_times,
    }

    if apply_edf_tz:
        stats['time_edf'] = stats['time_edf'].replace(
            tzinfo=timezone('US/Central'))

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
    stats = {
        'nan_prop': np.sum(np.isnan(data[0, :])) / len(data[0, :]),
        'std': np.std(data.flat),
        'mean': np.mean(data.flat),
        'min': np.min(data.flat),
        'max': np.max(data.flat),
    }

    return stats


def get_coverage(
    stats: Dict[str, Any],
    start_time: date,
) -> List[Tuple[float, float]]:
    """Gets the coverage of the data in a file.

    Args:
        stats: Dictionary of stats for a file.
        start_time: The start time of the file, date used for zero point

    Returns:
        Tuple of (start_time, duration) of the coverage.
    """
    zero_point = datetime.combine(start_time.date(), datetime.min.time())
    file_start = (start_time - zero_point).total_seconds()
    duration = stats['duration']
    return (file_start, duration)


def get_dropouts(
    data: np.array,
    times: np.array,
    start_time: datetime,
    min_dropout: int = 0,
) -> List[Tuple[float, float]]:
    """Calculates dropouts (constant sections, after mapping NaNs to 0) in a data array.

    Args:
        data: 1D array of data from `mne.io.read_raw_edf(filepath).get_data()`.
        times: Vector of times from `mne.io.read_raw_edf(filepath).times`.
        start_time: The start time of the file, date used for zero point
        min_dropout: Minimum dropout length to be included.

    Returns:
        List of tuples of (start_time, duration) of the dropouts greater than `min_dropout`.
    """
    assert len(data.shape) == 1, "Data must be 1D"

    zero_point = datetime.combine(start_time.date(), datetime.min.time())
    start_time = (start_time - zero_point).total_seconds()

    data[np.isnan(data)] = 0
    diffs = np.diff(data, prepend=np.nan)  # diffs[i] is data[i] - data[i-1]
    const = (diffs == 0)

    if not np.any(const):
        return []

    changes = np.where(np.diff(const) != 0)[0]
    starts, ends = changes[::2], changes[1::2] + 1

    # Add the last end index when there's a dropout at the end of the file
    ends = np.append(ends, len(data) - 1) if len(ends) < len(starts) else ends

    dropouts = [(start_time + times[start], times[end] - times[start])
                for start, end in zip(starts, ends)
                if end - start > min_dropout]

    return dropouts
