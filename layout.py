import dash_table
import dash_bootstrap_components as dbc
import dash_core_components as dcc

from get_data import *

colors = {
    'bg': '#010310',
    'text': '#F4E808'
}

graph_config = {'displayModeBar': True, 'displaylogo': False, 'modeBarButtonsToRemove':
                ['zoom2d', 'lasso2d', 'hoverCompareCartesian', 'hoverClosestCartesian', 'toggleSpikelines',
                 'toggleSpikelines', 'hoverClosestGeo']}

# df = pd.read_csv(r'https://covid.ourworldindata.org/data/owid-covid-data.csv')
df, country_name_list, numdate = latest_covid_data(r'https://covid.ourworldindata.org/data/owid-covid-data.csv')

df_cols = ['Country', 'Total Cases', 'New Cases', 'Total Deaths', 'New Deaths']

tab1_content = dbc.Card(
    dbc.CardBody(
        [dcc.Graph(id='total_cases_by_continent', figure={}, className="graph_tabs", config=graph_config),
         html.Button("Reset", id="drillback_cases", n_clicks=0, className="back_btn_drill_down")],
        style={"background-color": colors['bg'], "border-radius": "0"}), outline=colors['bg'], className="mt-3")

tab2_content = dbc.Card(
    dbc.CardBody(
        [dcc.Graph(id='total_deaths_by_continent', figure={}, className="graph_tabs", config=graph_config),
         html.Button("Reset", id="drillback_deaths", n_clicks=0, className="back_btn_drill_down")],
        style={"background-color": colors['bg'], "border-radius": "0"}), outline=colors['bg'], className="mt-3")

tab3_content = dbc.Card(
    dbc.CardBody(
        [dcc.Graph(id='total_vaccines_by_continent', figure={}, className="graph_tabs", config=graph_config),
         html.Button("Reset", id="drillback_vaccines", n_clicks=0, className="back_btn_drill_down")],
        style={"background-color": colors['bg'], "border-radius": "0"}), outline=colors['bg'], className="mt-3")


def make_layout():
    return html.Div(style={'backgroundColor': colors['bg']}, children=[

        html.Div(
            [
                dbc.Spinner(html.Div(id="loading-output"), fullscreen=True, color="primary",
                            fullscreenClassName="spinner_bg", spinnerClassName="spinner_dimension"),
            ]
        ),

        html.H1('Coronavirus Disease (COVID-19) Dashboard', className="title"),

        html.Div([
                  html.Div([
                        dcc.DatePickerSingle(id='date', min_date_allowed=min(df['date']),
                                             max_date_allowed=df['date'].max(),
                                             date=str(df['date'].max().to_pydatetime()-timedelta(days=1)).split(' ')[0],
                                             style={'display': 'inline-block', 'vertical-align': 'top'}),

                        html.Div([dcc.Dropdown(
                            id='country_name_dropdown',
                            options=country_name_list,
                            value='World',
                        )], style={'width': '10%', 'display': 'inline-block', 'margin-left': '3%'}),

                        html.Button("Today", id='today_btn', n_clicks=0, className="today_btn"),
                        html.Button("Total", id='total_btn', n_clicks=0, className="total_btn"),
                  ],
                        style={'width': '80%', "margin-left": "3%"}),

                  ]),

        html.Div([
            html.Div(id='total_cases', className="daily_stats_thumbnail"),
            html.Div(id='total_deaths', className="daily_stats_thumbnail"),
            html.Div(id='total_vaccines', className="daily_stats_thumbnail"),
        ], className="daily_stats_thumbnail_display"),

        # html.Div(dcc.Graph(id='testing')),
        html.H2(id="country_name", style={"margin-left": "5%", "color": "#F4E808"}),

        html.Div([
            dcc.Graph(id='graph', figure={}, className="geo_scatter",
                      config=graph_config),

            dbc.Card(
                [
                    dbc.Tabs(
                        [
                            dbc.Tab(tab1_content, label="CASES", tab_id="cases",
                                    label_style={"color": "orange"}, className="tab_style"),
                            dbc.Tab(tab2_content, label="DEATHS", tab_id="deaths",
                                    label_style={"color": "red"}, className="tab_style"),
                            dbc.Tab(tab3_content, label="VACCINATIONS", tab_id="vaccinations",
                                    label_style={"color": "green"}, className="tab_style"),
                        ],
                        id="card-tabs",
                        card=True,
                        active_tab="cases",
                        style={"background-color": "#010310"}
                    ),
                ], style={"width": "50%", "background-color": "#010310", "display": "inline-block"}
            )], style={"display": "flex", "margin-top": "1%"}),

        # html.Button("Reset", id="reset_btn", n_clicks=0),

        html.Div("Click the country name you are interested in to look at its graphs below!",
                 style={"color": "#F4E808", "font-size": "medium", "margin-left": "3%"}),

        html.Div([dash_table.DataTable(
            id="table_stats",
            columns=[{"name": col, "id": ['location', 'total_cases', 'new_cases', 'total_deaths', 'new_deaths',
                                          "total_vaccinations", "total_cases_per_million",
                                          "total_deaths_per_million"][idx]}
                     for (idx, col) in enumerate(['Country', 'Cases', '\u21E7 Cases', 'Deaths', '\u21E7 Deaths',
                                                  "Vaccines", "Cases/1M", "Deaths/1M"])],
            fixed_rows={'headers': True},
            style_table={'max-height': '300px', 'overflowY': 'auto'},

            style_data_conditional=[
                {
                    'if': {
                        'state': 'active'  # 'active' | 'selected'
                    },
                    'backgroundColor': '#6E6E6E',
                    'border': '1px solid #6E6E6E'
                },
                # data_bars(df, 'new_cases')
            ],
            style_header={
                'backgroundColor': '#F4E808',
                'color': '#010310',
                'fontWeight': 'bold',
                'fontSize': '15px',
             },
            style_cell={
                'backgroundColor': '#010310',
                'color': '#F4E808',
                'fontSize': '15px',
                'textAlign': 'left',
                'width': '8%',
            },
            # Remove vertical lines
            style_as_list_view=True,
            sort_action="native",)]),

        html.Div(id="top_stats", className="trending_stats"),

        html.Div([
            html.Div([
                dcc.Graph(id='total_cases_by_country', figure={}, style={"max-width": "50%"}, config=graph_config),
                dcc.Graph(id='daily_cases_by_country', figure={},  style={"max-width": "50%"}, config=graph_config)],
                style={'display': 'flex'}),

            html.Div([
                dcc.Graph(id='total_deaths_by_country', figure={},  style={"max-width": "50%"}, config=graph_config),
                dcc.Graph(id='daily_deaths_by_country', figure={},  style={"max-width": "50%"}, config=graph_config)
            ], style={'display': 'flex'})], style={'width': '74%', 'float': 'right'}),

        html.H2("Latest Covid-19 news around the world", className="news_main_header"),

        html.Div(id='news_location', style={"padding-bottom": "5%"}),

        ])


def data_bars(df, column):
    n_bins = 100
    bounds = [i * (1.0 / n_bins) for i in range(n_bins + 1)]
    ranges = [
        ((df[column].max() - df[column].min()) * i) + df[column].min()
        for i in bounds
    ]
    styles = []
    for i in range(1, len(bounds)):
        min_bound = ranges[i - 1]
        max_bound = ranges[i]
        max_bound_percentage = bounds[i] * 100
        styles.append({
            'if': {
                'filter_query': (
                    '{{{column}}} >= {min_bound}' +
                    (' && {{{column}}} < {max_bound}' if (i < len(bounds) - 1) else '')
                ).format(column=column, min_bound=min_bound, max_bound=max_bound),
                'column_id': column
            },
            'background': (
                """
                    linear-gradient(90deg,
                    #0074D9 0%,
                    #0074D9 {max_bound_percentage}%,
                    white {max_bound_percentage}%,
                    white 100%)
                """.format(max_bound_percentage=max_bound_percentage)
            ),
            'paddingBottom': 2,
            'paddingTop': 2
        })

    return styles
