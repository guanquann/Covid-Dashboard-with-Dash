import dash
import plotly.graph_objects as go
import plotly.express as px
import time

from layout import *
from callbacks import *
from get_data import *

app = dash.Dash(__name__, title='Covid-19 Analytics',
                external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css', dbc.themes.BOOTSTRAP],
                meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}])


# df = pd.read_csv(r'https://covid.ourworldindata.org/data/owid-covid-data.csv')
df, country_name_list, numdate = latest_covid_data(r'https://covid.ourworldindata.org/data/owid-covid-data.csv')

df_cols = ['Country', 'Total Cases', 'New Cases', 'Total Deaths', 'New Deaths']


@app.callback(
    Output("loading-output", "children"), [Input("date", "date")]
)
def load_output(n):
    if n:
        time.sleep(3.5)
    return


app.layout = make_layout()


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
    Output(component_id='total_vaccines', component_property='children'),
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
    total_vaccines = "TOTAL VACCINES", html.Br(), html.Div([df['total_vaccinations'][df['date'] <= date_selected]
                                                           .sum()], className="daily_stats_thumbnail_inner_div")
    return new_cases, new_deaths, total_cases, total_deaths, total_vaccines


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
            # color=dff[stats_chosen],
            # colorscale="reds",
            color="#EC7575",
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
        # default resolution is 110, which is much faster/less lag. But less countries shown
        # resolution=50,
        showcoastlines=True, coastlinecolor="#071260",
        showland=True, landcolor="#071260",
        showocean=True, oceancolor="#010310",
        showlakes=True, lakecolor="#010310",
        showcountries=True,
    )
    fig.update_layout(
        # title_text='Number of Covid-19 Cases Daily',
        # title_font_color=colors['text'],
        # width=800,
        # autosize=True,
        height=350,
        # Do this to minimise space between graph and outer div
        margin=go.layout.Margin(l=0, r=0, b=0, t=0,),
        geo=dict(
            showframe=False,
            projection_type='equirectangular',
        ),
        showlegend=False,
    )

    return fig


@app.callback(
    Output(component_id='total_cases_by_continent', component_property='figure'),
    Output(component_id='total_deaths_by_continent', component_property='figure'),
    Output(component_id='total_vaccines_by_continent', component_property='figure'),
    Input(component_id='date', component_property='date'),
    Input(component_id='type_of_stats', component_property='value')
)
def world_stats(date, stats_chosen):
    # https://plotly.com/python/axes/#set-axis-title-text-with-plotly-express
    list_of_continent = list(df['continent'].unique())
    if stats_chosen == 'total':
        cases = []
        for continent in list_of_continent:
            # () is necessary when using & inside df
            cases.append(df[(df['continent'] == continent) & (df['date'] == date)].sum()['total_cases'])
        graph_df = pd.DataFrame({'Continent': list_of_continent, 'Total Cases': cases})
        cases_by_continent = px.bar(graph_df, x="Total Cases", y="Continent", color="Continent", text="Total Cases",
                                    template="simple_white")

        deaths = []
        for continent in list_of_continent:
            deaths.append(df[(df['continent'] == continent) & (df['date'] == date)].sum()['total_deaths'])
        graph_df = pd.DataFrame({'Continent': list_of_continent, 'Total Deaths': deaths})
        deaths_by_continent = px.bar(graph_df, x="Total Deaths", y="Continent", color="Continent",
                                     text="Total Deaths", template="simple_white")

        vaccines = []
        for continent in list_of_continent:
            vaccines.append(df[(df['continent'] == continent) & (df['date'] == date)].sum()['total_vaccinations'])
        graph_df = pd.DataFrame({'Continent': list_of_continent, 'Total Vaccinations': vaccines})
        vaccines_by_continent = px.bar(graph_df, x="Total Vaccinations", y="Continent", color="Continent",
                                       text="Total Vaccinations", template="simple_white")
    else:
        cases = []
        for continent in list_of_continent:
            # () is necessary when using & inside df
            cases.append(df[(df['continent'] == continent) & (df['date'] == date)].sum()['new_cases'])
        graph_df = pd.DataFrame({'Continent': list_of_continent, 'Today Cases': cases})
        cases_by_continent = px.bar(graph_df, x="Today Cases", y="Continent", color="Continent",
                                    text="Today Cases", template="simple_white")

        deaths = []
        for continent in list_of_continent:
            deaths.append(df[(df['continent'] == continent) & (df['date'] == date)].sum()['new_deaths'])
        graph_df = pd.DataFrame({'Continent': list_of_continent, 'Today Deaths': deaths})
        deaths_by_continent = px.bar(graph_df, x="Today Deaths", y="Continent", color="Continent",
                                     text="Today Deaths", template="simple_white")

        vaccines = []
        for continent in list_of_continent:
            vaccines.append(df[(df['continent'] == continent) & (df['date'] == date)].sum()['new_vaccinations'])
        graph_df = pd.DataFrame({'Continent': list_of_continent, 'Today Vaccinations': vaccines})
        vaccines_by_continent = px.bar(graph_df, x="Today Vaccinations", y="Continent", color="Continent",
                                       text="Today Vaccinations", template="simple_white")

    graphs = [cases_by_continent, deaths_by_continent, vaccines_by_continent]
    text = ['Cases', 'Deaths', 'Vaccines']
    for i in range(3):
        graphs[i].update_traces(texttemplate='%{text:.4s}', textposition='auto',
                                hovertemplate='Continent: %{y} <br>'+text[i]+': %{x}  <extra></extra>', )
        graphs[i].update_layout(showlegend=False,
                                paper_bgcolor="#010310",
                                plot_bgcolor="#010310",
                                # xaxis, yaxis refers to the labels on the axes
                                xaxis=dict(tickfont={"size": 12, "color": "#F4E808"}),
                                yaxis=dict(tickfont={"size": 12, "color": "#F4E808"}),
                                margin=dict(l=0, r=0, t=0, b=0, ),
                                height=350,
                                )
        # Colour of axes -> the straight line only
        graphs[i].update_xaxes(title_font=dict(color="#F4E808"))
        graphs[i].update_yaxes(title_font=dict(color="#F4E808"))

    return cases_by_continent, deaths_by_continent, vaccines_by_continent


@app.callback(
    Output(component_id='total_cases_by_country', component_property='figure'),
    Output(component_id='total_deaths_by_country', component_property='figure'),
    Output(component_id='daily_cases_by_country', component_property='figure'),
    Output(component_id='daily_deaths_by_country', component_property='figure'),
    Input(component_id='country_name_dropdown', component_property='value'),
    Input(component_id='table_stats', component_property='active_cell'),
    State(component_id='table_stats', component_property='data'),
)
def line_chart_country(name_selected, active_cell, data):
    if active_cell:
        cell_data = data[active_cell['row']]
        country_data = df.loc[(df['iso_code'] == cell_data['iso_code']) & (df['date'] == cell_data['date'].
                                                                           split('T')[0])]
        country_name = country_data['location'].to_string().split('    ')[1]
    else:
        country_name = name_selected
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
    title_format = ['Total', 'Daily']
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
            # Uncomment bottom one and the title will be blocked
            # margin=dict(l=0, r=0, t=0, b=0),
            height=350,
        )
        # axes legend
        graph.update_xaxes(showline=True, linewidth=2, linecolor='#F4E808',
                           titlefont={"size": 13, "color": "#F4E808"}, ticks="inside", tickwidth=1,
                           tickcolor='#F4E808', ticklen=5)
        graph.update_yaxes(showline=True, linewidth=2, linecolor='#F4E808',
                           titlefont={"size": 13, "color": "#F4E808"}, ticks="inside", tickwidth=1,
                           tickcolor='#F4E808', ticklen=5)
        graph.update_traces(marker_color='#F4E808', marker_line=dict(width=2, color='#F4E808'))

    for index, graph in enumerate([total_deaths_by_country, daily_deaths_by_country]):
        graph.update_layout(
            showlegend=False,
            plot_bgcolor="#010310",
            paper_bgcolor='#010310',
            title=title_format[index] + ' Deaths in ' + country_name,
            titlefont={"size": 12, "color": "#F4E808"},
            xaxis=dict(
                tickfont={"size": 12, "color": "#F4E808"}
            ),
            yaxis=dict(
                tickfont={"size": 12, "color": "#F4E808"}
            ),
            # margin=dict(l=0, r=0, t=0, b=0),
            height=350,
        )
        graph.update_xaxes(showline=True, linewidth=2, linecolor='#F4E808',
                           titlefont={"size": 14, "color": "#F4E808"}, ticks="inside", tickwidth=1,
                           tickcolor='#F4E808', ticklen=5)
        graph.update_yaxes(showline=True, linewidth=2, linecolor='#F4E808',
                           titlefont={"size": 14, "color": "#F4E808"}, ticks="inside", tickwidth=1,
                           tickcolor='#F4E808', ticklen=5)
        graph.update_traces(marker_color='#F4E808', marker_line=dict(width=2, color='#F4E808'))

    return total_cases_by_country, total_deaths_by_country, daily_cases_by_country, daily_deaths_by_country


@app.callback(
    Output('news_location', 'children'),
    Input('date', 'date'),)
def update_output(date):
    return latest_news(df)


if __name__ == '__main__':
    app.run_server(debug=False,  port=int(os.environ.get("PORT", 5000)), host='0.0.0.0')
