import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import base64
import io

# Create a Dash app
app = dash.Dash(__name__)

# Define app layout
app.layout = html.Div([
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=True
    ),
    dcc.Dropdown(
        id='format-dropdown',
        options=[
            {'label': 'Auto', 'value': 'auto'},
            {'label': 'Excel', 'value': 'excel'},
            {'label': 'CSV', 'value': 'csv'}
        ],
        value='auto',
        style={'width': '50%', 'margin': '10px'}
    ),
    html.Div(id='output-data-upload'),
    html.Div(id='scatterplots')
])


def clean_data(contents, filename, file_format):
    decoded = base64.b64decode(contents[0])
    print(decoded[:100])
    try:
        if file_format == 'auto':
            if 'csv' in filename:
                df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            elif 'xls' in filename or 'xlsx' in filename:
                df = pd.read_excel(io.BytesIO(decoded))
            else:
                # Assume CSV by default if format cannot be determined
                df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        elif file_format == 'excel':
            df = pd.read_excel(io.BytesIO(decoded))
        elif file_format == 'csv':
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    # Clean up the data (replace NaNs, remove duplicates, etc.)
    # Your cleaning process here
    cleaned_df = df.dropna()  # Example: Drop NaN values

    return cleaned_df


@app.callback(Output('output-data-upload', 'children'),
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('format-dropdown', 'value')])
def update_output(contents, filename, file_format):
    if contents is not None:
        cleaned_df = clean_data(contents, filename, file_format)
        return html.Div([
            html.H5(filename),
            html.H6('Cleaned Data Preview:'),
            html.Div(cleaned_df.head())
        ])


@app.callback(Output('scatterplots', 'children'),
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('format-dropdown', 'value')])
def update_scatterplots(contents, filename, file_format):
    if contents is not None:
        cleaned_df = clean_data(contents, filename, file_format)

        # Create scatter plots
        fig_bmi = px.scatter(cleaned_df, x='Age', y='BMI', title='BMI Scatter Plot')
        fig_weight = px.scatter(cleaned_df, x='Age', y='Weight', title='Weight Scatter Plot')
        fig_length = px.scatter(cleaned_df, x='Age', y='Length', title='Length Scatter Plot')
        fig_hc = px.scatter(cleaned_df, x='Age', y='Head Circumference', title='Head Circumference Scatter Plot')

        return html.Div([
            dcc.Graph(figure=fig_bmi),
            dcc.Graph(figure=fig_weight),
            dcc.Graph(figure=fig_length),
            dcc.Graph(figure=fig_hc)
        ])


if __name__ == '__main__':
    app.run_server(debug=True)
