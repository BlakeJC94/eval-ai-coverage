from pathlib import Path
import pickle

from ea_coverage import PATIENT_IDS, DTYPES, load_results, OUTPUT_PATH
from ea_coverage.vis import add_timeline


def plot_timeline(patient_id: str):
    assert patient_id in PATIENT_IDS, f'{patient_id} not in {PATIENT_IDS}'

    patient_coverage = {}
    for data_type in DTYPES:
        results = load_results(patient_id, data_type)
        patient_coverage[data_type] = (results['coverage'], results['dropouts'])

    with open('sztimes.pkl', 'rb') as f:
        sztimes = pickle.load(f)
        sztimes = sztimes[patient_id]

    print("Plotting coverage timeline...")
    patient_coverage_fig = add_timeline(
        patient_id,
        patient_coverage,
        sztimes,
    )

    print("Saving coverage timeline...")
    output_filename = f'{patient_id}_coverage_timeline.png'
    fp = Path(OUTPUT_PATH) / Path(output_filename)
    fp.parent.mkdir(parents=True, exist_ok=True)

    patient_coverage_fig.write_image(str(fp))
