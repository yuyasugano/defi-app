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

    def getSpecificDefiData(self, tokens, period):
        df = pd.DataFrame()
        for token in tokens:
            df = pd.concat([df, self.getData(period, token)], axis=1, sort=True, join='outer')
        return df

    def drawPercent(self, tokens, period):
        print(tokens)
        df = self.getSpecificDefiData(tokens, period)
        df = df.loc[:, df.columns.str.contains('tvlUSD')]
        df.dropna(how='any', inplace=True)
        df /= df.loc[df.index[0]]
        df.tail()

        now = datetime.datetime.utcnow()
        path = '/tmp/' + 'weeklyTVLUSD_' + now.strftime('%Y%m%d_%H%M%S') + '.png'

        import seaborn as sns
        from matplotlib.dates import DateFormatter
        sns.set_style('whitegrid')
        sns.set_palette('Set2', 8, 1.0)
        sns.set_context(context='paper', font_scale=2, rc={"lines.linewidth":4})
        fig = plt.figure(figsize=(15, 7))
        ax = fig.add_subplot(1, 1, 1)
        ax.set_title('Weekly Total Value Lock change in DefiPulse')
        ax.xaxis.set_major_formatter(DateFormatter('%d'))
        ax = sns.lineplot(data=df, dashes=False)
        figure = ax.get_figure()
        figure.savefig(path)

        return path

    def getRates(self, token):
        api_url = '{0}/GetRates?token={1}&amount=10000'.format(api_url_base, token)
        res = requests.get(api_url, headers=headers)

        if res.status_code == 200:
            rates = json.loads(res.content.decode('utf-8'))
            return rates
        else:
            return None

    def getLendingOutstanding(self, token):
        api_url = '{0}/GetLendingProjects?token={1}'.format(api_url_base, token)
        res = requests.get(api_url, headers=headers)

        if res.status_code == 200:
            projects = json.loads(res.content.decode('utf-8'))
            names = [project['name'] for project in projects]
            return projects, names
        else:
            return None

    def drawDebt(self):
        projects, names = self.getLendingOutstanding(API_KEY)
        debtUSD = [int(round(p['outstanding']['total']['valueUSD'])) for p in projects[:-1]]
        s = pd.Series(debtUSD, index=names[:-1])

        now = datetime.datetime.utcnow()
        path = '/tmp/' + 'weeklyDebtUSD_' + now.strftime('%Y%m%d_%H%M%S') + '.png'

        import seaborn as sns
        sns.set_style('whitegrid')
        sns.set_palette('Set2', 8, 1.0)
        sns.set_context(context='paper', font_scale=2, rc={"lines.linewidth": 4})
        fig = plt.figure(figsize=(15, 7))
        ax = fig.add_subplot(1, 1, 1)
        ax.set_title('Defi Debt Outstanding in USD', pad=15)
        ax = sns.barplot(x=s.index, y=s, data=pd.DataFrame(s))
        ax.set_xlabel('Defi Protocol')
        ax.set_ylabel('Debt Outstanding USD')
        plt.yticks([], [])
        ax.xaxis.set_label_coords(0.5, -0.1)
        ax.yaxis.set_label_coords(-0.01, 0.5)

        for p in ax.patches:
            _x = p.get_x() + p.get_width() / 2
            _y = p.get_y() + p.get_height()
            value = int(round(p.get_height()))
            ax.text(_x, _y+10000000, value, ha="center")

        figure = ax.get_figure()
        figure.savefig(path)
        return path

