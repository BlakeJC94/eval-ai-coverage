# Given a contiguous segment of data, is it possible to detect contiguous segments of constant
# values?


import numpy as np


# generate test data and put dropouts in this data
# foo = np.random.randint(0, 1000, size=100)
foo = np.random.rand(100)
# foo[22:37] = 0  # long dropout
# foo[85:91] = 0  # short dropout
# foo[60:62] = 0  # double value dropout (should be detected)
# foo[55:56] = 0  # single value dropout (should not be detected)
# foo[:1] = 0  # dropout at start
# foo[-1:] = 0  # dropout at end
# foo[:] = 0  # all dropouts

# expected:
#   starts = [22, 60, 85]
#   ends =   [37, 62, 91]

differences = np.diff(foo, prepend=np.nan)
changes = np.where(np.diff((differences == 0)) != 0)[0]
starts, ends = changes[::2], changes[1::2] + 1
ends = np.append(ends, len(foo)) if len(ends) < len(starts) else ends

assert len(starts) >= len(ends)

# dropouts = [(a, b) for a, b in zip(starts, ends)]
dropouts = list(zip(starts, ends))
for i in dropouts: print(i)
