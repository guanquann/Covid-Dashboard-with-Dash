from layout import *
import plotly.graph_objects as go
import plotly.express as px


def main_stats(header, column_name, all_dates, today_date):
    """
    Show the total/increase in cases/deaths/vaccinations
    :param header: Title of div
    :param column_name: Column name in df
    :param all_dates: Minimum date to today's date
    :param today_date: Today's date
    :return: Div with total/increase in cases/deaths/vaccinations
    """
    return header, html.Br(), html.Div([df[column_name][all_dates].sum(),
                                        html.Div(["+", df[column_name][today_date].sum()],
                                                 className="new_stats_thumbnail_inner_div")],
                                       className="daily_stats_thumbnail_inner_div")


def geo_scatter_graph(data, stats_chosen):
    """
    Display geo-scatter graph
    :param data: Dataframe
    :param stats_chosen: Total/Today cases
    :return: Geo-scatter graph
    """
    fig = go.Figure(data=go.Scattergeo(
        locations=data["iso_code"],
        text=data[stats_chosen],
        mode='markers',
        marker=dict(
            color="#EC7575",
            size=data[stats_chosen],
            sizemode='area',
            sizeref=1. * max(data[stats_chosen]) / (50. ** 2),
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
        title_text='Click on the bubble to see detailed statistics of the country at the bottom!',
        title_font_size=11,
        title_font_color=colors['text'],
        # width=800,
        # autosize=True,
        height=430,
        # Do this to minimise space between graph and outer div
        margin=go.layout.Margin(l=0, r=0, b=90, t=40,),
        geo=dict(
            showframe=False,
            projection_type='equirectangular',
        ),
        showlegend=False,
        clickmode='event+select',
    )
    return fig


def country_bar_graph(country_name, col_name, graph_label):
    """
    Show bar graph of a particular country
    :param country_name: Name of the country
    :param col_name: Column name of dataframe
    :param graph_label: Label of y-axis of graph
    :return: Bar graph (one country)
    """
    return px.bar(country_name, x="date", y=col_name, color="location",
                  hover_name="location", template="simple_white",
                  labels={"location": "Country", "date": "Date", col_name: graph_label})


def full_country_graphs(total_by_country, daily_by_country, type_stats, country):
    """
    Display bar graph with the stats of a particular country. Continuation of country_bar_graph()
    Improve design and add on-click event to the graph
    :param total_by_country: Total number by a particular country over time
    :param daily_by_country: Daily number by a particular country
    :param type_stats: Cases/Deaths/Vaccinations
    :param country: Name of the country
    :return: Bar graphs (one country)
    """
    for index, graph in enumerate([total_by_country, daily_by_country]):
        graph.update_layout(
            showlegend=False,
            plot_bgcolor="#010310",
            paper_bgcolor='#010310',
            xaxis=dict(
                tickfont={"size": 12, "color": "#F4E808"}
            ),
            yaxis=dict(
                tickfont={"size": 12, "color": "#F4E808"}
            ),
            # Uncomment bottom one and the title will be blocked
            # margin=dict(l=0, r=0, t=0, b=0),
            height=350,
            clickmode='event+select',
        )
        # axes legend
        graph.update_xaxes(showline=True, linewidth=2, linecolor='#F4E808',
                           titlefont={"size": 13, "color": "#F4E808"}, ticks="inside", tickwidth=1,
                           tickcolor='#F4E808', ticklen=5)
        graph.update_yaxes(showline=True, linewidth=2, linecolor='#F4E808',
                           titlefont={"size": 13, "color": "#F4E808"}, ticks="inside", tickwidth=1,
                           tickcolor='#F4E808', ticklen=5)
        graph.update_traces(marker_color='#F4E808', marker_line=dict(width=2, color='#F4E808'),
                            textposition='auto',
                            hovertemplate='<b>' + country + '</b><br><br>' + type_stats + ': %{y:0f} <br>' + 'Date' +
                                          ': %{x}  <extra></extra>',
                            )

    return total_by_country, daily_by_country


def display_continent(stats_chosen, list_of_continent, column_name, x_axis, date):
    """
    Show bar graphs of continent
    :param stats_chosen: Cases/Deaths/Vaccinations
    :param list_of_continent: List of all the continents
    :param column_name: Column name in Dataframe
    :param x_axis: Label of x-axis in graph
    :param date: Date chosen
    :return: Bar graphs of continent
    """
    type_list = list()
    if stats_chosen == 'total':
        col_name = 'total_{}'.format(column_name)
        for continent in list_of_continent:
            data = df[(df['continent'] == continent) & (df['date'] == date)][col_name].sum()
            type_list.append(data)

        graph_df = pd.DataFrame({'Continent': list_of_continent, x_axis: type_list})
        cases_by_continent = px.bar(graph_df, x=x_axis, y="Continent", color="Continent", text=x_axis,
                                    template="simple_white")

    else:
        col_name = 'new_{}'.format(column_name)
        for continent in list_of_continent:
            data = df[(df['continent'] == continent) & (df['date'] == date)][col_name].sum()
            type_list.append(data)

        graph_df = pd.DataFrame({'Continent': list_of_continent, x_axis: type_list})
        cases_by_continent = px.bar(graph_df, x=x_axis, y="Continent", color="Continent",
                                    text=x_axis, template="simple_white")

    cases_by_continent.update_traces(textposition='auto',
                                     hovertemplate='Continent: %{y} <br>' + 'Cases' + ': %{x:0f}  <extra></extra>', )
    cases_by_continent.update_layout(showlegend=False,
                                     paper_bgcolor="#010310",
                                     plot_bgcolor="#010310",
                                     # xaxis, yaxis refers to the labels on the axes
                                     xaxis=dict(tickfont={"size": 12, "color": "#F4E808"}),
                                     yaxis=dict(tickfont={"size": 12, "color": "#F4E808"}),
                                     margin=dict(l=0, r=0, t=0, b=0),
                                     height=350,
                                     )
    # cases_by_continent.add_annotation(text="DrillDown available",
    #                                   font={"color": "#F4E808", "size": 9},
    #                                   xref="paper", yref="paper",
    #                                   x=0.95, y=0.0, showarrow=False)
    # Colour of axes -> the straight line only
    cases_by_continent.update_xaxes(title_font=dict(color="#F4E808"))
    cases_by_continent.update_yaxes(title_font=dict(color="#F4E808"))

    return cases_by_continent


def drill_down_continent(graph_df, y_axis):
    """
    Display this graph when users drill down the continent graph
    :param graph_df: Dataframe
    :param y_axis: Columns name from df
    :return: Bar graph with all countries in a continent
    """
    total_by_country = px.bar(graph_df, x="Countries", y=y_axis, color="Countries",
                              template="simple_white",)

    total_by_country.update_traces(hovertemplate='Country: %{x} <br>' + 'Cases' + ': %{y:0f}  <extra></extra>')
    total_by_country.update_layout(showlegend=False,
                                   paper_bgcolor="#010310",
                                   plot_bgcolor="#010310",
                                   # xaxis, yaxis refers to the labels on the axes
                                   xaxis=dict(tickfont={"size": 12, "color": "#F4E808"}),
                                   yaxis=dict(tickfont={"size": 12, "color": "#F4E808"}),
                                   margin=dict(l=0, r=0, t=0, b=0, ),
                                   height=350,
                                   )
    # Colour of axes -> the straight line only
    total_by_country.update_xaxes(title_font=dict(color="#F4E808"))
    total_by_country.update_yaxes(title_font=dict(color="#F4E808"))

    return total_by_country
