import warnings
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Union
from pickle import load

import mne


def get_edf_filepaths(
    data_dir: str,
    patient_id: str,
    data_type: Optional[str] = None,
) -> List[Path]:
    """Gets a list of filepaths to EDF files for a patient.

    Args:
        data_dir: Path to the directory containing the patient's data.
        patient_id: Patient ID.
        data_type: Type of data to get.

    Returns:
        List of filepaths to EDF files.
    """
    data_path = Path(data_dir).expanduser() / patient_id
    assert data_path.exists(), f"{data_path} does not exist!"

    # get listing of all edf files (edfs that are not hidden files)
    filepaths = sorted([
        i for i in data_path.glob('**/*')
        if i.suffix == '.edf' and i.stem[0] != '.'
    ])

    # ensure all the EDF files are Empatica files
    assert all(filepath.stem[:9] == 'Empatica-' for filepath in filepaths), \
        'Invalid filepaths present'

    # Filter list of files further if `data_type` is specified
    if data_type is not None:
        print(f"Filtering for data type: {data_type}")
        filepaths = [
            filepath for filepath in filepaths if data_type in filepath.stem
        ]
    else:
        data_type = 'all'

    print(f"{len(filepaths)} files found ({data_type}) for patient {patient_id}")
    return filepaths


def filter_dodgy_files(
    all_filepaths: List[Path],
) -> Tuple[List[Path], Dict[Path, str]]:
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
        for filepath in all_filepaths:
            try:
                file = mne.io.read_raw_edf(str(filepath))
                if file.n_times == 0:
                    raise ValueError('No n_times in file')
                if len(file.ch_names) == 0:
                    raise ValueError('No ch_names')
                # Add additional error criteria here if needed

            except Exception as e:
                print(f"  {filepath} is dodgy: {e}")
                dodgy_filepaths[filepath] = str(e)

    mne.set_log_level(old_log_level)
    filepaths = [fp for fp in all_filepaths if fp not in dodgy_filepaths]
    return filepaths, dodgy_filepaths


def get_duplicates(filepaths: List[Path]) -> List[Path]:
    """Gets a list of duplicate directories in the filepaths.

    Args:
        filepaths: List of filepaths to check.

    Returns:
        List of duplicate directories.
    """
    dirs = [filepath.parent.stem for filepath in filepaths]
    duplicates = {dir: dirs.count(dir) for dir in dirs if dirs.count(dir) > 1}
    duplicate_filepaths = sorted([
        filepath for filepath in filepaths
        if filepath.parent.stem in duplicates.keys()
    ])

    if len(duplicate_filepaths) > 0:
        print(f"Duplicate directories found:")
        for filepath in duplicate_filepaths:
            print(f"  {filepath.parent.stem} : {filepath}")
    else:
        print('No duplicate directories found')

    return duplicate_filepaths


def load_results(
    results_filepath: Union[Path, str],
) -> dict:
    """Loads results from a pickle file.

    Args:
        results_filepath: Path to the pickle file.

    Returns:
        Dictionary of results. See docs for `main` for more info.
    """
    return load(str(results_filepath))

