import dash
from dash.dependencies import Input, Output, State
import time

from callbacks import *
from get_data import *

app = dash.Dash(__name__, title='Covid-19 Analytics',
                external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css', dbc.themes.BOOTSTRAP])


@app.callback(
    Output("loading-output", "children"), [Input("date", "date")]
)
def load_output(n):
    if n:
        time.sleep(3.5)
    return


app.layout = make_layout()
server = app.server


# TODO: add continent drill down countries
@app.callback(
    Output(component_id='table_stats', component_property='data'),
    Input(component_id='date', component_property='date'),
    Input(component_id='country_name_dropdown', component_property='value'),
    Input(component_id='graph', component_property='clickData'),
)
def table_data(date_selected, country_name_dropdown, clickdata):
    if clickdata and dash.callback_context.triggered[0]['prop_id'] != 'country_name_dropdown.value':
        iso_code = clickdata['points'][0]['location']
        data_contents = df[(df['date'] == date_selected) & (df['iso_code'] == iso_code)].to_dict('records')
        return data_contents
    if country_name_dropdown and country_name_dropdown != 'World':
        data_contents = df[(df['date'] == date_selected) & (df['location'] == country_name_dropdown)].to_dict('records')
        return data_contents
    data_contents = df[df['date'] == date_selected].to_dict('records')
    return data_contents


@app.callback(
    Output(component_id='total_cases', component_property='children'),
    Output(component_id='total_deaths', component_property='children'),
    Output(component_id='total_vaccines', component_property='children'),
    Input(component_id='date', component_property='date')
)
def stats(date_selected):
    """
    Selection of date shows the number of cases/cases/vaccines worldwide
    :param date_selected: Date selected from calendar
    :return: Number of cases/cases/vaccines worldwide
    """
    all_dates = (df['date'] <= date_selected) & (df['continent'] != 0)
    today_date = (df['date'] == date_selected) & (df['continent'] != 0)

    total_cases = main_stats("Total Cases", "new_cases", all_dates, today_date)
    total_deaths = main_stats("Total Deaths", "new_deaths", all_dates, today_date)
    total_vaccines = main_stats("Total Vaccines", "new_vaccinations", all_dates, today_date)
    return total_cases, total_deaths, total_vaccines


@app.callback(
    Output(component_id='graph', component_property='figure'),
    Input(component_id='today_btn', component_property='n_clicks'),
    Input(component_id='total_btn', component_property='n_clicks'),
    Input(component_id='date', component_property='date')
)
def world_graph(today_btn, total_btn, date_selected):
    """
    Updates the geo-scatter graph depending on date and whether the users want total/today stats
    :param today_btn: Button to select today's stats
    :param total_btn: Button to select total's stats
    :param date_selected: Date selected from calendar
    :return: Updated the geo-scatter graph
    """
    changed_id = dash.callback_context.triggered[0]['prop_id']
    if changed_id == 'total_btn.n_clicks':
        stats_chosen = 'total'
    else:
        stats_chosen = 'today'
    dff = df[(df['date'] == date_selected) & (df['continent'] != 0)]

    if stats_chosen == 'today':
        stats_chosen = 'new_cases'
    else:
        stats_chosen = 'total_cases'

    return geo_scatter_graph(dff, stats_chosen)


# TODO: reset button to drill back up
@app.callback(
    Output(component_id='total_cases_by_continent', component_property='figure'),
    Input(component_id='date', component_property='date'),
    Input(component_id='today_btn', component_property='n_clicks'),
    Input(component_id='total_btn', component_property='n_clicks'),
    Input(component_id='total_cases_by_continent', component_property='clickData')
)
def drill_down_cases(date, today_btn, total_btn, drill_down):
    """
    Drill down number of cases from continent to countries level
    :param date: Date selected from calendar
    :param today_btn: Button to select today's stats
    :param total_btn: Button to select total's stats
    :param drill_down: Click on the graph to result in drill down
    :return:
    """
    changed_id = dash.callback_context.triggered[0]['prop_id']
    if changed_id == 'total_btn.n_clicks':
        stats_chosen = 'total'
    else:
        stats_chosen = 'today'

    # When the graph is not selected -> when the web is being loaded, this fn will be called
    if not drill_down:
        list_of_continent = list(df['continent'].unique())
        list_of_continent.remove(0)
        cases_by_continent = display_continent(stats_chosen, list_of_continent, "cases", "Total Cases", date)
        return cases_by_continent

    if drill_down and drill_down['points'][0]['label'] in ['Asia', 'Europe', 'Africa', 'North America',
                                                           'South America', 'Oceania']:
        continent = drill_down['points'][0]['label']
        data = df[(df['date'] == date) & (df['continent'] == continent)]
        countries_list = data['location'].to_list()

        graph_df = pd.DataFrame({'Countries': countries_list,
                                 'Total Cases': data['total_cases'].to_list()})
        total_cases_by_country = drill_down_continent(graph_df, "Total Cases")
        return total_cases_by_country


# TODO: reset button to drill back up
@app.callback(
    Output(component_id='total_deaths_by_continent', component_property='figure'),
    Input(component_id='date', component_property='date'),
    Input(component_id='today_btn', component_property='n_clicks'),
    Input(component_id='total_btn', component_property='n_clicks'),
    Input('total_deaths_by_continent', 'clickData')
)
def drill_down_deaths(date, today_btn, total_btn, drill_down):
    changed_id = dash.callback_context.triggered[0]['prop_id']
    if changed_id == 'total_btn.n_clicks':
        stats_chosen = 'total'
    else:
        stats_chosen = 'today'

    # When the graph is not selected -> when the web is being loaded, this fn will be called
    if not drill_down:
        list_of_continent = list(df['continent'].unique())
        list_of_continent.remove(0)
        deaths_by_continent = display_continent(stats_chosen, list_of_continent, "deaths", "Total Deaths", date)
        return deaths_by_continent

    if drill_down and drill_down['points'][0]['label'] in ['Asia', 'Europe', 'Africa', 'North America',
                                                           'South America', 'Oceania']:
        continent = drill_down['points'][0]['label']
        data = df[(df['date'] == date) & (df['continent'] == continent)]
        countries_list = data['location'].to_list()

        graph_df = pd.DataFrame({'Countries': countries_list,
                                 'Total Deaths': data['total_deaths'].to_list()})
        total_deaths_by_country = drill_down_continent(graph_df, "Total Deaths")
        return total_deaths_by_country


# TODO: reset button to drill back up
@app.callback(
    Output(component_id='total_vaccines_by_continent', component_property='figure'),
    Input(component_id='date', component_property='date'),
    Input(component_id='today_btn', component_property='n_clicks'),
    Input(component_id='total_btn', component_property='n_clicks'),
    Input(component_id='total_vaccines_by_continent', component_property='clickData')
)
def drill_down_vaccines(date, today_btn, total_btn, drill_down):
    changed_id = dash.callback_context.triggered[0]['prop_id']
    if changed_id == 'total_btn.n_clicks':
        stats_chosen = 'total'
    else:
        stats_chosen = 'today'

    # When the graph is not selected -> when the web is being loaded, this fn will be called
    if not drill_down:
        list_of_continent = list(df['continent'].unique())
        list_of_continent.remove(0)
        vaccines_by_continent = display_continent(stats_chosen, list_of_continent, "vaccinations",
                                                  "Total Vaccinations", date)
        return vaccines_by_continent

    if drill_down and drill_down['points'][0]['label'] in ['Asia', 'Europe', 'Africa', 'North America',
                                                           'South America', 'Oceania']:
        continent = drill_down['points'][0]['label']
        data = df[(df['date'] == date) & (df['continent'] == continent)]
        countries_list = data['location'].to_list()

        graph_df = pd.DataFrame({'Countries': countries_list,
                                 'Total Vaccinations': data['total_vaccinations'].to_list()})
        total_vaccines_by_country = drill_down_continent(graph_df, "Total Vaccinations")
        return total_vaccines_by_country


def get_top_stats(data, date_selected, col_name):
    data = data[(data['date'] == date_selected) & (data['continent'] != 0)].sort_values(by=[col_name])[
        ['location', col_name]].tail(10)
    new_location_list = data['location'].to_list()[::-1]
    new_list = data[col_name].to_list()[::-1]

    code = [html.U(col_name.replace('_', ' ').title())]
    for index, (location, number) in enumerate(zip(new_location_list, new_list)):
        code.append(html.Div([html.Div(index+1, className="number_circle"), ' ', location, ': +', number]))
        code.append(html.Br())
    return code


@app.callback(
    Output(component_id='top_stats', component_property='children'),
    Input(component_id='date', component_property='date'),
)
def top_statistics(date_selected):
    new_cases_location = get_top_stats(df, date_selected, 'new_cases')

    new_deaths_location = get_top_stats(df, date_selected, 'new_deaths')

    new_vaccines_location = get_top_stats(df, date_selected, 'new_vaccinations')

    new_cases_location.extend(new_deaths_location)
    new_cases_location.extend(new_vaccines_location)

    return new_cases_location


@app.callback(
    Output(component_id='total_cases_by_country', component_property='figure'),
    Output(component_id='daily_cases_by_country', component_property='figure'),
    Output(component_id='country_name', component_property='children'),
    Input(component_id='country_name_dropdown', component_property='value'),
    Input(component_id='table_stats', component_property='active_cell'),
    Input(component_id='graph', component_property='clickData'),
    State(component_id='table_stats', component_property='data'),
)
def country_cases_stats(name_selected, active_cell, clickdata, data):
    if active_cell:
        cell_data = data[active_cell['row']]
        country_data = df.loc[(df['iso_code'] == cell_data['iso_code']) & (df['date'] == cell_data['date'].
                                                                           split('T')[0])]
        country_name = country_data['location'].to_string().split('    ')[1]
    # Determining which Input has fired using dash.callback_context.triggered
    elif clickdata and dash.callback_context.triggered[0]['prop_id'] != 'country_name_dropdown.value':
        iso_code = clickdata['points'][0]['location']
        country_name = df[df['iso_code'] == iso_code]['location'].values[0]
    else:
        country_name = name_selected

    country_name_df = df[df['location'] == country_name]

    total_cases_by_country = country_bar_graph(country_name_df, "total_cases", "Total Cases")
    daily_cases_by_country = country_bar_graph(country_name_df, "new_cases", "New Cases")

    total_cases_by_country, daily_cases_by_country = full_country_graphs(total_cases_by_country, daily_cases_by_country)

    return total_cases_by_country, daily_cases_by_country, country_name


@app.callback(
    Output(component_id='total_deaths_by_country', component_property='figure'),
    Output(component_id='daily_deaths_by_country', component_property='figure'),
    Input(component_id='country_name_dropdown', component_property='value'),
    Input(component_id='table_stats', component_property='active_cell'),
    Input(component_id='graph', component_property='clickData'),
    State(component_id='table_stats', component_property='data'),
)
def country_deaths_stats(name_selected, active_cell, clickdata, data):
    if active_cell:
        cell_data = data[active_cell['row']]
        country_data = df.loc[(df['iso_code'] == cell_data['iso_code']) & (df['date'] == cell_data['date'].
                                                                           split('T')[0])]
        country_name = country_data['location'].to_string().split('    ')[1]
    # Determining which Input has fired using dash.callback_context.triggered
    elif clickdata and dash.callback_context.triggered[0]['prop_id'] != 'country_name_dropdown.value':
        iso_code = clickdata['points'][0]['location']
        country_name = df[df['iso_code'] == iso_code]['location'].values[0]
    else:
        country_name = name_selected

    country_name_df = df[df['location'] == country_name]

    total_deaths_by_country = country_bar_graph(country_name_df, "total_deaths", "Total Deaths")
    daily_deaths_by_country = country_bar_graph(country_name_df, "new_deaths", "New Deaths")

    total_deaths_by_country, daily_deaths_by_country = full_country_graphs(total_deaths_by_country,
                                                                           daily_deaths_by_country)

    return total_deaths_by_country, daily_deaths_by_country


@app.callback(
    Output('news_location', 'children'),
    Input('date', 'date'),)
def update_output(date):
    return latest_news(df)


if __name__ == '__main__':
    # app.run_server(debug=True)
    app.run_server(debug=False,  port=int(os.environ.get("PORT", 5000)), host='0.0.0.0')
