from pathlib import Path
from typing import List, Tuple, Optional, Dict
from datetime import datetime, timedelta
import pytz

import pandas as pd
import plotly.graph_objects as go

from .globals import SPLIT


# TODO re-write this guff
def create_coverage_timeline(
    patient_id: str,
    patient_coverage: Dict[str, Tuple[pd.DataFrame, pd.DataFrame]],
    sztimes: pd.Series,
) -> go.Figure:
    """Create a time series figure from a dictionary of DataFrames."""
    num_dtypes = len(patient_coverage)
    start_date, end_date = None, None

    traces = []
    annotations = []
    row_idx = 0
    for dtype, (coverage, dropouts) in patient_coverage.items():
        row_idx += 2

        annotations.append(
            dict(
                text=dtype,
                xref='paper',
                x=-0.01,
                xanchor='right',
                yref='y',
                y=row_idx + 1.2,
                showarrow=False,
            )
        )
        traces, start_date, end_date = add_traces(
            coverage,
            'green',
            row_idx,
            traces,
            start_date,
            end_date,
        )
        traces, start_date, end_date = add_traces(
            dropouts,
            'red',
            row_idx,
            traces,
            start_date,
            end_date,
        )

    x_range_pad = timedelta(days=3)
    x_range = (start_date - x_range_pad, end_date + x_range_pad)
    y_range = [1, (num_dtypes + 1.5) * 2]

    # add lines for when seizures occur
    for sztime in sztimes:
        traces.append(
            go.Scatter(
                x=[sztime, sztime],
                y=y_range,
                mode='lines',
                line=dict(
                    color='black',
                    width=1,
                ),
            )
        )

    # add line for train/test split
    # Q: ARE THESE DIRNAMES UTC OR LOCAL??
    split_date = datetime.fromtimestamp(int(SPLIT[patient_id]))
    # IF LOCAL:
    split_date = split_date.replace(tzinfo=pytz.timezone('US/Central'))
    # IF UTC:
    # split_date = split_date.replace(tzinfo=pytz.utc)
    # split_date = split_date.astimezone(pytz.timezone('US/Central'))
    traces.append(
        go.Scatter(
            x=[split_date, split_date],
            y=y_range,
            mode='lines',
            line=dict(
                color='black',
                dash='dot',
                width=2,
            ),
        )
    )

    fig = go.Figure(
        data=traces,
        layout={
            'height': num_dtypes * 120,
            'width': 5000,
            'showlegend': False,
            'xaxis_showgrid': False,
            'annotations': annotations,
            'margin': {
                'l': 100,
                't': 25
            },
            'yaxis': {
                'showticklabels': False,
                'range': y_range,
            },
            'xaxis': {
                'range': x_range,
            }
        }
    )

    return fig

def add_traces(labels, color, row_idx, traces, start_date, end_date):
    """Add traces to the Figure."""
    dt_format = '%-I:%M:%S%p %d/%m'

    if len(labels) == 0:
        return traces, start_date, end_date

    for _, row in labels.iterrows():
        start = row['time_edf'] + timedelta(seconds=row['label_start'])
        end = row['time_edf'] + timedelta(seconds=row['label_start'] + row['label_duration'])

        if start_date is None or start < start_date:
            start_date = start

        if end_date is None or end > end_date:
            end_date = end

        if start.day != end.day:
            text = f"{start.strftime(dt_format)} - {end.strftime(dt_format)}"
        else:
            text = f"{start.strftime('%-I:%M:%S%p')} - {end.strftime(dt_format)}"

        traces.append(
            go.Scatter(
                x=[start, start, end, end, start],
                y=[row_idx, row_idx + 1.8, row_idx + 1.8, row_idx, row_idx],
                name=str(row['filepath'].parent.stem),
                mode='lines',
                marker={'color': color},
                fill='toself',
                hoveron='fills',
                text=text,
            )
        )

    return traces, start_date, end_date
