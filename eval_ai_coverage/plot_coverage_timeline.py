from pathlib import Path
from typing import List, Tuple, Optional

import pandas as pd
import plotly.graph_objects as go


# TODO re-write this guff
def plot_coverage_timeline(
    coverage: pd.DataFrame,
    dropouts: pd.DataFrame,
) -> go.Figure:
    """Create a time series figure from an iterable of DataFrames."""

    traces = []
    annotations = []
    row_idx = 0
    for hub_df in hub_dfs:
        row_idx += 2
        annotations.append(
            dict(text=hub_df['Common Name'].iloc[0], xref='paper', x=-0.01, xanchor='right',
                 yref='y', y=row_idx + 1.2, showarrow=False))
        for _, row in hub_df.iterrows():
            start = row['Connected Since']
            end = row['Last Seen']
            if start.day != end.day:
                text = f"{start.strftime(dt_format)} - {end.strftime(dt_format)}"
            else:
                text = f"{start.strftime('%-I:%M:%S%p')} - {end.strftime(dt_format)}"

            traces.append(
                go.Scatter(x=[start, start, end, end,
                              start], y=[row_idx, row_idx + 1.8, row_idx + 1.8, row_idx, row_idx],
                           name=row['Common Name'], mode='lines', marker={'color': row['colour']},
                           fill='toself', hoveron='fills', text=text), )

    fig = go.Figure(
        data=traces, layout={
            'height': num_hubs * 20,
            'width': 1000,
            'showlegend': False,
            'xaxis_showgrid': False,
            'annotations': annotations,
            'margin': {
                'l': 100,
                't': 25
            },
            'yaxis': {
                'showticklabels': False,
                'range': (1, (num_hubs + 1) * 2)
            },
            'xaxis': {
                'range': (start_date, latest_date)
            }
        })
