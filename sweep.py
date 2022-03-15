from itertools import product

from main import main

DATA_DIR = './edf'
START_TIME_KEY = 'time_edf'

PATIENT_IDS = ['1110', '1869'] #, '1876', '1904', '1965', '2002']
DATA_TYPES = ['ACC', 'BVP'] #, 'EDA', 'HR', 'TEMP']

if __name__ == '__main__':

    for pid, dtype in product(PATIENT_IDS, DATA_TYPES):
        print(f'-------- Processing patient {pid} ({dtype})')
        results_training = main(
            data_dir=DATA_DIR,
            patient_id=pid,
            data_type=dtype,
            start_time_key=START_TIME_KEY,
            min_dropout=128 * 60,
            compute_dropouts=True,
        )

