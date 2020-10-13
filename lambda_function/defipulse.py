import os
import json
import datetime
import requests
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

headers = {'Content-Type': 'application/json'}
api_url_base = 'https://public.defipulse.com/api'
API_KEY = os.environ.get('API_KEY', 'ap-northeast-1')

class DefiPulse(object):

    def getProjects(self):
        api_url = '{0}/GetProjects?api-key={1}'.format(api_url_base, API_KEY)
        res = requests.get(api_url, headers=headers)

        if res.status_code == 200:
            projects = json.loads(res.content.decode('utf-8'))
            names = [project['name'] for project in projects]
            return projects, names
        else:
            return None

    def getData(self, p, t):
        api_url = '{0}/GetHistory?api-key={1}&period={2}&project={3}'.format(api_url_base, API_KEY, p, t)
        res = requests.get(api_url, headers=headers)

        if res.status_code == 200:
            df = pd.read_json(res.content.decode('utf-8'))
            df.index = df['timestamp']
            feature_name = ['tvlUSD', 'tvlETH']
            df = df[feature_name]
            df.interpolate(limit_direction='both', inplace=True)
            df.columns = [s + '_' + t for s in df.columns]
            return df
        else:
            return None

    def getDefiData(self, period):
        projects, names = self.getProjects()
        df = pd.DataFrame()
        for name in names:
            df = pd.concat([df, self.getData(period, name)], axis=1, sort=True, join='outer')
        return df

    def drawPercent(self, period):
        df = self.getDefiData(period)
        df = df.loc[:, df.columns.str.contains('tvlUSD')]
        pct = df.iloc[:, 0:10]/df.iloc[0, 0:10]

        now = datetime.datetime.utcnow()
        path = '/tmp/' + 'tvlchange_' + now.strftime('%Y%m%d_%H%M%S') + '.png'

        fig = plt.figure(figsize=(15, 7))
        ax1 = fig.add_subplot(1, 1, 1)
        df.plot(ax=ax1)
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Percent')
        ax1.set_title('Weekly Total Value Lock change')
        plt.savefig(path)
        plt.close('all')

        return path

    def getRates(self, token):
        api_url = '{0}/GetRates?token={1}&amount=10000'.format(api_url_base, token)
        res = requests.get(api_url, headers=headers)

        if res.status_code == 200:
            rates = json.loads(res.content.decode('utf-8'))
            return rates
        else:
            return None
