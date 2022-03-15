
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
#     ...
#
# 146 directories, 720 files

from pathlib import Path
dir_2002 = Path('edf/2002/')

train_dirs = [i for i in dir_2002.glob('training/**') if i.stem != 'training']
test_dirs = [i for i in dir_2002.glob('testing/**') if i.stem != 'testing']

print(f'{len(train_dirs)} training directories')
print(f'{len(test_dirs)} testing directories')

# check that every directory has the same file structure
expected_edfs = {'Empatica-ACC', 'Empatica-BVP', 'Empatica-EDA', 'Empatica-HR', 'Empatica-TEMP'}
assert all([{j.stem for j in i.glob('*.edf')} == expected_edfs for i in train_dirs])
assert all([{j.stem for j in i.glob('*.edf')} == expected_edfs for i in test_dirs])

# let's just look at the edfs in the first directory
first_dir = train_dirs[1]
edf_files = list(first_dir.glob('**/*.edf'))

from pyedflib import highlevel
import matplotlib.pyplot as plt

# Load (signals, signal_headers, header) for each edf file in dict
edfs = {
    i.stem[9:].lower(): highlevel.read_edf(str(i)) for i in edf_files
}

# check the number and names of edf signals
assert set(edfs.keys()) == {'acc', 'bvp', 'eda', 'hr', 'temp'}, \
    f"Incorrect keys: {edfs.keys() = }"

expected_channels = {'acc': 4, 'bvp': 1, 'eda': 1, 'hr': 1, 'temp': 1}
for ch_name, (signals, signal_headers, header) in edfs.items():

    # check the number of channels in each edf
    assert len(signal_headers) == expected_channels[ch_name], \
        f"Incorrect number of channels for {ch_name}: {len(signal_headers) = }"

    # Is there a start time?
    assert header['startdate'], "No start date in edf header"

    # TODO check the sampling rate and data length

    for i, ch_header in enumerate(signal_headers):
        assert ch_header['sample_rate'] == 1000.0
        assert ch_header['sample_frequency'] == 1000.0



# plot signals
signals, signal_headers, header = edfs['acc']
fig, axs = plt.subplots(len(signal_headers), 1, figsize=(16, 10))
title = 'acc'
fig.suptitle(title, fontsize=16)
for i, (ch_header, ax) in enumerate(zip(signal_headers, axs.flat)):
    data = signals[i, :]
    ax.plot(data)
    ax.set_ylabel(f"{ch_header['label']}")
fig.tight_layout()
plt.show()

# what are the lenghts of all the signals in this directory?

# what are the shapes of the signals? -- They're all a bit different??
for k, v in edfs.items():
    print(f"{k} signals shape: {v[0].shape}")


# TODO build a function to plot numpy dashboard
# plot the standard deviations of the signals in each directory

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





