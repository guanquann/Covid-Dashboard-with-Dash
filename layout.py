import dash_table
import dash_bootstrap_components as dbc
import dash_core_components as dcc

from get_data import *

colors = {
    'bg': '#010310',
    'text': '#F4E808'
}

tab1_content = dbc.Card(
    dbc.CardBody(
        [dcc.Graph(id='total_cases_by_continent', figure={}, style={"width": "90%", "min-width": "300px"})],
        style={"background-color": colors['bg'], "border-radius": "0"}), outline=colors['bg'], className="mt-3")

tab2_content = dbc.Card(
    dbc.CardBody(
        [dcc.Graph(id='total_deaths_by_continent', figure={}, style={"width": "90%", "min-width": "300px"})],
        style={"background-color": colors['bg'], "border-radius": "0"}), outline=colors['bg'], className="mt-3")

tab3_content = dbc.Card(
    dbc.CardBody(
        [dcc.Graph(id='total_vaccines_by_continent', figure={}, style={"width": "90%", "min-width": "300px"})],
        style={"background-color": colors['bg'], "border-radius": "0"}), outline=colors['bg'], className="mt-3")

# df = pd.read_csv(r'https://covid.ourworldindata.org/data/owid-covid-data.csv')
df, country_name_list, numdate = latest_covid_data(r'https://covid.ourworldindata.org/data/owid-covid-data.csv')

df_cols = ['Country', 'Total Cases', 'New Cases', 'Total Deaths', 'New Deaths']


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
                        dcc.Dropdown(
                            id='type_of_stats',
                            options=[
                              {'label': "Today Statistics", 'value': 'today'},
                              {'label': 'Total Statistics', 'value': 'total'},
                            ],
                            value='today', style={'display': 'inline-block', 'vertical-align': 'top'})],
                        style={'width': '80%', "margin-left": "3%"}),
                  ]),

        html.Div([
            html.Div(id='total_cases', className="daily_stats_thumbnail"),
            html.Div(id='total_deaths', className="daily_stats_thumbnail"),
            html.Div(id='total_vaccines', className="daily_stats_thumbnail"),
        ], className="daily_stats_thumbnail_display"),

        # html.Div(dcc.Graph(id='testing')),

        html.Div([
            dcc.Graph(id='graph', figure={}, className="geo_scatter",
                      config={'displayModeBar': True, 'displaylogo': False, 'modeBarButtonsToRemove':
                              ['zoom2d', 'hoverCompareCartesian', 'hoverClosestCartesian', 'toggleSpikelines']}),

            dbc.Card(
                [
                    dbc.Tabs(
                        [
                            dbc.Tab(tab1_content, label="CASES", tab_id="cases", label_style={"color": "orange", "border-radius": "3px", "border": "0.5px solid", "font-weight": "bold"}),
                            dbc.Tab(tab2_content, label="DEATHS", tab_id="deaths",
                                    label_style={"color": "red", "border-radius": "3px", "border": "0.5px solid red", "font-weight": "bold"}),
                            dbc.Tab(tab3_content, label="VACCINATIONS", tab_id="vaccinations",
                                    label_style={"color": "green", "border-radius": "3px", "border": "0.5px solid green", "font-weight": "bold"}),
                        ],
                        id="card-tabs",
                        card=True,
                        active_tab="cases",
                        style={"background-color": "#010310"}
                    ),
                ], style={"width": "50%", "background-color": "#010310"}
            )], style={"display": "flex"}),

        # dcc.Graph(id='daily_by_continent', figure={}, style={"margin": "3%", "border-radius": "5px"}),

        html.Div([dash_table.DataTable(
            id="table_stats",
            columns=[{"name": col, "id": ['location', 'total_cases', 'new_cases', 'total_deaths', 'new_deaths',
                                          "population", "total_vaccinations", "total_cases_per_million",
                                          "total_deaths_per_million"][idx]}
                     for (idx, col) in enumerate(['Country', 'Confirmed', '\u21E7 Cases', 'Deaths', '\u21E7 Deaths',
                                                  "Population", "Vaccination", "Confirm/1M", "Deaths/1M"])],
            fixed_rows={'headers': True},
            style_table={'max-height': '300px', 'overflowY': 'auto'},
            style_cell_conditional=[
                {'if': {'column_id': 'location'},
                 'width': '15%', 'textAlign': 'left', },
            ],
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
                'width': '7%',
            },
            # Remove vertical lines
            style_as_list_view=True,
            sort_action="native",)],
            style={"margin": "3%", "border": "2px black solid"}),

        html.Div([dcc.Dropdown(
            id='country_name_dropdown',
            options=country_name_list,
            value='United States',
        )], style={'width': '20%', 'display': 'inline-block', 'margin-left': '3%'}),

        html.Div([
            dcc.Graph(id='total_cases_by_country', figure={}, style={"max-width": "50%"}),
            dcc.Graph(id='daily_cases_by_country', figure={}, style={"max-width": "50%"})],
            style={'display': 'flex', 'width': '100%'}),

        html.Div([
            dcc.Graph(id='total_deaths_by_country', figure={}, style={"max-width": "50%"}),
            dcc.Graph(id='daily_deaths_by_country', figure={}, style={"max-width": "50%"})
        ],
            style={'display': 'flex', 'width': '100%'}),

        html.Div(id='news_location'),
        # html.Div(id='dummy', style={"display": "none"}),
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
