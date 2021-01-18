import dash
from dash.dependencies import Input, Output, State
import time

from callbacks import *
from get_data import *

app = dash.Dash(__name__, title='Covid-19 Analytics',
                external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css', dbc.themes.BOOTSTRAP],
                meta_tags=[])
# {"name": "viewport", "content": "width=device-width, initial-scale=1"}


@app.callback(
    Output("loading-output", "children"), [Input("date", "date")]
)
def load_output(n):
    if n:
        time.sleep(2.5)
    return


app.layout = make_layout()
server = app.server


@app.callback(
    Output(component_id='table_stats', component_property='data'),
    Input(component_id='date', component_property='date'),
)
def table_data(date_selected):
    data_contents = df[df['date'] == date_selected].to_dict('records')
    return data_contents


@app.callback(
    Output(component_id='total_cases', component_property='children'),
    Output(component_id='total_deaths', component_property='children'),
    Output(component_id='total_vaccines', component_property='children'),
    Input(component_id='date', component_property='date')
)
def stats(date_selected):
    all_dates = df['date'] <= date_selected
    today_date = df['date'] == date_selected

    total_cases = main_stats("Total Cases", "new_cases", all_dates, today_date)
    total_deaths = main_stats("Total Deaths", "new_deaths", all_dates, today_date)
    total_vaccines = main_stats("Total Vaccines", "new_vaccinations", all_dates, today_date)
    return total_cases, total_deaths, total_vaccines


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

    return geo_scatter_graph(dff, stats_chosen)


@app.callback(
    Output(component_id='total_cases_by_continent', component_property='figure'),
    Input(component_id='date', component_property='date'),
    Input(component_id='type_of_stats', component_property='value'),
    Input('total_cases_by_continent', 'clickData')
)
def drill_down_cases(date, stats_chosen, drill_down):
    if drill_down and drill_down['points'][0]['label'] in ['Asia', 'Europe', 'Africa', 'North America',
                                                           'South America', 'Oceania']:
        continent = drill_down['points'][0]['label']
        data = df[(df['date'] == date) & (df['continent'] == continent)]
        countries_list = data['location'].to_list()

        graph_df = pd.DataFrame({'Countries': countries_list,
                                 'Total Cases': data['total_cases'].to_list()})
        total_cases_by_country = drill_down_continent(graph_df, "Total Cases")
        return total_cases_by_country

    list_of_continent = list(df['continent'].unique())
    cases_by_continent = display_continent(stats_chosen, list_of_continent, "total_cases", "Total Cases", date)
    return cases_by_continent


@app.callback(
    Output(component_id='total_deaths_by_continent', component_property='figure'),
    Input(component_id='date', component_property='date'),
    Input(component_id='type_of_stats', component_property='value'),
    Input('total_deaths_by_continent', 'clickData')
)
def drill_down_deaths(date, stats_chosen, drill_down):
    if drill_down and drill_down['points'][0]['label'] in ['Asia', 'Europe', 'Africa', 'North America',
                                                           'South America', 'Oceania']:
        continent = drill_down['points'][0]['label']
        data = df[(df['date'] == date) & (df['continent'] == continent)]
        countries_list = data['location'].to_list()

        graph_df = pd.DataFrame({'Countries': countries_list,
                                 'Total Deaths': data['total_deaths'].to_list()})
        total_deaths_by_country = drill_down_continent(graph_df, "Total Deaths")
        return total_deaths_by_country

    list_of_continent = list(df['continent'].unique())
    deaths_by_continent = display_continent(stats_chosen, list_of_continent, "total_deaths", "Total Deaths", date)
    return deaths_by_continent


@app.callback(
    Output(component_id='total_vaccines_by_continent', component_property='figure'),
    Input(component_id='date', component_property='date'),
    Input(component_id='type_of_stats', component_property='value'),
    Input('total_vaccines_by_continent', 'clickData')
)
def drill_down_vaccines(date, stats_chosen, drill_down):
    if drill_down and drill_down['points'][0]['label'] in ['Asia', 'Europe', 'Africa', 'North America',
                                                           'South America', 'Oceania']:
        continent = drill_down['points'][0]['label']
        data = df[(df['date'] == date) & (df['continent'] == continent)]
        countries_list = data['location'].to_list()

        graph_df = pd.DataFrame({'Countries': countries_list,
                                 'Total Vaccinations': data['total_vaccinations'].to_list()})
        total_vaccines_by_country = drill_down_continent(graph_df, "Total Vaccinations")
        return total_vaccines_by_country

    list_of_continent = list(df['continent'].unique())
    vaccines_by_continent = display_continent(stats_chosen, list_of_continent, "total_vaccinations",
                                              "Total Vaccinations", date)
    return vaccines_by_continent


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

    country_name_df = df[df['location'] == country_name]

    total_cases_by_country = country_bar_graph(country_name_df, "total_cases", "Total Cases")
    total_deaths_by_country = country_bar_graph(country_name_df, "total_deaths", "Total Deaths")
    daily_cases_by_country = country_bar_graph(country_name_df, "new_cases", "New Cases")
    daily_deaths_by_country = country_bar_graph(country_name_df, "new_deaths", "New Deaths")

    total_cases_by_country, daily_cases_by_country, total_deaths_by_country, daily_deaths_by_country = \
        full_country_graphs(country_name, total_cases_by_country, daily_cases_by_country,
                            total_deaths_by_country, daily_deaths_by_country)

    return total_cases_by_country, total_deaths_by_country, daily_cases_by_country, daily_deaths_by_country


@app.callback(
    Output('news_location', 'children'),
    Input('date', 'date'),)
def update_output(date):
    return latest_news(df)


if __name__ == '__main__':
    # app.run_server(debug=True)
    app.run_server(debug=False,  port=int(os.environ.get("PORT", 5000)), host='0.0.0.0')
