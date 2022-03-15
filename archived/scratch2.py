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


from copy import copy
from pathlib import Path
from datetime import datetime

import pandas as pd
import numpy as np
from pyedflib import EdfReader, highlevel


DATA_DIR = './edf'
PATIENT_ID = '2002'
DATA_GROUP = 'training'


# get data
data_path = Path(DATA_DIR).expanduser() / PATIENT_ID / DATA_GROUP
filepaths = [
    i for i in data_path.glob('**/*')
    if i.suffix == '.edf'
]
print(f"{len(filepaths)} files found in {data_path}")
all_filepaths = copy(filepaths)

# filter dodgy files
dodgy_filepaths = []
for filepath in all_filepaths:
    try:
        f = EdfReader(str(filepath))
        f.close()
    except OSError:
        dodgy_filepaths.append(filepath)
        filepaths.remove(filepath)

if dodgy_filepaths:
    print(f"{len(dodgy_filepaths)} files could not be read, removing from `filepaths` list")
    print(f"{len(filepaths)} non-dodgy files found in {data_path}")


# load the file metadata (headers and shit)
edf_headers, edf_signal_headers = {}, {}
for filepath in filepaths:
    with EdfReader(str(filepath)) as f:
        edf_headers[filepath] = f.getHeader()
        edf_signal_headers[filepath] = f.getSignalHeaders()


# init dataframe
filestats = pd.DataFrame(data=filepaths, columns=['filepath']).set_index('filepath')


# compute timestamp from directory name
filestats['time_filepath'] = filestats.index.map(
    lambda x: datetime.fromtimestamp(int(x.parent.stem)),
)
# compute timestamp from edf header
filestats['time_edf_header'] = filestats.index.map(
    lambda x: edf_headers[x]['startdate']
)
# What is the difference between the two timestamps?
filestats['time_diff_fp_edf'] = filestats['time_filepath'] - filestats['time_edf_header']


# This is pretty much all I can get from the edf header and the signal header..
# Maybe I'll record the sample rate of the first signal header
filestats['srate_edf_sig_header'] = filestats.index.map(
    lambda x: edf_signal_headers[x][0]['sample_rate']
)
# These all seem to be 1000.0? I though these were sampled at 128Hz?
filestats['nchs_signal_headers'] = filestats.index.map(
    lambda x: len(edf_signal_headers[x])
)





# Lets start opening all the data files and getting some more stats
# - number of samples in data
# - number of channels in data

# NOTE: wow this is slow, speed it up by just looking at what's needed?
edf_signal_stats = {}
for i, filepath in enumerate(filepaths):
    print(f"{i+1}/{len(filepaths)}: {filepath}")

    stats = {}
    with EdfReader(str(filepath)) as f:
        assert f.getNSamples().max() == f.getNSamples().min(), \
            f"{filepath} has different number of samples for different channels"

        n_samples = f.getNSamples().max()
        n_channels = f.signals_in_file

        # data = np.zeros((f.signals_in_file, f.getNSamples().max()))
        # for i in range(f.signals_in_file):
        #     data[i, :] = f.readSignal(i)


        stats['n_samples'] = n_samples

        # stats['duration'] = None  # TODO
        stats['proportion_of_dropouts'] = sum(np.isnan(data.flat)) / np.prod(data.shape)
        stats['std_dev'] = np.std(data.flat)
        stats['mean'] = np.mean(data.flat)
        stats['range'] = np.max(data.flat) - np.min(data.flat)

    edf_signal_stats[filepath] = stats

for k, v in edf_signal_stats[0].keys():
    filestats[f'edf_{k}'] = filestats.index.map(
        lambda x: edf_signal_stats[x][k]
    )


# NOTE: KILLED, this takes too much memory lol
# edf_signals = {}
# for i, filepath in enumerate(filepaths):
#     print(f"{i}/{len(filepaths)}: {filepath}")

#     with EdfReader(str(filepath)) as f:
#         assert f.getNSamples().max() == f.getNSamples().min(), \
#             f"{filepath} has different number of samples for different channels"

#         data = np.zeros((f.signals_in_file, f.getNSamples().max()))
#         for i in range(f.signals_in_file):
#             data[i, :] = f.readSignal(i)

#         edf_signals[filepath] = data









