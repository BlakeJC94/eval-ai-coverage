import warnings
from pathlib import Path
from typing import List, Dict, Tuple, Optional

import mne

from .globals import RESULTS_DIR, OPTS

def check_filepaths(
        data_dir: str,
        patient_id: str,
        data_type: str,
    ):
    """TODO."""
    all_filepaths = get_edf_filepaths(data_dir, patient_id, data_type)
    filepaths, dodgy_filepaths = filter_dodgy_files(all_filepaths)
    write_dodgy_files(dodgy_filepaths, patient_id, data_type)
    return filepaths, dodgy_filepaths


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


def write_dodgy_files(
    dodgy_filepaths: Dict[Path, str],
    patient_id: str,
    data_type: str,
) -> None:
    """Writes dodgy files to a file.

    Args:
        dodgy_filepaths: Dictionary of dodgy files and errors.
        results_dir: Path to the directory to write the dodgy files to.
    """
    output_filename = f'{patient_id}_{data_type.lower()}_dodgy_files.txt'

    results_dir = Path(RESULTS_DIR).expanduser()
    results_dir.mkdir(exist_ok=True)
    results_filepath = results_dir / output_filename

    with open(str(results_filepath), 'w') as f:
        if len(dodgy_filepaths) == 0:
            f.write('No dodgy files found!')
        else:
            for filepath, error in dodgy_filepaths.items():
                f.write(f'{filepath},{error}\n\n')

