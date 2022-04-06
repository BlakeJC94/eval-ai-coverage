"""Plots timeline of coverage for a given patient."""

from pathlib import Path
import pickle

import plotly.graph_objects as go

from eval_ai_coverage import (
    OPTS,
    TIMELINE_DIR,
    load_results,
    create_coverage_timeline,
)


def main(patient_id: str) -> go.Figure:

    patient_coverage = {}
    for data_type in OPTS['data_type']:
        results = load_results(patient_id, data_type)
        patient_coverage[data_type] = (results['coverage'], results['dropouts'])

    with open('sztimes.pkl', 'rb') as f:
        sztimes = pickle.load(f)
        sztimes = sztimes[patient_id]

    print("Plotting coverage timeline...")
    patient_coverage_fig = create_coverage_timeline(
        patient_id,
        patient_coverage,
        sztimes,
    )

    print("Saving coverage timeline...")
    output_filename = f'{patient_id}_coverage_timeline.png'
    fp = Path(TIMELINE_DIR) / Path(output_filename)
    if not fp.parent.exists():
        fp.parent.mkdir(parents=True)

    patient_coverage_fig.write_image(str(fp))
    return patient_coverage_fig

if __name__ == "__main__":

    # TEST
    PATIENT_IDS = ['1110']

    # ALL DATA
    # PATIENT_IDS = ['1110', '1869', '1876', '1904', '1965', '2002']

    for pid in PATIENT_IDS:
        print(f'-------- Processing patient {pid}')
        fig = main(pid)

        if len(PATIENT_IDS) == 1:
            fig.show()


