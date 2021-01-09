import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import json
import requests
import datetime as datetime
# Make it less laggy
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}
# C:\Users\Acer\PycharmProjects\temp\owid-covid-data.csv
# https://covid.ourworldindata.org/data/owid-covid-data.csv
# df = pd.read_csv(r'C:\Users\Acer\PycharmProjects\temp\owid-covid-data.csv')
df = pd.read_csv(r'https://covid.ourworldindata.org/data/owid-covid-data.csv')
df[df['new_cases'] < 0] = 0
df = df.iloc[:, :10]
df = df[df['continent'].notna()]
df = df[df['date'].notna()]
df = df[df['date'] != 0]
df.fillna(0, inplace=True)
# df.to_csv('covid-data.csv')

df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
group_continent = pd.read_csv('covid-data.csv')
country_name_list = []
for country_name in df['location'].unique():
    country_name_list.append({'label': country_name, 'value': country_name})

# transform every unique date to a number
numdate = [x for x in range(0, len(df['date'].unique()) + 30, 30)]


def generate_thumbnail(news_title, news_description, news_url, news_image_url):
    return html.Div([
        html.Img(src=news_image_url,
                 style={
                     "width": "100%",
                 }
                 ),
        html.A(news_title, href=news_url, target='_blank'),
    ],
        style={"border": "2px black solid", "text-align": "left", "display": "inline-block", "font-size": "15px",
               "padding": "1px", "width": "300px"})


# all_news = []
# url = ('http://newsapi.org/v2/everything?'
#        'language=en&'
#        'q=covid-19&'
#        'from=2020-10-21&'
#        'sources=bbc-news&'
#        'sortBy=popularity&'
#        'apiKey=bf25476268b640d0a6972e685f1c7215')
#
# response = requests.get(url)
# for news in response.json()['articles']:
#     if 'covid' in news['description'].lower() or 'coronavirus' in news['description'].lower() or 'pandemic' in news[
#         'description'].lower() \
#             or 'coronavirus' in news['title'].lower() or 'covid' in news['title'].lower():
#         all_news.append(generate_thumbnail(news['title'], news['description'], news['url'], news['urlToImage']))

df_cols = ['Country', 'Total Cases', 'New Cases', 'Total Deaths', 'New Deaths']

app.layout = html.Div(style={'backgroundColor': '#f1f1f1'}, children=[
    # 'backgroundColor': '#000033'
    html.H1('Coronavirus Disease (COVID-19) Dashboard', style={'text-align': 'center'}),

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
        html.Div(id='new_cases',
                 style={"border-radius": "5px", "text-align": "center", "width": "19%",  # "border": "1px solid",
                        "font-size": "1.7vw", 'display': 'inline-block', 'margin-right': '4%',
                        'background-color': '#F5765B'}),

        html.Div(id='new_deaths',
                 style={"border-radius": "5px", "text-align": "center", "width": "19%",
                        "font-size": "1.7vw", 'display': 'inline-block', 'margin-right': '4%',
                        'background-color': '#F5765B'}),

        html.Div(id='total_cases',
                 style={"border-radius": "5px", "text-align": "center", "width": "19%",
                        "font-size": "1.7vw", 'display': 'inline-block', 'margin-right': '4%',
                        'background-color': '#F5765B'}),
        html.Div(id='total_deaths',
                 style={"border-radius": "5px", "text-align": "center", "width": "19%",
                        "font-size": "1.7vw", 'display': 'inline-block', 'background-color': '#F5765B'}),
    ], style={"display": "flex", "align-items": "center", "justify-content": "center"}),

    dcc.Graph(id='graph', figure={}, style={"width": "80%", "margin": "3%"}),  # "border": "2px black solid",

    dcc.Dropdown(
        id='deaths_or_cases',
        options=[
            {'label': "Cases", 'value': 'Cases'},
            {'label': 'Deaths', 'value': 'Deaths'},
        ],
        value='Cases',
        style={'width': '40%', 'display': 'inline-block', "margin-left": "3%"},
    ),

    dcc.Graph(id='total_by_continent', figure={}, style={"width": "80%", "margin": "3%"}),

    dcc.Graph(id='daily_by_continent', figure={}, style={"width": "80%", "margin": "3%", "border-radius": "5px"}),

    html.Div([dash_table.DataTable(
        columns=[{"name": col, "id": ['location', 'total_cases', 'new_cases', 'total_deaths', 'new_deaths'][idx]} for (idx, col) in enumerate(['Country', 'Total Cases', 'New Cases', 'Total Deaths', 'New Deaths'])],
        data=df[['location', 'total_cases', 'new_cases', 'total_deaths', 'new_deaths']][
            df['date'] == df['date'].max()].to_dict('records'),
        page_action='none',
        fixed_rows={'headers': True},
        style_table={'height': '300px', 'overflowY': 'auto'},
        style_cell_conditional=[
            {'if': {'column_id': 'location'},
             'width': '28%', 'textAlign': 'left'},
            {'if': {'column_id': 'new_cases'},
             'width': '18%', 'textAlign': 'left'},
            {'if': {'column_id': 'total_cases'},
             'width': '18%', 'textAlign': 'left'},
            {'if': {'column_id': 'total_deaths'},
             'width': '18%', 'textAlign': 'left'},
            {'if': {'column_id': 'new_deaths'},
             'width': '18%', 'textAlign': 'left'},
        ],
        style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold',
            'fontSize': '15px',
            'marginLeft': '3px',
        },
        style_cell={
            'fontSize': '15px',
        },
        # style_as_list_view=True,
        # filter_action="native",
        sort_action="native",
        ), ],
             style={"width": "80%", "margin": "3%", "border": "2px black solid"}),

    html.Div([dcc.Dropdown(
        id='country_name_dropdown',
        options=country_name_list,
        value='United States',
        style={'width': '40%', 'display': 'inline-block', "margin-left": "3%"},
    ),

        dcc.Dropdown(
            id='daily_or_sum_stats',
            options=[
                {'label': "Total", 'value': 'Total'},
                {'label': "Daily", 'value': 'Daily'}],
            value='Total',
            style={'width': '300px', 'display': 'inline-block'},
        )]),

    dcc.Graph(id='cases_by_country', figure={}, style={"width": "80%", "margin": "3%"}),

    dcc.Graph(id='deaths_by_country', figure={}, style={"width": "80%", "margin": "3%"}),

    # html.Div(id='news_location', children={}),
    # html.Button('<', id='previous_news', n_clicks=0),
    # html.Button('>', id='next_news', n_clicks=0),
    # html.Div(id='container-button-basic',
    #          children='Enter a value and press submit')
])


@app.callback(
    Output(component_id='new_cases', component_property='children'),
    Output(component_id='new_deaths', component_property='children'),
    Output(component_id='total_cases', component_property='children'),
    Output(component_id='total_deaths', component_property='children'),
    Input(component_id='date', component_property='date')
)
def stats(date_selected):
    new_cases = "NEW CASES", html.Br(), html.Div([df['new_cases'][df['date'] == date_selected].sum()],
                                                 style={'background-color': 'white', 'margin': '2%',
                                                        'border-radius': '3px', 'font-size': '2vw'})
    new_deaths = "NEW DEATHS", html.Br(), html.Div([df['new_deaths'][df['date'] == date_selected].sum()],
                                                   style={'background-color': 'white', 'margin': '2%',
                                                          'border-radius': '3px', 'font-size': '2vw'})
    total_cases = "TOTAL CASES", html.Br(), html.Div([df['new_cases'][df['date'] <= date_selected].sum()],
                                                     style={'background-color': 'white', 'margin': '2%',
                                                            'border-radius': '3px', 'font-size': '2vw'})
    total_deaths = "TOTAL DEATHS", html.Br(), html.Div([df['new_deaths'][df['date'] <= date_selected].sum()],
                                                       style={'background-color': 'white', 'margin': '2%',
                                                              'border-radius': '3px', 'font-size': '2vw'})
    return new_cases, new_deaths, total_cases, total_deaths


@app.callback(
    Output(component_id='graph', component_property='figure'),
    Input('type_of_stats', 'value'),
    Input(component_id='date', component_property='date')
)
def world_graph(stats_chosen, date_selected):
    dff = df[df['date'] == date_selected]

    if stats_chosen == 'today':
        stats_chosen, title = 'new_cases', 'NEW CASES'
    else:
        stats_chosen, title = 'total_cases', 'TOTAL CASES'

    fig = go.Figure(data=go.Scattergeo(
        locations=dff["iso_code"],
        text=dff[stats_chosen],
        mode='markers',
        marker=dict(
            color=dff[stats_chosen],
            colorbar=dict(
                title=title,
                titlefont={"size": 19, "color": "black"},
                tickfont={"size": 15, "color": "black"},
            ),
            colorscale="Burg",
            size=dff[stats_chosen],
            sizemode='area',
            sizeref=1. * max(dff[stats_chosen]) / (50. ** 2),
            sizemin=3,
        ),
        line=dict(color="black"),
    ),
        layout=go.Layout(geo=dict(bgcolor='rgba(0,0,0,0)'),
                         paper_bgcolor='white',
                         plot_bgcolor='white',
                         )
    )

    fig.update_geos(
        resolution=50,
        showcoastlines=True, coastlinecolor="RebeccaPurple",
        showland=True, landcolor="White",
        showocean=True, oceancolor="#4E5D6C",  # #4E5D6C
    )
    fig.update_layout(
        # title_text='Number of Covid-19 Cases Daily',
        # width='1500',
        # autosize=False,
        height=700,
        margin=go.layout.Margin(
            l=10,
            r=10,
            b=10,
            t=10,
            pad=1,
        ),
        geo=dict(
            showframe=False,
            projection_type='equirectangular',
        ),
        showlegend=False,
    )

    return fig


@app.callback(
    Output(component_id='total_by_continent', component_property='figure'),
    Output(component_id='daily_by_continent', component_property='figure'),
    Input(component_id='deaths_or_cases', component_property='value')
)
def line_chart_continent(by_deaths_or_cases):
    # https://plotly.com/python/axes/#set-axis-title-text-with-plotly-express
    list_of_continent = list(group_continent['continent'].unique())
    if by_deaths_or_cases == 'Cases':
        title = 'Cases by Continent'
        total_cases = []
        for continent in list_of_continent:
            total_cases.append(group_continent[group_continent['continent'] == continent].max()['total_cases'])
        df = pd.DataFrame({'Continent': list_of_continent, 'Total Cases': total_cases})
        total_by_continent = px.bar(df, x="Total Cases", y="Continent", color="Continent", text="Total Cases",
                                    template="simple_white")
        total_by_continent.update_traces(texttemplate='%{text:.5s}', textposition='outside',
                                         hovertemplate='Continent: %{y} <br>Cases: %{x}  <extra></extra>', )
        total_by_continent.update_layout(showlegend=False, )

        sort_by_continent = px.bar(group_continent, x="date", y="new_cases", color="continent",
                                   hover_name="continent", template="simple_white",
                                   labels={"continent": "Continent", "new_cases": "New Cases", "date": "Date"},
                                   )
    else:
        title = 'Deaths by Continent'
        total_deaths = []
        for continent in list_of_continent:
            total_deaths.append(group_continent[group_continent['continent'] == continent].max()['total_deaths'])
        df = pd.DataFrame({'Continent': list_of_continent, 'Total Deaths': total_deaths})
        total_by_continent = px.bar(df, x="Total Deaths", y="Continent", color="Continent", text="Total Deaths",
                                    template="simple_white")
        total_by_continent.update_traces(texttemplate='%{text:.5s}', textposition='outside',
                                         hovertemplate='Continent: %{y} <br>Deaths: %{x}  <extra></extra>', )
        total_by_continent.update_layout(showlegend=False, )
        sort_by_continent = px.bar(group_continent, x="date", y="new_deaths", color="continent",
                                   hover_name="continent", template="simple_white",
                                   labels={"continent": "Continent", "new_deaths": "New Deaths", "date": "Date"},
                                   )
    sort_by_continent.update_layout(
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ),
        plot_bgcolor="White",
        paper_bgcolor='White',
        title=title,
        titlefont={"size": 19, "color": "Black"},
        xaxis=dict(
            tickfont={"size": 15, "color": "Black"}
        ),
        yaxis=dict(
            tickfont={"size": 15, "color": "Black"}
        ),
    )

    sort_by_continent.update_xaxes(showline=True, linewidth=2, linecolor='Black',
                                   titlefont={"size": 19, "color": "Black"}, ticks="inside", tickwidth=1,
                                   tickcolor='White', ticklen=5)
    sort_by_continent.update_yaxes(showline=True, linewidth=2, linecolor='Black',
                                   titlefont={"size": 19, "color": "Black"}, ticks="inside", tickwidth=1,
                                   tickcolor='White', ticklen=5)

    return total_by_continent, sort_by_continent


@app.callback(
    Output(component_id='cases_by_country', component_property='figure'),
    Output(component_id='deaths_by_country', component_property='figure'),
    Input('country_name_dropdown', 'value'),
    Input('daily_or_sum_stats', 'value')
)
def line_chart_country(country_name, stats_chosen):
    if stats_chosen == 'Total':
        cases_by_country = px.bar(df[df['location'] == country_name], x="date", y="total_cases", color="location",
                                  hover_name="location", template="simple_white",
                                  labels={"location": "Country", "date": "Date", "total_cases": "Total Cases"}, )
        deaths_by_country = px.bar(df[df['location'] == country_name], x="date", y="total_deaths", color="location",
                                   # line_group="location",
                                   hover_name="location", template="simple_white",
                                   labels={"location": "Country", "date": "Date", "total_deaths": "Total Deaths"}, )
    else:
        cases_by_country = px.bar(df[df['location'] == country_name], x="date", y="new_cases", color="location",
                                  hover_name="location", template="simple_white",
                                  labels={"location": "Country", "date": "Date", "new_cases": "New Cases"}, )
        deaths_by_country = px.bar(df[df['location'] == country_name], x="date", y="new_deaths", color="location",
                                   hover_name="location", template="simple_white",
                                   labels={"location": "Country", "date": "Date", "new_deaths": "New Deaths"},
                                   )
    cases_by_country.update_layout(
        showlegend=False,
        plot_bgcolor="White",
        paper_bgcolor='White',
        title=stats_chosen + ' Cases in ' + country_name,
        titlefont={"size": 19, "color": "Black"},
        xaxis=dict(
            tickfont={"size": 15, "color": "Black"}
        ),
        yaxis=dict(
            tickfont={"size": 15, "color": "Black"}
        ),
    )
    cases_by_country.update_xaxes(showline=True, linewidth=2, linecolor='Black',
                                  titlefont={"size": 19, "color": "Black"}, ticks="inside", tickwidth=1,
                                  tickcolor='White', ticklen=5)
    cases_by_country.update_yaxes(showline=True, linewidth=2, linecolor='Black',
                                  titlefont={"size": 19, "color": "Black"}, ticks="inside", tickwidth=1,
                                  tickcolor='White', ticklen=5)

    deaths_by_country.update_layout(
        showlegend=False,
        plot_bgcolor="White",
        paper_bgcolor='White',
        title=stats_chosen + ' Deaths in ' + country_name,
        titlefont={"size": 19, "color": "Black"},
        xaxis=dict(
            tickfont={"size": 15, "color": "Black"}
        ),
        yaxis=dict(
            tickfont={"size": 15, "color": "Black"}
        )
    )
    deaths_by_country.update_xaxes(showline=True, linewidth=2, linecolor='Black',
                                  titlefont={"size": 19, "color": "Black"}, ticks="inside", tickwidth=1,
                                  tickcolor='White', ticklen=5)
    deaths_by_country.update_yaxes(showline=True, linewidth=2, linecolor='Black',
                                  titlefont={"size": 19, "color": "Black"}, ticks="inside", tickwidth=1,
                                  tickcolor='White', ticklen=5)

    return cases_by_country, deaths_by_country


# @app.callback(
#     Output('container-button-basic', 'children'),
#     Output('news_location', 'children'),
#     Input('next_news', 'n_clicks'),)
# def update_output(n_clicks):
#     return 'The input value was and the button has been clicked {} times'.format(
#         n_clicks
#     ), all_news[n_clicks:]
#
#
# @app.callback(
#     Output('container-button-basic', 'children'),
#     Output('news_location', 'children'),
#     Input('next_news', 'n_clicks'),)
# def update_output(n_clicks):
#     return 'The input value was and the button has been clicked {} times'.format(
#         n_clicks
#     ), all_news[n_clicks:]
#

if __name__ == '__main__':
    app.run_server(debug=True)
