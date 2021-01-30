import requests
import pandas as pd
import dash_html_components as html
import os
from datetime import timedelta


def latest_covid_data(csv_file):
    """
    Get the latest covid data from website
    :param csv_file: link of html
    :return: required df, all country names, minimum to maximum date
    """
    df = pd.read_csv(csv_file)

    # Identify rows that have new/total cases/deaths less than 0, which is impossible
    df[(df['new_cases'] < 0) | (df['new_deaths'] < 0)] = 0

    # Get just the relevant columns
    df = df[["iso_code", "continent", "location", "date", "total_cases", "new_cases", "total_deaths", "new_deaths",
             "total_cases_per_million", "new_cases_per_million", "total_deaths_per_million", "new_deaths_per_million",
             "population", "total_vaccinations", "new_vaccinations", "hosp_patients"]]

    # Remove rows that are wrong value / empty
    df = df[df['date'].notna()]
    df = df[df['date'] != 0]
    df = df.round(2)

    # Replace all N.A. with 0 for easy manipulation of data
    df.fillna(0, inplace=True)
    # df.to_csv('covid-data.csv')

    # Convert column from string to date object
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')

    country_name_list = []
    for country_name in df['location'].unique():
        country_name_list.append({'label': country_name, 'value': country_name})

    # transform every unique date to a number
    numdate = [x for x in range(0, len(df['date'].unique()) + 30, 30)]

    return df, country_name_list, numdate


def generate_thumbnail(news_title, description, news_url, news_image_url):
    """
    Generate thumbnail for news article
    :param news_title: title of the news
    :param description: description of the news
    :param news_url: url of the news (href)
    :param news_image_url: url of image of news
    :return: thumbnail for news article
    """
    return html.Div([
        html.Div([
            html.Img(src=news_image_url,
                     style={"width": "25%", "vertical-align": "top"}),
            html.Div([
                html.P(html.U(html.B(news_title))),
                html.Span(description+" ", style={"font-size": "13"}),
                html.A("Read More", href=news_url, target='_blank'),
                ], style={"width": "70%", "display": "inline-block", "color": "white"})])
    ], className="newspaper_thumbnail")


def latest_news(df):
    """
    Get the latest covid news using newsAPI
    :param df: dataframe
    :return: list of latest news
    """
    all_news = set()
    url = ('http://newsapi.org/v2/everything?'
           'language=en&'
           'q=coronavirus&'
           'from={}&to={}&'
           'apiKey={}'.format(df['date'].max().to_pydatetime()-timedelta(days=3), df['date'].max(), os.getenv('API')))
    response = requests.get(url)

    for news in response.json()['articles']:
        list_of_words = ['vaccine', 'vaccination', 'coronavirus', 'covid', 'lockdown', 'virus']
        for common_word in list_of_words:
            if common_word in news['title'].lower():
                title = news['title']
                all_news.add(generate_thumbnail(title, news['description'], news['url'], news['urlToImage']))
                break
    return list(all_news)
