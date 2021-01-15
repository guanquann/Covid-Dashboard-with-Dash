import dash_bootstrap_components as dbc
import dash_core_components as dcc

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

