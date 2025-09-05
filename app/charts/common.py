import plotly.express as px
import pandas as pd
import numpy as np

def style_fig(fig, height=420):
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=50, b=10),
        xaxis_title=None, yaxis_title=None,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0)
    )
    return fig

def nz(df: pd.DataFrame, required_cols):
    """Remove linhas com NaN/±inf nas colunas exigidas."""
    clean = df.replace([np.inf, -np.inf], pd.NA)
    return clean.dropna(subset=required_cols)
