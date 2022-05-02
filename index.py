import pandas as pd
from getDataset import df as original_dataset
from getDataset import df_obs as patient_obs
import plotly.graph_objects as go
# print(original_dataset)

import os
import pathlib
import numpy as np
import datetime as dt
import dash
import dash_core_components as dcc
import dash_html_components as html

from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
from scipy.stats import rayleigh
import plotly.express as px

GRAPH_INTERVAL = os.environ.get("GRAPH_INTERVAL", 5000)

app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
app.title = "FHIR Dashboard"

server = app.server

app_color = {"graph_bg": "#082255", "graph_line": "#007ACE"}

app.layout = html.Div(
    [
        # header
        html.Div(
            [
                html.Div(
                    [
                        html.H4("PATIENT DASHBOARD", className="app__header__title"),
                        html.P(
                            "FHIR Demo",
                            className="app__header__title--grey",
                        ),
                    ],
                    className="app__header__desc",
                ),
                html.Div(
                    [

                        html.A(
                            html.Button("CASE ANYANLYSIS", className="link-button"),
                            # href="https://cloud.google.com/healthcare-api/docs/concepts/fhir",
                        ),
                        html.A(
                            html.Button("MORE DATA", className="link-button"),
                            href="https://github.com/plotly/dash-sample-apps/tree/main/apps/dash-wind-streaming",
                        ),
                        html.A(
                            html.Img(
                                src=app.get_asset_url("FHIR-new-logo.png"),
                                className="app__menu__img",
                            ),
                            href="https://cloud.google.com/healthcare-api/docs/concepts/fhir",
                        ),
                    ],
                    className="app__header__logo",
                ),
            ],
            className="app__header",
        ),
        html.Div(
            [
                # wind speed
                html.Div(
                    [
                        html.Div(
                            [html.H6("Cases Distribution", className="graph__title")]
                        ),
                        dcc.Graph(
                            id="DistributionCaseMap",
                            figure=dict(
                                layout=dict(
                                    plot_bgcolor=app_color["graph_bg"],
                                    paper_bgcolor=app_color["graph_bg"],
                                )
                            ),
                        ),
                        html.Div(
                            [html.H6("Distribution of Age", className="graph__title")]
                        ),
                        dcc.Graph(
                            id="DistributionAge",
                            figure=dict(
                                layout=dict(
                                    plot_bgcolor=app_color["graph_bg"],
                                    paper_bgcolor=app_color["graph_bg"],
                                )
                            ),
                        ),
                    ],
                    className="two-thirds column wind__speed__container",
                ),
                html.Div(
                    [
                        # histogram
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.H6(
                                            "GENDER FILLTER",
                                            className="graph__title",
                                        )
                                    ]
                                ),
                                dcc.Dropdown(
                                    id='gender-dropdown',
                                    options=[{'label': x, 'value': x} for x in ['female', 'male', 'Both']],
                                    value='Both'
                                ),
                                html.Div(
                                    [
                                        html.H6(
                                            "BIN SIZE OF HISTOGRAM",
                                            className="graph__title",
                                        )
                                    ]
                                ),
                                html.Div(
                                    [
                                        dcc.Slider(
                                            id="bin-slider",
                                            min=1,
                                            max=60,
                                            step=1,
                                            value=20,
                                            updatemode="drag",
                                            marks={
                                                20: {"label": "20"},
                                                40: {"label": "40"},
                                                60: {"label": "60"},
                                            },
                                        )
                                    ],
                                    className="slider",
                                ),
                                html.Div(
                                    [
                                        html.P(
                                            "# of Bins: Auto",
                                            id="bin-size",
                                            className="auto__p",
                                        ),
                                    ],
                                    className="auto__container",
                                ),
                                # dcc.Graph(
                                #     id="wind-histogram",
                                #     figure=dict(
                                #         layout=dict(
                                #             plot_bgcolor=app_color["graph_bg"],
                                #             paper_bgcolor=app_color["graph_bg"],
                                #         )
                                #     ),
                                # ),
                            ],
                            className="graph__container first",
                        ),
                        html.Div(
                            [
                                dcc.Graph(
                                    id="Age-Pie-Chart",
                                    figure=dict(
                                        layout=dict(
                                            plot_bgcolor=app_color["graph_bg"],
                                            paper_bgcolor=app_color["graph_bg"],
                                        )
                                    ),
                                ),
                            ],
                            className="graph__container second",
                        ),
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.H6(
                                            "Single Case Analysis", className="graph__title"
                                        )
                                    ]
                                ),
                                html.Div(
                                    [
                                        html.H6(
                                            "CONDITION FILLTER",
                                            className="graph__title",
                                        )
                                    ]
                                ),
                                dcc.Dropdown(
                                    id='condition-dropdown',
                                    options=[{'label': x, 'value': x} for x in ['Body Height','Body Weight', 'Body Mass Index']],
                                    value='Body Weight'
                                ),
                                dcc.Graph(
                                    id="Condition-Pie-Chart",
                                    figure=dict(
                                        layout=dict(
                                            plot_bgcolor=app_color["graph_bg"],
                                            paper_bgcolor=app_color["graph_bg"],
                                        )
                                    ),
                                ),
                            ],
                            className="graph__container second",
                        ),
                    ],
                    className="one-third column histogram__direction",
                ),
            ],
            className="app__content",
        ),
    ],
    className="app__container",
)


@app.callback(
    Output("DistributionAge", "figure"), [Input("bin-slider", "value"), Input('gender-dropdown', 'value')],
)
def gen_wind_speed(slider_value, gender):
    df = original_dataset
    if not gender == 'Both':
        df = df.loc[df['Gender'] == gender]
    fig = px.histogram(df, x="Age", histnorm='probability density', nbins=slider_value)

    layout = dict(
        height=350,
        plot_bgcolor=app_color["graph_bg"],
        paper_bgcolor=app_color["graph_bg"],
        font={"color": "#fff"},
        autosize=False,
        polar={
            "bgcolor": app_color["graph_line"],
            "radialaxis": {"range": [0, 45], "angle": 45, "dtick": 10},
            "angularaxis": {"showline": False, "tickcolor": "white"},
        },
        showlegend=False,
    )
    fig.update_layout(layout)
    return fig



@app.callback(
    Output("DistributionCaseMap", "figure"), [Input('gender-dropdown', 'value')],
)
def gen_wind_speed(gender):
    df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/2014_us_cities.csv')
    df.head()

    df['text'] = df['name'] + '<br>Population ' + (df['pop'] / 1e6).astype(str) + ' million'
    limits = [(0, 2), (3, 10), (11, 20), (21, 50), (50, 3000)]
    colors = ["royalblue", "crimson", "lightseagreen", "orange", "lightgrey"]
    cities = []
    scale = 5000

    fig = go.Figure()

    for i in range(len(limits)):
        lim = limits[i]
        df_sub = df[lim[0]:lim[1]]
        fig.add_trace(go.Scattergeo(
            locationmode='USA-states',
            lon=df_sub['lon'],
            lat=df_sub['lat'],
            text=df_sub['text'],
            marker=dict(
                size=df_sub['pop'] / scale,
                color=colors[i],
                line_color='rgb(40,40,40)',
                line_width=0.5,
                sizemode='area'
            ),
            name='{0} - {1}'.format(lim[0], lim[1])))

    layout = dict(
        # height=350,
        # width=1000,
        # plot_bgcolor=app_color["graph_bg"],
        # paper_bgcolor=app_color["graph_bg"],
        # font={"color": "#fff"},
        # # autosize=False,
        # polar={
        #     "bgcolor": app_color["graph_line"],
        #     "radialaxis": {"range": [0, 45], "angle": 45, "dtick": 10},
        #     "angularaxis": {"showline": False, "tickcolor": "white"},
        # },
        # showlegend=False,
        geo=dict(
            scope='usa',
            landcolor='rgb(217, 217, 217)',
            # width=1000,
        )
    )
    fig.update_layout(layout)
    return fig

@app.callback(
    Output("Age-Pie-Chart", "figure"), [Input('gender-dropdown', 'value')],
)
def gen_Age_pie_chart(gender):
    df = original_dataset
    if not gender == 'Both':
        df = df.loc[df['Gender'] == gender]
    fig = px.pie(df, values='Age', names='Name', title='Pie Chart of Age')

    layout = dict(
        height=350,
        plot_bgcolor=app_color["graph_bg"],
        paper_bgcolor=app_color["graph_bg"],
        font={"color": "#fff"},
        autosize=False,
        polar={
            "bgcolor": app_color["graph_line"],
            "radialaxis": {"range": [0, 45], "angle": 45, "dtick": 10},
            "angularaxis": {"showline": False, "tickcolor": "white"},
        },
        showlegend=False,
    )
    fig.update_layout(layout)
    return fig



@app.callback(
    Output("Condition-Pie-Chart", "figure"), [Input('condition-dropdown', 'value')],
)
def gen_Condition_pie_chart(condition):
    df = patient_obs
    if condition is not None:
        df = df.loc[df['Condition_Name'] == condition]
        fig = px.pie(df, values='Value', names='Value', title='Pie Chart of ' + condition)

        layout = dict(
            height=350,
            plot_bgcolor=app_color["graph_bg"],
            paper_bgcolor=app_color["graph_bg"],
            font={"color": "#fff"},
            autosize=False,
            polar={
                "bgcolor": app_color["graph_line"],
                "radialaxis": {"range": [0, 45], "angle": 45, "dtick": 10},
                "angularaxis": {"showline": False, "tickcolor": "white"},
            },
            showlegend=False,
        )
        fig.update_layout(layout)
        return fig


@app.callback(
    Output("bin-size", "children"),
    [Input("bin-slider", "value")],
)
def show_num_bins(slider_value):
    """ Display the number of bins. """
    return "# of Bins: " + str(int(slider_value))



if __name__ == "__main__":
    app.run_server(debug=True)