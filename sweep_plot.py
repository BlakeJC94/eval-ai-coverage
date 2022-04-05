from itertools import product

from plot import plot_outputs

DATA_DIR = './edf'
START_TIME_KEY = 'time_edf'

# PATIENT_IDS = ['1110']#, '1869'] #, '1876', '1904', '1965', '2002']
# PATIENT_IDS = ['1869', '1876', '1904', '1965', '2002']
PATIENT_IDS = ['1110', '1869', '1876', '1904', '1965', '2002']
DATA_TYPES = ['ACC', 'BVP', 'EDA', 'HR', 'TEMP']

if __name__ == '__main__':

    for pid, dtype in product(PATIENT_IDS, DATA_TYPES):
        print(f'-------- Processing patient {pid} ({dtype})')
        plot_outputs(
            patient_id=pid,
            data_type=dtype,
        )

