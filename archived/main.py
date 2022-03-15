
from copy import copy
from pathlib import Path
from datetime import datetime, timedelta

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mne

from tools import (
    filter_dodgy_files,
    get_metadata_stats,
    get_dropouts_and_data_stats,
)


DATA_DIR = './edf'
assert DATA_DIR in ['./edf', './edf_sample']

PATIENT_ID = '2002'
assert PATIENT_ID in ['1110', '1869', '1876', '1904', '1965', '2002']

DATA_GROUP = 'training'
assert DATA_GROUP in ['training', 'testing', 'all']

DATA_TYPE = 'ACC'
assert DATA_TYPE in ['ACC', 'BVP', 'EDA', 'HR', 'TEMP', 'ALL']


# TODO:
# - Add more docs about program outputs
# - Add argparser?
# - Add simple logging?

def main():
    """Entry point for the program."""
    data_path = Path(DATA_DIR).expanduser() / PATIENT_ID / DATA_GROUP

    # get listing of all edf files
    filepaths = [i for i in data_path.glob('**/*') if i.suffix == '.edf']
    all_filepaths = copy(filepaths)

    assert all(filepath.stem[:9] == 'Empatica-' for filepath in filepaths), \
        'Invalid filepaths present'


    print(f"Filtering for data type: {DATA_TYPE}")
    filepaths = [
        filepath for filepath in filepaths if DATA_TYPE in filepath.stem
    ]
    print(f"{len(filepaths)} {DATA_TYPE} files found")


    print("Filtering dodgy files...")
    filepaths, dodgy_filepaths = filter_dodgy_files(filepaths)
    print(f"{len(dodgy_filepaths)} dodgy files removed")

    # EXPECTED DODGY FILES for 2002 training
    # - edf/2002/training/1611462137/Empatica-HR.edf,
    # - edf/2002/training/1611462137/Empatica-BVP.edf,
    # - edf/2002/training/1611658350/Empatica-HR.edf,
    # - edf/2002/training/1611658350/Empatica-BVP.edf


    filestats_dict = {'filepath': filepaths}

    print("Calulating file statistics from metadata...")
    # TODO figure out timezone info (which region?)
    filestats_dict = get_metadata_stats(filestats_dict)

    print("Calulating file statistics from data...")
    filestats_dict, dropouts = get_dropouts_and_data_stats(filestats_dict)
    # TODO add dropouts calculation


    # convert to DataFrame and calculate more stats
    filestats = pd.DataFrame().from_dict(filestats_dict)

    filestats = filestats.sort_values(by='filepath').set_index('filepath')
    filestats['time_diff_fp_edfs'] = filestats['time_fp'] - filestats['time_edf']
    filestats['range'] = filestats['max'] - filestats['min']


    # TODO run some additional filters, durations? range? std? etc


    # Ficgure out how to represent labels couple with filepaths and a seamless way to plot a
    # collection of them


if __name__ == '__main__':
    main()
