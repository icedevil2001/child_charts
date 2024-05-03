
import pandas as pd
from pathlib import Path
from typing import List

import seaborn as sns
from plotly.offline import iplot
from plotly import graph_objs as go
from plotly.subplots import make_subplots

from src.database import Child, get_growth_table


PERCENTILES = ['P1', "P5", 'P10', "P25", 'P50', "P75", 'P90', "P95", 'P99']
COLOURS = sns.color_palette("icefire",len(PERCENTILES)).as_hex()
PERCENTILES_TO_COLOR = dict(zip(PERCENTILES, COLOURS))

def growth_percentiles(df) -> List[go.Scatter]:
    """Plots the growth percentiles lines for the given dataframe.
    The dataframe should have columns 'Month', 'P1', 'P5', 'P10', 'P25', 'P50', 'P75', 'P90', 'P95', 'P99'"""
    def _plot_growth_percentiles(df, col):
        return go.Scatter(
            x=df['Month'],
            y=df[col],
            mode='lines',
            name=f'{col}th',
            # labels = {col: f'{col}th percentile'},
            line=dict(
                shape = 'linear',
                color = PERCENTILES_TO_COLOR.get(col, 'rgb(205, 12, 24)'),
                width= 1,
                dash = 'solid'
                
            )
        )
    plots = []
    for col in PERCENTILES:
        plots.append(_plot_growth_percentiles(df, col))
    return plots

def plot_growth_percentiles_with_subject(
        who_reference_df: pd.DataFrame, 
        subject_df: pd.DataFrame, 
        subject_ycol: str, 
        # percentiles: str,
        # title: str
        ) -> go.Figure:
    """Plots the growth percentiles with the subject's data"""
    plots = growth_percentiles(who_reference_df)
    trace = go.Scatter(
        x=subject_df['months'],
        y=subject_df[subject_ycol],
        mode='markers',
        name='Subject',
        # labels = {subject_ycol: ' '.join(subject_ycol.split('_')).capitalize()},
        # text=subject_df[percentiles].round(0).astype(str) + '%',
        marker=dict(
            size=5,
            color='red',
        )
    )
    plots.append(trace)
    # title = f"{title}"
    # layout = go.Layout(
    #     title=title,
    #     xaxis=dict(title='Age (months)'),
    #     yaxis=dict(title=subject_ycol),
    # )
    # fig = go.Figure(data=plots, layout=layout)
    return plots



def plot_subplot_growth_percentiles(df: pd.DataFrame, child: Child, growth_tables: dict, output: Path):
    """Plots the growth percentiles for Weight, BMI, Height and Head circumference. 
    The growth_tables is a dictionary of pandas DataFrames.
    The output is the path to save the plot as ineractive html file.
    """
    fig = make_subplots(rows=3, cols=2, 
                        subplot_titles=(
                            "Weight growth percentiles", 
                            "BMI growth percentiles", 
                            "Height growth percentiles", 
                            "Head circumference growth percentiles", 
                            "Table"),
                        shared_xaxes=False,
                        shared_yaxes=False,
                        vertical_spacing=0.1,
                        horizontal_spacing=0.1,
                        # x_title='Age (months)',
                        # y_title=['Weight (kg)', 'BMI', 'Height (cm)', 'Head circumference (cm)'],
                        specs=[
                            [{"type": "scatter"}, {"type": "scatter"}],
                            [{"type": "scatter"}, {"type": "scatter"}],
                            [{"type": "table", "colspan": 2}, None]
                        ]
                    )

    mapper= {
        'weight_kg': 'wfa',
        'bmi': 'bmi',
        'height_cm': 'lhfa',
        'hc_cm': 'hcfa'
    }

    for idx, ycol in enumerate([ 'weight_kg','bmi',  'height_cm', 'hc_cm']):
        # print(row, col, ycol)
        row = idx//2 + 1
        col = idx%2 + 1
        table = get_growth_table(growth_tables, mapper[ycol], child.gender, child.age).reset_index()
        # percentiles_col = f'{ycol.split("_")[0]}_percentile'

        dfx = df.loc[df[ycol].notna(), ['months', ycol]] ## remove NaN rows values

        traces =  plot_growth_percentiles_with_subject(
            who_reference_df=table, 
            subject_df=dfx, 
            subject_ycol=ycol, 
            # percentiles=f'{ycol.split("_")[0]}_percentile', 
            # title=f'{ycol.split("_")[0].capitalize()} growth percentiles'
            )
        # print(traces)
        fig.add_traces(
            traces,
            rows=[row]*len(traces), cols=[col]*len(traces),
        )
    df = df.fillna(0).round(2)
    df.style.format({
        "weight_percentile": "{:.2f}%",
        "bmi_percentile": "{:.2f}%",
        "height_percentile": "{:.2f}%",
        "hc_percentile": "{:.2f}%"
    })
    fig.add_trace(
        go.Table(
            header=dict(
                values=["Month", "Weight (%)", "BMI (%)", "Height (%)", "Head Circumference (%)"],
                font=dict(size=10),
                align="left"
            ),
            cells=dict(
                values=[df['months'], df['weight_percentile'] , df['bmi_percentile'], df['height_percentile'], df['hc_percentile']],
                align = "left"
            )
        ),
        row=3, col=1
    )

    fig.update_layout(
        title_text=f"Growth percentiles for {child.name}",
        height=800, width=1200, 
        showlegend=False,

        )
    
    fig.write_html(output)
    ## save figure to file
    fig.show()


