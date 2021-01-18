import pandas as pd
import logging
from apscheduler.schedulers.blocking import BlockingScheduler


def get_latest_csv():
    df = pd.read_csv(r'https://covid.ourworldindata.org/data/owid-covid-data.csv')
    df.to_csv("owid-covid-data.csv")


scheduler = BlockingScheduler()
scheduler.add_job(get_latest_csv, 'interval', minutes=1)
scheduler.start()
