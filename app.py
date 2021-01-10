import dash
import dash_table
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import json
import requests
import time
import datetime as datetime

app = dash.Dash(__name__, title='Covid-19 Analytics',
                external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'],
                meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}])

colors = {
    'bg': '#010310',
    'text': '#F4E808'
}

df = pd.read_csv(r'C:\Users\Acer\PycharmProjects\temp\owid-covid-data.csv')
# df = pd.read_csv(r'https://covid.ourworldindata.org/data/owid-covid-data.csv')

# Identify rows that have new cases less than 0, which is impossible
df[df['new_cases'] < 0] = 0

# Get just the relevant columns
df = df[["iso_code", "continent", "location", "date", "total_cases", "new_cases", "total_deaths", "new_deaths",
         "total_cases_per_million", "new_cases_per_million", "total_deaths_per_million", "new_deaths_per_million", "population"]]

# Continent that are N.A. means total world statistics
df = df[df['continent'].notna()]

# Remove rows that are wrong value / empty
df = df[df['date'].notna()]
df = df[df['date'] != 0]
df = df[df['total_cases'].notna()]
df = df.round(2)

# Replace all N.A. with 0 for easy manipulation of data
df.fillna(0, inplace=True)
# df.to_csv('covid-data.csv')

# Convert column from string to date object
df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
group_continent = pd.read_csv('covid-data.csv')

country_name_list = []
for country_name in df['location'].unique():
    country_name_list.append({'label': country_name, 'value': country_name})

# transform every unique date to a number
numdate = [x for x in range(0, len(df['date'].unique()) + 30, 30)]


############################################################################################
# @app.callback(
#     Output("loading-output", "children"), [Input(component_id='total_by_continent', component_property='figure'),
#     Input(component_id='daily_by_continent', component_property='figure')]
# )
# def load_output(n, i):
#     if n:
#         time.sleep(1)
#         return f"Output loaded {datetime.datetime.now()} times"
#     return "Output not reloaded yet"

############################################################################################


def generate_thumbnail(news_title, news_description, news_url, news_image_url):
    return html.Div([
        html.Img(src=news_image_url,
                 style={"width": "100%"}),
        html.A(news_title, href=news_url, target='_blank'),
    ], className="newspaper_thumbnail")


all_news = []
url = ('http://newsapi.org/v2/everything?'
       'language=en&'
       'q=covid-19&'
       'from=2020-12-31&'
       'sources=bbc-news&'
       'sortBy=popularity&'
       'apiKey=bf25476268b640d0a6972e685f1c7215')

response = requests.get(url)

for news in response.json()['articles']:
    if 'covid' in news['description'].lower() or 'coronavirus' in news['description'].lower() or 'pandemic' in news[
        'description'].lower() \
            or 'coronavirus' in news['title'].lower() or 'covid' in news['title'].lower():
        all_news.append(generate_thumbnail(news['title'], news['description'], news['url'], news['urlToImage']))

df_cols = ['Country', 'Total Cases', 'New Cases', 'Total Deaths', 'New Deaths']

items = [
    dbc.DropdownMenuItem("Item 1"),
    dbc.DropdownMenuItem("Item 2"),
    dbc.DropdownMenuItem("Item 3"),
]

app.layout = html.Div(style={'backgroundColor': colors['bg']}, children=[

    # html.Div(
    #     [
    #         dbc.Button("Load", id="loading-button"),
    #         dbc.Spinner(html.Div(id="loading-output"), fullscreen=True, color="primary"),
    #     ]
    # ),

    html.H1('Coronavirus Disease (COVID-19) Dashboard', className="title"),

    html.Div([dcc.DatePickerSingle(id='date', min_date_allowed=min(df['date']), max_date_allowed=df['date'].max(),
                                   date=str(df['date'].max()).split(' ')[0],
                                   style={'display': 'inline-block', 'vertical-align': 'top', 'border-radius': '5px'}),

              dcc.Dropdown(
                  id='type_of_stats',
                  options=[
                      {'label': "Daily Statistics", 'value': 'today'},
                      {'label': 'Total Statistics', 'value': 'total'},
                  ],
                  value='today',
                  style={'width': '40%', 'display': 'inline-block', "margin-left": "3%", 'vertical-align': 'top',
                         'border-radius': '5px'},
            ), ]),

    html.Div([
        html.Div(id='new_cases', className="daily_stats_thumbnail"),
        html.Div(id='new_deaths', className="daily_stats_thumbnail"),
        html.Div(id='total_cases', className="daily_stats_thumbnail"),
        html.Div(id='total_deaths', className="daily_stats_thumbnail"),
    ], className="daily_stats_thumbnail_display"),

    dcc.Graph(id='graph', figure={}, style={"margin": "3%", "color": "#F4E808"}),  # "border": "2px black solid",

    dcc.Dropdown(
        id='deaths_or_cases',
        options=[
            {'label': "Cases", 'value': 'Cases'},
            {'label': 'Deaths', 'value': 'Deaths'},
        ],
        value='Cases',
        style={'width': '40%', 'display': 'inline-block', "margin-left": "3%"},
    ),
    # dbc.DropdownMenu([dbc.DropdownMenuItem("Cases"), dbc.DropdownMenuItem("Deaths")], label="Cases", color="primary"),
    # dcc.Graph(id='total_by_continent', figure={}, style={"margin": "3%"}),

    # dcc.Graph(id='daily_by_continent', figure={}, style={"margin": "3%", "border-radius": "5px"}),

    html.Div([dash_table.DataTable(
        id="table_stats",
        columns=[{"name": col, "id": ['location', 'total_cases', 'new_cases', 'total_deaths', 'new_deaths',
                                      "population", "total_cases_per_million", "total_deaths_per_million"][idx]}
                 for (idx, col) in enumerate(['Country', 'Confirmed', '\u21E7 Cases', 'Deaths', '\u21E7 Deaths',
                                              "Population", "Confirm/1M", "Deaths/1M"])],
        # page_action='none',
        fixed_rows={'headers': True},
        style_table={'height': '300px', 'overflowY': 'auto'},
        style_cell_conditional=[
            {'if': {'column_id': 'location'},
             'width': '15%', 'textAlign': 'left'}],
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
        sort_action="native",)],
        style={"margin": "3%", "border": "2px black solid"}),

    html.Div([dcc.Dropdown(
        id='country_name_dropdown',
        options=country_name_list,
        value='United States',
        style={'width': '40%', 'display': 'inline-block', "margin-left": "3%"},
    ),
        # dcc.Dropdown(
        #     id='daily_or_sum_stats',
        #     options=[
        #         {'label': "Total", 'value': 'Total'},
        #         {'label': "Daily", 'value': 'Daily'}],
        #     value='Total',
        #     style={'width': '300px', 'display': 'inline-block'},
        # )]),
    html.Div([
        dcc.Graph(id='total_cases_by_country', figure={}), dcc.Graph(id='daily_cases_by_country', figure={}),
        dcc.Graph(id='total_deaths_by_country', figure={}), dcc.Graph(id='daily_deaths_by_country', figure={})],
        style={'display': 'flex'}),

    html.Div(id='news_location'),
    html.Button('<', id='previous_news', n_clicks=0),
    html.Button('>', id='next_news', n_clicks=0),
    html.Div(id='container-button-basic',
             children='Enter a value and press submit')
])])


@app.callback(
    Output(component_id='table_stats', component_property='data'),
    Input(component_id='date', component_property='date'),
)
def table_data(date_selected):
    data_contents = df[df['date'] == date_selected].to_dict('records')
    return data_contents


@app.callback(
    Output(component_id='new_cases', component_property='children'),
    Output(component_id='new_deaths', component_property='children'),
    Output(component_id='total_cases', component_property='children'),
    Output(component_id='total_deaths', component_property='children'),
    Input(component_id='date', component_property='date')
)
def stats(date_selected):
    new_cases = "NEW CASES", html.Br(), html.Div([df['new_cases'][df['date'] == date_selected].sum()],
                                                    className="daily_stats_thumbnail_inner_div")
    new_deaths = "NEW DEATHS", html.Br(), html.Div([df['new_deaths'][df['date'] == date_selected].sum()],
                                                   className="daily_stats_thumbnail_inner_div")
    total_cases = "TOTAL CASES", html.Br(), html.Div([df['new_cases'][df['date'] <= date_selected].sum()],
                                                      className="daily_stats_thumbnail_inner_div")
    total_deaths = "TOTAL DEATHS", html.Br(), html.Div([df['new_deaths'][df['date'] <= date_selected].sum()],
                                                        className="daily_stats_thumbnail_inner_div")
    return new_cases, new_deaths, total_cases, total_deaths


@app.callback(
    Output(component_id='graph', component_property='figure'),
    Input('type_of_stats', 'value'),
    Input(component_id='date', component_property='date')
)
def world_graph(stats_chosen, date_selected):
    dff = df[df['date'] == date_selected]

    if stats_chosen == 'today':
        stats_chosen = 'new_cases'
    else:
        stats_chosen = 'total_cases'

    fig = go.Figure(data=go.Scattergeo(
        locations=dff["iso_code"],
        text=dff[stats_chosen],
        mode='markers',
        marker=dict(
            color=dff[stats_chosen],
            colorscale="Burg",
            size=dff[stats_chosen],
            sizemode='area',
            sizeref=1. * max(dff[stats_chosen]) / (50. ** 2),
            sizemin=3,
        ),
        line=dict(color="black"),
    ),
        layout=go.Layout(geo=dict(bgcolor='#010310'),
                         paper_bgcolor='#010310',))
    fig.update_geos(
        resolution=50,
        showcoastlines=True, coastlinecolor="#071260",
        showland=True, landcolor="#071260",
        showocean=True, oceancolor="#010310",
    )
    fig.update_layout(
        # title_text='Number of Covid-19 Cases Daily',
        # title_font_color=colors['text'],
        width=800,
        # autosize=True,
        # height=700,
        margin=go.layout.Margin(
            l=0,
            r=0,
            b=0,
            t=00,
            pad=1,
        ),
        geo=dict(
            showframe=False,
            projection_type='equirectangular',
        ),
        showlegend=False,
    )
    return fig


# @app.clientside_callback(
#     """
#     function(by_deaths_or_cases) {
#         list_of_continent =
#         return total_by_continent, sort_by_continent
#     }
#     """,
#     Output(component_id='total_by_continent', component_property='figure'),
#     Output(component_id='daily_by_continent', component_property='figure'),
#     Input(component_id='deaths_or_cases', component_property='value')
# )


# @app.callback(
#     Output(component_id='total_by_continent', component_property='figure'),
#     Output(component_id='daily_by_continent', component_property='figure'),
#     Input(component_id='deaths_or_cases', component_property='value')
# )
# def line_chart_continent(by_deaths_or_cases):
#     # https://plotly.com/python/axes/#set-axis-title-text-with-plotly-express
#     list_of_continent = list(group_continent['continent'].unique())
#     if by_deaths_or_cases == 'Cases':
#         title = 'Cases by Continent'
#         total_cases = []
#         for continent in list_of_continent:
#             total_cases.append(group_continent[group_continent['continent'] == continent].max()['total_cases'])
#         df = pd.DataFrame({'Continent': list_of_continent, 'Total Cases': total_cases})
#         total_by_continent = px.bar(df, x="Total Cases", y="Continent", color="Continent", text="Total Cases",
#                                     template="simple_white")
#         total_by_continent.update_traces(texttemplate='%{text:.5s}', textposition='outside',
#                                          hovertemplate='Continent: %{y} <br>Cases: %{x}  <extra></extra>',)
#         total_by_continent.update_layout(showlegend=False,
#                                          paper_bgcolor="#010310",
#                                          plot_bgcolor="#010310",
#                                          xaxis=dict(tickfont={"size": 15, "color": "#F4E808"}),
#                                          yaxis=dict(tickfont={"size": 15, "color": "#F4E808"}),)
#
#         # Colour of axes -> the straight line only
#         total_by_continent.update_xaxes(title_font=dict(color="#F4E808"))
#         total_by_continent.update_yaxes(title_font=dict(color="#F4E808"))
#
#         sort_by_continent = px.bar(group_continent, x="date", y="new_cases", color="continent",
#                                    hover_name="continent",
#                                    labels={"continent": "Continent", "new_cases": "New Cases", "date": "Date"},
#                                    template="simple_white",
#                                    )
#     else:
#         title = 'Deaths by Continent'
#         total_deaths = []
#         for continent in list_of_continent:
#             total_deaths.append(group_continent[group_continent['continent'] == continent].max()['total_deaths'])
#         df = pd.DataFrame({'Continent': list_of_continent, 'Total Deaths': total_deaths})
#         total_by_continent = px.bar(df, x="Total Deaths", y="Continent", color="Continent", text="Total Deaths",
#                                     template="simple_white")
#         total_by_continent.update_traces(texttemplate='%{text:.5s}', textposition='outside',
#                                          hovertemplate='Continent: %{y} <br>Deaths: %{x}  <extra></extra>', textfont_color='#F4E808')
#         total_by_continent.update_layout(showlegend=False,
#                                          paper_bgcolor="#010310",
#                                          plot_bgcolor="#010310",
#                                          # xaxis, yaxis refers to the labels on the axes
#                                          xaxis=dict(tickfont={"size": 15, "color": "#F4E808"}),
#                                          yaxis=dict(tickfont={"size": 15, "color": "#F4E808"}),
#                                          )
#         total_by_continent.update_xaxes(title_font=dict(color="#F4E808"))
#         total_by_continent.update_yaxes(title_font=dict(color="#F4E808"))
#
#         sort_by_continent = px.bar(group_continent, x="date", y="new_deaths", color="continent",
#                                    hover_name="continent", template="simple_white",
#                                    labels={"continent": "Continent", "new_deaths": "New Deaths", "date": "Date"},
#                                    )
#     sort_by_continent.update_layout(
#         showlegend=True,
#         legend=dict(
#             yanchor="top",
#             y=0.99,
#             xanchor="left",
#             x=0.01,
#             font=dict(color="white"),
#             # bgcolor='',
#             # bordercolor
#         ),
#         plot_bgcolor="#010310",
#         paper_bgcolor='#010310',
#         title=title,
#         titlefont={"size": 19, "color": "#F4E808"},
#         # Labels on axes
#         xaxis=dict(
#             tickfont={"size": 15, "color": "#F4E808"}
#         ),
#         yaxis=dict(
#             tickfont={"size": 15, "color": "#F4E808"}
#         ),
#     )
#
#     sort_by_continent.update_xaxes(showline=True, linewidth=2, linecolor='Black',
#                                    titlefont={"size": 19, "color": "Black"}, ticks="inside", tickwidth=1,
#                                    tickcolor='#F4E808', ticklen=5)
#     sort_by_continent.update_yaxes(showline=True, linewidth=2, linecolor='Black',
#                                    titlefont={"size": 19, "color": "Black"}, ticks="inside", tickwidth=1,
#                                    tickcolor='#F4E808', ticklen=5)
#
#     return total_by_continent, sort_by_continent


@app.callback(
    Output(component_id='total_cases_by_country', component_property='figure'),
    Output(component_id='total_deaths_by_country', component_property='figure'),
    Output(component_id='daily_cases_by_country', component_property='figure'),
    Output(component_id='daily_deaths_by_country', component_property='figure'),
    Input('country_name_dropdown', 'value'),
)
def line_chart_country(country_name):

    total_cases_by_country = px.bar(df[df['location'] == country_name], x="date", y="total_cases", color="location",
                              hover_name="location", template="simple_white",
                              labels={"location": "Country", "date": "Date", "total_cases": "Total Cases"}, )
    total_deaths_by_country = px.bar(df[df['location'] == country_name], x="date", y="total_deaths", color="location",
                               hover_name="location", template="simple_white",
                                     labels={"location": "Country", "date": "Date", "total_deaths": "Total Deaths"})
    daily_cases_by_country = px.bar(df[df['location'] == country_name], x="date", y="new_cases", color="location",
                              hover_name="location", template="simple_white",
                              labels={"location": "Country", "date": "Date", "new_cases": "New Cases"}, )
    daily_deaths_by_country = px.bar(df[df['location'] == country_name], x="date", y="new_deaths", color="location",
                               hover_name="location", template="simple_white",
                               labels={"location": "Country", "date": "Date", "new_deaths": "New Deaths"})
    title_format = ['Daily', 'Total']
    for index, graph in enumerate([total_cases_by_country, daily_cases_by_country]):
        graph.update_layout(
            showlegend=False,
            plot_bgcolor="#010310",
            paper_bgcolor='#010310',
            title=title_format[index] + ' Cases in ' + country_name,
            titlefont={"size": 12, "color": "#F4E808"},
            xaxis=dict(
                tickfont={"size": 12, "color": "#F4E808"}
            ),
            yaxis=dict(
                tickfont={"size": 12, "color": "#F4E808"}
            ),

        )
        # axes legend
        graph.update_xaxes(showline=True, linewidth=2, linecolor='#F4E808',
                                      titlefont={"size": 14, "color": "#F4E808"}, ticks="inside", tickwidth=1,
                                      tickcolor='#F4E808', ticklen=5)
        graph.update_yaxes(showline=True, linewidth=2, linecolor='#F4E808',
                                      titlefont={"size": 14, "color": "#F4E808"}, ticks="inside", tickwidth=1,
                                      tickcolor='#F4E808', ticklen=5)
    for index, graph in enumerate([total_deaths_by_country, daily_deaths_by_country]):
        graph.update_layout(
            showlegend=False,
            plot_bgcolor="#010310",
            paper_bgcolor='#010310',
            title= title_format[index] + ' Deaths in ' + country_name,
            titlefont={"size": 12, "color": "#F4E808"},
            xaxis=dict(
                tickfont={"size": 12, "color": "#F4E808"}
            ),
            yaxis=dict(
                tickfont={"size": 12, "color": "#F4E808"}
            )
        )
        graph.update_xaxes(showline=True, linewidth=2, linecolor='#F4E808',
                                      titlefont={"size": 14, "color": "#F4E808"}, ticks="inside", tickwidth=1,
                                      tickcolor='#F4E808', ticklen=5)
        graph.update_yaxes(showline=True, linewidth=2, linecolor='#F4E808',
                                      titlefont={"size": 14, "color": "#F4E808"}, ticks="inside", tickwidth=1,
                                      tickcolor='#F4E808', ticklen=5)

    return total_cases_by_country, total_deaths_by_country, daily_cases_by_country, daily_deaths_by_country


@app.callback(
    Output('container-button-basic', 'children'),
    Output('news_location', 'children'),
    Input('next_news', 'n_clicks'),)
def update_output(n_clicks):
    return 'The input value was and the button has been clicked {} times'.format(
        n_clicks
    ), all_news[n_clicks:]


if __name__ == '__main__':
    app.run_server(debug=True)
