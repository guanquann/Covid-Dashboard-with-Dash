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

list_of_continents = ['Asia', 'Europe', 'Africa', 'North America', 'South America', 'Oceania']


@app.callback(
    Output(component_id='today_btn', component_property='className'),
    Output(component_id='total_btn', component_property='className'),
    Input(component_id='today_btn', component_property='n_clicks'),
    Input(component_id='total_btn', component_property='n_clicks'),
)
def select_btn_style(today_btn, total_btn):
    if dash.callback_context.triggered[0]['prop_id'] == 'today_btn.n_clicks':
        return "today_btn_selected", "total_btn_not_selected"
    else:
        return "today_btn_not_selected", "total_btn_selected"


@app.callback(
    Output(component_id='table_stats', component_property='data'),
    Input(component_id='date', component_property='date'),
    Input(component_id='country_name_dropdown', component_property='value'),
    Input(component_id='world_stats', component_property='n_clicks'),
    Input(component_id='graph', component_property='clickData'),
    Input(component_id='total_cases_by_continent', component_property='clickData'),
    Input(component_id='total_deaths_by_continent', component_property='clickData'),
    Input(component_id='total_vaccines_by_continent', component_property='clickData'),
)
def table_data(date_selected, country_name_dropdown, world_btn, click_graph, click_cases, click_deaths, click_vaccines):
    # If users click on the World Btn at the top of the web
    # Reset the DataTable - all data displayed
    if world_btn and dash.callback_context.triggered[0]['prop_id'] == 'world_stats.n_clicks':
        data_contents = df[(df['date'] == date_selected) & (df['location'] != "International")].to_dict('records')
        return data_contents

    # If users click on the geo-scatter graph
    # DataTable shows country selected
    if click_graph and dash.callback_context.triggered[0]['prop_id'] == 'graph.clickData':
        iso_code = click_graph['points'][0]['location']
        data_contents = df[(df['date'] == date_selected) & (df['iso_code'] == iso_code)].to_dict('records')
        return data_contents

    # If users click on the cases tab with continents
    # DataTable shows continent selected
    if click_cases and click_cases['points'][0]['label'] in list_of_continents and \
            dash.callback_context.triggered[0]['prop_id'] == 'total_cases_by_continent.clickData':
        continent_selected = click_cases['points'][0]['label']
        data_contents = df[(df['date'] == date_selected) & (df['continent'] == continent_selected)].to_dict('records')
        return data_contents

    # If users click on the cases tab with countries of a continent
    # DataTable shows country selected
    if click_cases and click_cases['points'][0]['label'] not in list_of_continents and \
            dash.callback_context.triggered[0]['prop_id'] == 'total_cases_by_continent.clickData':
        country_name = click_cases['points'][0]['label']
        data_contents = df[(df['date'] == date_selected) & (df['location'] == country_name)].to_dict('records')
        return data_contents

    # If users click on the deaths tab with continents
    # DataTable shows continent selected
    if click_deaths and click_deaths['points'][0]['label'] in list_of_continents and \
            dash.callback_context.triggered[0]['prop_id'] == 'total_deaths_by_continent.clickData':
        continent_selected = click_deaths['points'][0]['label']
        data_contents = df[(df['date'] == date_selected) & (df['continent'] == continent_selected)].to_dict('records')
        return data_contents

    # If users click on the deaths tab with countries of a continent
    # DataTable shows country selected
    if click_deaths and click_deaths['points'][0]['label'] not in list_of_continents and \
            dash.callback_context.triggered[0]['prop_id'] == 'total_deaths_by_continent.clickData':
        country_name = click_deaths['points'][0]['label']
        data_contents = df[(df['date'] == date_selected) & (df['location'] == country_name)].to_dict('records')
        return data_contents

    # If users click on the vaccines tab with continents
    # DataTable shows continent selected
    if click_vaccines and click_vaccines['points'][0]['label'] in list_of_continents and \
            dash.callback_context.triggered[0]['prop_id'] == 'total_vaccines_by_continent.clickData':
        continent_selected = click_vaccines['points'][0]['label']
        data_contents = df[(df['date'] == date_selected) & (df['continent'] == continent_selected)].to_dict('records')
        return data_contents

    # If users click on the vaccines tab with countries of a continent
    # DataTable shows country selected
    if click_vaccines and click_vaccines['points'][0]['label'] not in list_of_continents and \
            dash.callback_context.triggered[0]['prop_id'] == 'total_vaccines_by_continent.clickData':
        country_name = click_vaccines['points'][0]['label']
        data_contents = df[(df['date'] == date_selected) & (df['location'] == country_name)].to_dict('records')
        return data_contents

    if country_name_dropdown and country_name_dropdown != 'World':
        data_contents = df[(df['date'] == date_selected) & (df['location'] == country_name_dropdown)
                           & (df['location'] != "International")].to_dict('records')
        return data_contents

    data_contents = df[(df['date'] == date_selected) & (df['location'] != "International")].to_dict('records')
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
    Input(component_id='date', component_property='date'),
    Input(component_id='card-tabs', component_property='active_tab'),
)
def world_graph(today_btn, total_btn, date_selected, active_tab):
    """
    Updates the geo-scatter graph depending on date and whether the users want total/today stats
    :param today_btn: Button to select today's stats
    :param total_btn: Button to select total's stats
    :param date_selected: Date selected from calendar
    :param active_tab: Tab selected when seeing comparison between continents
    :return: Updated the geo-scatter graph
    """
    changed_id = dash.callback_context.triggered[0]['prop_id']
    if changed_id == 'total_btn.n_clicks':
        stats_chosen = 'total'
    else:
        stats_chosen = 'today'
    dff = df[(df['date'] == date_selected) & (df['continent'] != 0)]

    if stats_chosen == 'today':
        stats_chosen = 'new_' + active_tab
    else:
        stats_chosen = 'total_' + active_tab

    return geo_scatter_graph(dff, stats_chosen)


@app.callback(
    Output(component_id='total_cases_by_continent', component_property='figure'),
    Output(component_id='tab_cases_instruction', component_property='children'),
    Output(component_id='current_selected_cases', component_property='children'),
    Output(component_id='toggle_cases', component_property='children'),

    Input(component_id='date', component_property='date'),
    Input(component_id='today_btn', component_property='n_clicks'),
    Input(component_id='total_btn', component_property='n_clicks'),
    Input(component_id='toggle_cases', component_property='n_clicks'),
    Input(component_id='total_cases_by_continent', component_property='clickData')
)
def drill_down_cases(date, today_btn, total_btn, toggle_cases, drill_down):
    """
    Drill down number of cases from continent to countries level
    :param date: Date selected from calendar
    :param today_btn: Button to select today's stats
    :param total_btn: Button to select total's stats
    :param toggle_cases: Click on country to drill back to continent level
    :param drill_down: Click on the graph to result in drill down
    :return:
    """
    changed_id = dash.callback_context.triggered[0]['prop_id']
    if changed_id == 'total_btn.n_clicks':
        stats_chosen = 'total'
    else:
        stats_chosen = 'today'

    # When the graph is not selected -> when the web is being loaded, this fn will be called
    if not drill_down or toggle_cases % 2 == 1:
        list_of_continent = list(df['continent'].unique())
        list_of_continent.remove(0)
        cases_by_continent = display_continent(stats_chosen, list_of_continent, "cases", "Total Cases", date)

        return cases_by_continent, "Click on any continent before clicking Confirm", 'Currently Selected: None', 'Confirm'

    if drill_down and drill_down['points'][0]['label'] in ['Asia', 'Europe', 'Africa', 'North America',
                                                           'South America', 'Oceania']:
        continent = drill_down['points'][0]['label']

    else:
        continent = df[df['location'] == drill_down['points'][0]['label']]['continent'].iloc[0]

    data = df[(df['date'] == date) & (df['continent'] == continent)]
    countries_list = data['location'].to_list()

    if stats_chosen == 'total':
        graph_df = pd.DataFrame({'Countries': countries_list, 'Total Cases': data['total_cases'].to_list()})
        cases_by_country = drill_down_continent(graph_df, "Total Cases")

    else:
        graph_df = pd.DataFrame({'Countries': countries_list, 'Today Cases': data['new_cases'].to_list()})
        cases_by_country = drill_down_continent(graph_df, "Today Cases")

    return cases_by_country, 'Click on Back to reset', 'Continent Selected: {}'.format(continent), 'Back'


@app.callback(
    Output(component_id='total_deaths_by_continent', component_property='figure'),
    Output(component_id='tab_deaths_instruction', component_property='children'),
    Output(component_id='current_selected_deaths', component_property='children'),
    Output(component_id='toggle_deaths', component_property='children'),
    Input(component_id='date', component_property='date'),
    Input(component_id='today_btn', component_property='n_clicks'),
    Input(component_id='total_btn', component_property='n_clicks'),
    Input(component_id='toggle_deaths', component_property='n_clicks'),
    Input('total_deaths_by_continent', 'clickData')
)
def drill_down_deaths(date, today_btn, total_btn, toggle_deaths, drill_down):
    changed_id = dash.callback_context.triggered[0]['prop_id']
    if changed_id == 'total_btn.n_clicks':
        stats_chosen = 'total'
    else:
        stats_chosen = 'today'

    # When the graph is not selected -> when the web is being loaded, this fn will be called
    if not drill_down or toggle_deaths % 2 == 1:
        list_of_continent = list(df['continent'].unique())
        list_of_continent.remove(0)
        deaths_by_continent = display_continent(stats_chosen, list_of_continent, "deaths", "Total Deaths", date)
        return deaths_by_continent, "Click on any continent before clicking Confirm", 'Currently Selected: None', 'Confirm'

    if drill_down and drill_down['points'][0]['label'] in ['Asia', 'Europe', 'Africa', 'North America',
                                                           'South America', 'Oceania']:
        continent = drill_down['points'][0]['label']
    else:
        continent = df[df['location'] == drill_down['points'][0]['label']]['continent'].iloc[0]

    data = df[(df['date'] == date) & (df['continent'] == continent)]
    countries_list = data['location'].to_list()
    if stats_chosen == 'total':
        graph_df = pd.DataFrame({'Countries': countries_list, 'Total Deaths': data['total_deaths'].to_list()})
        total_deaths_by_country = drill_down_continent(graph_df, "Total Deaths")
        return total_deaths_by_country
    else:
        graph_df = pd.DataFrame({'Countries': countries_list, 'Today Deaths': data['new_deaths'].to_list()})
        today_deaths_by_country = drill_down_continent(graph_df, "Today Deaths")
        return today_deaths_by_country, 'Click on Back to reset', 'Continent Selected: {}'.format(continent), 'Back'


@app.callback(
    Output(component_id='total_vaccines_by_continent', component_property='figure'),
    Output(component_id='tab_vaccines_instruction', component_property='children'),
    Output(component_id='current_selected_vaccines', component_property='children'),
    Output(component_id='toggle_vaccines', component_property='children'),
    Input(component_id='date', component_property='date'),
    Input(component_id='today_btn', component_property='n_clicks'),
    Input(component_id='total_btn', component_property='n_clicks'),
    Input(component_id='toggle_vaccines', component_property='n_clicks'),
    Input(component_id='total_vaccines_by_continent', component_property='clickData')
)
def drill_down_vaccines(date, today_btn, total_btn, toggle_vaccines, drill_down):
    changed_id = dash.callback_context.triggered[0]['prop_id']
    if changed_id == 'total_btn.n_clicks':
        stats_chosen = 'total'
    else:
        stats_chosen = 'today'

    # When the graph is not selected -> when the web is being loaded, this fn will be called
    if not drill_down or toggle_vaccines % 2 == 1:
        list_of_continent = list(df['continent'].unique())
        list_of_continent.remove(0)
        vaccines_by_continent = display_continent(stats_chosen, list_of_continent, "vaccinations",
                                                  "Total Vaccinations", date)
        return vaccines_by_continent, "Click on any continent before clicking Confirm", 'Currently Selected: None', 'Confirm'

    if drill_down and drill_down['points'][0]['label'] in ['Asia', 'Europe', 'Africa', 'North America',
                                                           'South America', 'Oceania']:
        continent = drill_down['points'][0]['label']

    else:
        continent = df[df['location'] == drill_down['points'][0]['label']]['continent'].iloc[0]

    data = df[(df['date'] == date) & (df['continent'] == continent)]
    countries_list = data['location'].to_list()
    if stats_chosen == 'total':
        graph_df = pd.DataFrame({'Countries': countries_list, 'Total Vaccinations': data['total_vaccinations'].to_list()})
        total_vaccines_by_country = drill_down_continent(graph_df, "Total Vaccinations")
        return total_vaccines_by_country
    else:
        graph_df = pd.DataFrame({'Countries': countries_list, 'Today Vaccinations': data['new_vaccinations'].to_list()})
        today_vaccines_by_country = drill_down_continent(graph_df, "Today Vaccinations")
        return today_vaccines_by_country, 'Click on Back to reset', 'Continent Selected: {}'.format(continent), 'Back'


def get_top_stats(data, date_selected, col_name, display_type):
    data = data[(data['date'] == date_selected) & (data['continent'] != 0)].sort_values(by=[col_name])[
        ['location', col_name]].tail(10)
    new_location_list = data['location'].to_list()[::-1]
    new_list = data[col_name].to_list()[::-1]

    code = [html.U("Top " + col_name.replace('_', ' ').title())]
    for index, (location, number) in enumerate(zip(new_location_list, new_list)):
        if display_type == 'New':
            code.append(html.Div([html.Div(index+1, className="number_circle"), ' ', location, ': +', number]))
        else:
            code.append(html.Div([html.Div(index + 1, className="number_circle"), ' ', location, ': ', number]))
        code.append(html.Br())
    return code


@app.callback(
    Output(component_id='top_stats', component_property='children'),
    Input(component_id='date', component_property='date'),
)
def top_statistics(date_selected):
    new_cases_location = get_top_stats(df, date_selected, 'new_cases', 'New')
    total_cases_location = get_top_stats(df, date_selected, 'total_cases', 'Total')

    new_deaths_location = get_top_stats(df, date_selected, 'new_deaths', 'New')
    total_deaths_location = get_top_stats(df, date_selected, 'total_deaths', 'Total')

    new_vaccines_location = get_top_stats(df, date_selected, 'new_vaccinations', 'New')
    total_vaccines_location = get_top_stats(df, date_selected, 'total_vaccinations', 'Total')

    new_cases_location.extend(total_cases_location + new_deaths_location + total_deaths_location +
                              new_vaccines_location + total_vaccines_location)

    return new_cases_location


@app.callback(
    Output(component_id='total_cases_by_country', component_property='figure'),
    Output(component_id='daily_cases_by_country', component_property='figure'),
    Output(component_id='country_name', component_property='children'),
    Input(component_id='world_stats', component_property='n_clicks'),
    Input(component_id='country_name_dropdown', component_property='value'),
    Input(component_id='table_stats', component_property='active_cell'),
    Input(component_id='graph', component_property='clickData'),
    Input(component_id='total_cases_by_continent', component_property='clickData'),
    Input(component_id='total_deaths_by_continent', component_property='clickData'),
    Input(component_id='total_vaccines_by_continent', component_property='clickData'),
    State(component_id='table_stats', component_property='data'),
)
def country_cases_stats(world_btn, name_selected, active_cell, graph_click, cases_click, deaths_click,
                        vaccines_click, data):
    if dash.callback_context.triggered[0]['prop_id'] == 'world_stats.n_clicks':
        country_name = 'World'

    elif active_cell:
        cell_data = data[active_cell['row']]
        country_data = df.loc[(df['iso_code'] == cell_data['iso_code']) & (df['date'] == cell_data['date'].
                                                                           split('T')[0])]
        country_name = country_data['location'].to_string().split('    ')[1]

    elif graph_click and dash.callback_context.triggered[0]['prop_id'] == 'graph.clickData':
        iso_code = graph_click['points'][0]['location']
        country_name = df[df['iso_code'] == iso_code]['location'].values[0]

    elif cases_click and cases_click['points'][0]['label'] not in list_of_continents and \
            dash.callback_context.triggered[0]['prop_id'] == 'total_cases_by_continent.clickData':
        country_name = cases_click['points'][0]['label']

    elif deaths_click and deaths_click['points'][0]['label'] not in list_of_continents and \
            dash.callback_context.triggered[0]['prop_id'] == 'total_deaths_by_continent.clickData':
        country_name = deaths_click['points'][0]['label']

    # TODO: click on graph btn, show world graph
    # TODO: click on continent, show contientn graph

    elif vaccines_click and vaccines_click['points'][0]['label'] not in list_of_continents and \
            dash.callback_context.triggered[0]['prop_id'] == 'total_vaccines_by_continent.clickData':
        country_name = vaccines_click['points'][0]['label']

    else:
        country_name = name_selected

    country_name_df = df[df['location'] == country_name]

    total_cases_by_country = country_bar_graph(country_name_df, "total_cases", "Total Cases")
    daily_cases_by_country = country_bar_graph(country_name_df, "new_cases", "New Cases")

    total_cases_by_country, daily_cases_by_country = full_country_graphs(total_cases_by_country,
                                                                         daily_cases_by_country, "Cases", country_name)

    return total_cases_by_country, daily_cases_by_country, country_name


@app.callback(
    Output(component_id='total_deaths_by_country', component_property='figure'),
    Output(component_id='daily_deaths_by_country', component_property='figure'),
    Input(component_id='country_name_dropdown', component_property='value'),
    Input(component_id='table_stats', component_property='active_cell'),
    Input(component_id='graph', component_property='clickData'),
    Input(component_id='total_cases_by_continent', component_property='clickData'),
    State(component_id='table_stats', component_property='data'),
)
def country_deaths_stats(name_selected, active_cell, clickdata, continent_click, data):
    if active_cell:
        cell_data = data[active_cell['row']]
        country_data = df.loc[(df['iso_code'] == cell_data['iso_code']) & (df['date'] == cell_data['date'].
                                                                           split('T')[0])]
        country_name = country_data['location'].to_string().split('    ')[1]

    # Determining which Input has fired using dash.callback_context.triggered
    elif clickdata and dash.callback_context.triggered[0]['prop_id'] != 'country_name_dropdown.value':
        iso_code = clickdata['points'][0]['location']
        country_name = df[df['iso_code'] == iso_code]['location'].values[0]

    elif continent_click and continent_click['points'][0]['label'] not in ['Asia', 'Europe', 'Africa', 'North America',
                                                                           'South America', 'Oceania']:
        country_name = continent_click['points'][0]['label']

    else:
        country_name = name_selected

    country_name_df = df[df['location'] == country_name]

    total_deaths_by_country = country_bar_graph(country_name_df, "total_deaths", "Total Deaths")
    daily_deaths_by_country = country_bar_graph(country_name_df, "new_deaths", "New Deaths")

    total_deaths_by_country, daily_deaths_by_country = full_country_graphs(total_deaths_by_country,
                                                                           daily_deaths_by_country,
                                                                           "Deaths", country_name)

    return total_deaths_by_country, daily_deaths_by_country


@app.callback(
    Output('news_location', 'children'),
    Input('date', 'date'),)
def update_output(date):
    return latest_news(df)


if __name__ == '__main__':
    app.run_server(debug=True)
    # app.run_server(debug=False,  port=int(os.environ.get("PORT", 5000)), host='0.0.0.0')
