import os
import json
import datetime
import requests
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

headers = {'Content-Type': 'application/json'}
api_url_base = 'https://api.coingecko.com/api/v3/coins/'
vs_currency = 'usd'
days = '7'

class CoinGecko(object):

    def getCoinData(self, ids, vs, days):
        api_url = '{0}/{1}/ohlc?vs_currency={2}&days={3}'.format(api_url_base, ids, vs, days)
        res = requests.get(api_url, headers=headers)

        if res.status_code == 200:
            df = pd.read_json(res.content.decode('utf-8'))
            df.columns = ['timestamp', 'Open', 'High', 'Low', 'Close']
            df['timestamp'] = df['timestamp']/1000
            df['timestamp'] = df['timestamp'].astype(int)
            df['timestamp'] = df['timestamp'].map(datetime.datetime.utcfromtimestamp)
            df.index = df['timestamp']
            feature_name = ['Open', 'High', 'Low', 'Close']
            df = df[feature_name]
            df.interpolate(limit_direction='both', inplace=True)
            return df
        else:
            return None

    def draw(self, df, title):

        now = datetime.datetime.utcnow()
        path = '/tmp/' + title  + now.strftime('%Y%m%d_%H%M%S') + '.png'

        import seaborn as sns
        from matplotlib.dates import DateFormatter
        sns.set_style('whitegrid')
        sns.set_palette('Set2', 8, 1.0)
        sns.set_context(context='paper', font_scale=2, rc={"lines.linewidth":4})
        fig = plt.figure(figsize=(15, 7))
        ax = fig.add_subplot(1, 1, 1)
        ax.set_title(title)
        ax.xaxis.set_major_formatter(DateFormatter('%d'))
        ax = sns.lineplot(data=df, dashes=False)

        ax.set_xlabel("Date")
        ax.set_ylabel("Change")
        ax.xaxis.set_label_coords(0.5, -0.07)
        ax.yaxis.set_label_coords(-0.07, 0.5)
        ax.legend(bbox_to_anchor=(1, 1), loc='upper right')

        figure = ax.get_figure()
        figure.savefig(path)

        return path
