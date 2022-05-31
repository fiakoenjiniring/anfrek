from pathlib import Path
import dash
from dash import Output, Input, State, dcc
from pyconfig import appConfig
from pytemplate import fktemplate
import dash_bootstrap_components as dbc
import plotly.io as pio
import pylayout, pyfunc, pylayoutfunc, pyfigure  # noqa
import pandas as pd

pio.templates.default = fktemplate

# DASH APP CONFIG
APP_TITLE = appConfig.DASH_APP.APP_TITLE
UPDATE_TITLE = appConfig.DASH_APP.UPDATE_TITLE
DEBUG = appConfig.DASH_APP.DEBUG

# BOOTSTRAP THEME
THEME = appConfig.TEMPLATE.THEME
DBC_CSS = (
    "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.4/dbc.min.css"
)

# MAIN APP
app = dash.Dash(
    name=APP_TITLE,
    external_stylesheets=[getattr(dbc.themes, THEME), DBC_CSS],
    title=APP_TITLE,
    update_title=UPDATE_TITLE,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"},
    ],
    suppress_callback_exceptions=True,
    prevent_initial_callbacks=True,
)

server = app.server

# LAYOUT APP
app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        pylayout.HTML_ROW_TITLE,
                        pylayout.HTML_ROW_BUTTON_UPLOAD,
                        pylayout.HTML_ROW_BUTTON_EXAMPLE,
                    ],
                    md=3,
                    align="start",
                    class_name="text-center pt-3",
                ),
                dbc.Col(
                    [
                        pylayout.HTML_CARDS,
                    ],
                    class_name="pt-3",
                ),
            ],
        ),
        pylayout._HTML_TROUBLESHOOTER,
        pylayout.HTML_FOOTER,
    ],
    fluid=True,
    class_name="dbc my-3 px-3",
)

# CALLBACK FUNCTION


@app.callback(
    Output("row-table-data", "children"),
    # Output("row-troubleshooter", "children"),
    Output("card-stat", "disabled"),
    Output("card-frequency", "disabled"),
    Output("card-goodness", "disabled"),
    Input("dcc-upload", "contents"),
    State("dcc-upload", "filename"),
    State("dcc-upload", "last_modified"),
    Input("button-example", "n_clicks"),
)
def callback_upload(content, filename, filedate, _):
    ctx = dash.ctx

    if content is not None:
        report, dataframe = pyfunc.parse_upload_data(content, filename)

    if ctx.triggered_id == "button-example":
        dataframe = pd.read_csv(
            Path(r"./example_data.csv"), index_col=0, parse_dates=True
        )

    tab_stat_disabled = True
    tab_frequency_disabled = True
    tab_goodness_disabled = True

    if dataframe is None:
        children = report
    else:
        EDITABLE = [False, True]
        children = pylayoutfunc.create_table_layout(
            dataframe,
            "output-table",
            filename=filename,
            editable=EDITABLE,
            deletable=False,
        )
        tab_stat_disabled = False
        tab_frequency_disabled = False
        tab_goodness_disabled = False

    return (
        children,
        tab_stat_disabled,
        tab_frequency_disabled,
        tab_goodness_disabled,
    )


@app.callback(
    Output("row-table-viz", "children"),
    Input("output-table", "derived_virtual_data"),
    State("output-table", "columns"),
)
def callback_table_visualize(table_data, table_columns):

    dataframe = pyfunc.transform_to_dataframe(table_data, table_columns)

    fig = pyfigure.figure_tabledata(dataframe)

    return dcc.Graph(figure=fig)


@app.callback(
    Output("row-stat-statistics", "children"),
    Output("row-stat-distribution", "children"),
    Input("button-stat-calc", "n_clicks"),
    State("output-table", "derived_virtual_data"),
    State("output-table", "columns"),
)
def callback_calc_statout(_, table_data, table_columns):

    dataframe = pyfunc.transform_to_dataframe(table_data, table_columns)

    fig_statout = pyfigure.figure_statout(dataframe)

    fig_dist = pyfigure.figure_distribution(dataframe)

    return dcc.Graph(figure=fig_statout), dcc.Graph(figure=fig_dist)


if __name__ == "__main__":
    app.run(debug=DEBUG)
