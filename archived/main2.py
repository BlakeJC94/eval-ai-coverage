from copy import copy
from pathlib import Path
from datetime import datetime, timedelta
from pytz import utc

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mne

import tools

DATA_DIR = './edf_sample'
assert DATA_DIR in ['./edf', './edf_sample']

PATIENT_ID = '2002'
assert PATIENT_ID in ['1110', '1869', '1876', '1904', '1965', '2002']

DATA_GROUP = 'training'
assert DATA_GROUP in ['training', 'testing', 'all']

DATA_TYPE = 'ACC'
assert DATA_TYPE in ['ACC', 'BVP', 'EDA', 'HR', 'TEMP', None]

START_TIME_KEY = 'time_edf'
assert START_TIME_KEY in ['time_edf', 'time_fp']

# TODO:
# - Add more docs about program outputs
# - Add argparser?
# - Add simple logging?

all_filepaths = tools.get_edf_filepaths(DATA_DIR, PATIENT_ID, DATA_GROUP, DATA_TYPE)
filepaths, dodgy_filepaths = tools.filter_dodgy_files(all_filepaths)

# EXPECTED DODGY FILES for 2002 training
# - edf/2002/training/1611462137/Empatica-HR.edf,
# - edf/2002/training/1611462137/Empatica-BVP.edf,
# - edf/2002/training/1611658350/Empatica-HR.edf,
# - edf/2002/training/1611658350/Empatica-BVP.edf

_log_level = mne.set_log_level(False)

all_stats = []
dropout_labels, coverage_labels = [], []
print("Calulating file statistics from data...")
for i, filepath in enumerate(filepaths, 1):
    print(f"  {i}/{len(filepaths)}: {filepath}")

    file = mne.io.read_raw_edf(str(filepath))
    data, times = file.get_data(), file.times

    time_fp = datetime.fromtimestamp(int(filepath.parent.stem))
    stats = {
        'filepath': filepath,
        'time_fp': time_fp,  #.replace(tzinfo=utc),  # Only some of these times are actually UTC?
        **tools.get_metadata_stats(file, apply_tz=True),
        **tools.get_data_stats(data),
    }
    stats['time_diff_fp_edfs'] = stats['time_fp'] - stats['time_edf'].replace(tzinfo=None)
    stats['range'] = stats['max'] - stats['min']

    all_stats.append(stats)

    coverage = tools.get_coverage(stats,
                            start_time=stats['time_edf'].replace(tzinfo=None))
    coverage_labels.append((filepath, *coverage))

    # TODO put a minimum duration on dropouts
    dropouts = tools.get_dropouts(
        data[0, :],
        times,
        start_time=stats['time_edf'].replace(tzinfo=None),
        # min_dropout=int(0.5 * stats['srate']),
        min_dropout=128*10,  # filter off dropouts that are less than 10 seconds
    )
    if len(dropouts) > 0:
        dropouts = [(filepath, *dropout) for dropout in dropouts]
        dropout_labels.extend(dropouts)

# filestats = pd.DataFrame.from_dict(all_stats).set_index(
#     'filepath').sort_index()

print("Plotting results..")
fig, ax = plt.subplots()

day_in_hr = 24
ax.plot([-1, len(filepaths)], [1 * day_in_hr, 1 * day_in_hr], 'k--')
ax.plot([-1, len(filepaths)], [2 * day_in_hr, 2 * day_in_hr], 'k--')

print("  Plotting coverage..")
ax = tools.plot_labels(coverage_labels, ax, color='g', alpha=0.5, legend='COVERAGE')

print("  Plotting dropouts..")
ax = tools.plot_labels(dropout_labels, ax, color='r', alpha=1.0, legend='DROPOUT')

ax.set_title(
    f'Coverage of {DATA_TYPE.lower()} files for patient {PATIENT_ID} ({DATA_GROUP})'
)
ax.tick_params(axis='x', labelrotation=90)
ax.legend()

plt.tight_layout()
plt.savefig(f'{DATA_TYPE.lower()}_coverage_{PATIENT_ID}_{DATA_GROUP}.png')
# plt.show()
