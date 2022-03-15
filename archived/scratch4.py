# TODO create a dataframe compute statistics for each training/testing directory
# (per patient, per signal)
# index: filepath
# * start time
# * duration
# * sample rate
# * number of samples
# * number of channels
# * standard deviation of data
# * mean of data
# * range of data
# * difference between folder timestamp and edf timestamp

# General structure of patient dir:
#
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

import warnings
from copy import copy
from pathlib import Path
from datetime import datetime, timedelta

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mne


DATA_DIR = './edf'
assert DATA_DIR in ['./edf', './edf_sample']

PATIENT_ID = '2002'
assert PATIENT_ID in ['1110', '1869', '1876', '1904', '1965', '2002']

DATA_GROUP = 'training'
assert DATA_GROUP in ['training', 'testing', 'all']

DATA_TYPE = 'ACC'
assert DATA_TYPE in ['ACC', 'BVP', 'EDA', 'HR', 'TEMP', 'ALL']


# get data
data_path = Path(DATA_DIR).expanduser() / PATIENT_ID / DATA_GROUP
filepaths = [i for i in data_path.glob('**/*') if i.suffix == '.edf']
print(f"{len(filepaths)} files found in {data_path}")
all_filepaths = copy(filepaths)

if DATA_TYPE != 'ALL':
    print(f"Filtering for data type: {DATA_TYPE}")
    assert all([filepath.stem[:9] == 'Empatica-' for filepath in filepaths]), \
        'Invalid filepaths present'
    filepaths = [
        filepath for filepath in filepaths if filepath.stem[9:] == DATA_TYPE
    ]
    print(f"{len(filepaths)} {DATA_TYPE} files found in {data_path}")

# filter dodgy files
dodgy_filepaths = {}
old_log_level = mne.set_log_level(False)

print("Filtering dodgy files...")
with warnings.catch_warnings():
    warnings.simplefilter('error')
    for i, filepath in enumerate(filepaths):
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

    print(f"{len(dodgy_filepaths)} dodgy files removed")

# mne.set_log_level(old_log_level)  # I don't think this is needed

# EXPECTED DODGY FILES for 2002 training
# - edf/2002/training/1611462137/Empatica-HR.edf,
# - edf/2002/training/1611462137/Empatica-BVP.edf,
# - edf/2002/training/1611658350/Empatica-HR.edf,
# - edf/2002/training/1611658350/Empatica-BVP.edf

# TODO MAKE SURE THIS WORKS WITH MNE, expecting 4 bad files with 2002 training (using pyedflib)

# INIT dict for dataframe
fields = [
    'time_fp',
    'time_edf',
    'duration',
    'srate',
    'nchan',
    'nsample',
    'nan_prop',
    'std',
    'mean',
    'min',
    'max',
]

filestats_dict = {k: [] for k in fields}
filestats_dict['filepath'] = filepaths
dropouts = {filepath: [] for filepath in filepaths}
print("Calulating file statistics...")
for i, filepath in enumerate(filepaths):
    print(f"{i + 1}/{len(filepaths)}: {filepath}")
    file = mne.io.read_raw_edf(str(filepath))
    stats = {k: None for k in filestats_dict.keys() if k != 'filepath'}

    stats['time_fp'] = datetime.fromtimestamp(int(filepath.parent.stem))
    stats['time_edf'] = file.info.get('meas_date').replace(tzinfo=None)  # Thinks it's UTC?
    stats['duration'] = (file.times[-1] - file.times[0])
    stats['srate'] = file.info.get('sfreq')
    stats['nchan'] = file.info.get('nchan')
    stats['nsample'] = file.n_times

    data = file.get_data()  # chs, times
    stats['nan_prop'] = np.sum(np.isnan(data[0,:])) / file.n_times
    stats['std'] = np.std(data.flat)
    stats['mean'] = np.mean(data.flat)
    stats['min'] = np.min(data.flat)
    stats['max'] = np.max(data.flat)

    # search for flat sections


    dropout_start = data[0, 0]
    for i in range(1, file.n_times):
        if np.abs(data[0, i] - dropout_start) > 0.1:
            dropout_end = data[0, i - 1]
            dropouts[filepath].append((dropout_start, dropout_end))
            dropout_start = dropout_end
        else:

    dropout_times = [(start, end) for start, end in zip(file.data[0,:-1], file.times[0, 1:]) if end - start < 0.1]
    dropouts[filepath].extend(dropout_times)

    for k, v in stats.items():
        assert v is not None, f"{k} has not been set"
        filestats_dict[k].append(v)

# convert to DataFrame and calculate more stats
filestats = pd.DataFrame().from_dict(filestats_dict)
filestats = filestats.sort_values(by='filepath').set_index('filepath')
filestats['time_diff_fp_edfs'] = filestats['time_fp'] - filestats['time_edf']
filestats['range'] = filestats['max'] - filestats['min']

# TODO run some additional filters, durations? range? std? etc

# IDEA: plot horizontal bar chart of coverage of each channel across each day
# * Are the times on the directories more reliable than the times on the edfs?
#   * For which files are these the same?

# just try the times on the edf files for now

# UPDATE: chatted to Ewan, he's aware of the issue. Let's just include local times in EDFs in the
# instructions for the competition.

START_TIME = 'time_edf'  # Local time on the EDF file, UTC-5/UTC-6. Timezone info not on EDF!
filestats['coverage_index'] = filestats[START_TIME].dt.normalize()  # This strips the time info
assert (filestats['coverage_index'] <= filestats[START_TIME]).all(), \
    "coverage_index is not less than or equal to time_edf"

filestats['coverage_start'] = (filestats[START_TIME] - filestats['coverage_index'])
filestats['coverage_start'] = filestats['coverage_start'].dt.total_seconds()


labels = [str(i.parent.stem) for i in filestats.index.values]
bar1 = filestats['coverage_start']
bar2 = filestats['duration']
width = 0.35  # the width of the bars: can also be len(x) sequence

fig, ax = plt.subplots()
day_in_hr = 24
sec_in_hr = 3600
ax.bar(labels, bar2/sec_in_hr, width, bottom=bar1/sec_in_hr, label='COVERAGE')
ax.plot([-1, len(labels)], [1 * day_in_hr, 1 * day_in_hr], 'k--')
ax.plot([-1, len(labels)], [2 * day_in_hr, 2 * day_in_hr], 'k--')
ax.plot([-1, len(labels)], [3 * day_in_hr, 3 * day_in_hr], 'k--')
ax.set_ylim(0, (max(bar1) + max(bar2))/(sec_in_hr) * 1.1)
ax.set_ylabel('Hours')
ax.set_title(f'Coverage of {DATA_TYPE.lower()} files in {data_path}')
ax.tick_params(axis='x', labelrotation=90)
ax.legend()
plt.tight_layout()
plt.show()


# bar1 = coverage_start[:len(labels)]
# bar2 = coverage_end[:len(labels)]
# width = 0.35  # the width of the bars: can also be len(x) sequence
# fig, ax = plt.subplots()
# ax.plot([min(labels), max(labels)], [24 * 60 * 60, 24 * 60 * 60], 'k--')
# # ax.bar(labels, bar1, width, alpha=0.0)
# ax.bar(labels, bar2, width, bottom=bar1, label='COVERAGE')
# ax.set_ylim(0, (max(bar1) + max(bar2)) * 1.1)
# ax.set_ylabel('Seconds')
# ax.set_title('coverage testo')
# ax.tick_params(axis='x', labelrotation=90)
# ax.legend()
# plt.show()
