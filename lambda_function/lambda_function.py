import os
import sys
import json
import tweepy
import requests
import pandas as pd
from defipulse import DefiPulse
from coingecko import CoinGecko
from subprocess import call

# Data Preprocessing and Feature Engineering
consumer_key = os.environ.get('TWITTER_CONSUMER_KEY', 'ap-northeast-1')
consumer_secret = os.environ.get('TWITTER_CONSUMER_SECRET', 'ap-northeast-1')
access_token = os.environ.get('TWITTER_ACCESS_TOKEN', 'ap-northeast-1')
access_secret = os.environ.get('TWITTER_ACCESS_SECRET', 'ap-northeast-1')

def rates(token):
    obj = DefiPulse()
    rates = obj.getRates(token)
    names = ['Maker', 'Compound', 'Aave']

    tweet = "Current DeFi Rates for {} #DeFi #Ethereum\n".format(token)
    for name in names:
        tweet = tweet + "{0}, lend: {1}%, borrow: {2}%\n".format(name, rates['rates'][name]['lend']['rate'], rates['rates'][name]['borrow']['rate'])

    # initialize tweepy instance
    try:
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_secret)
        api = tweepy.API(auth)
        
        if tweet is not None:
            print(tweet)
            api.update_status(tweet)
        else:
            print('empty tweet')
    except Exception as e:
        print(e)

def prices():
    obj = DefiPulse()
    projects, names = obj.getProjects()
    # print(' '.join([project['name'] for project in projects]))

    tweet = "Current DeFi Top3 in TVL/USD #DeFi #Ethereum\n"
    for project in projects[:3]:
        tweet = tweet + "Name: {0}, tvlUSD: {1}, USD 1day relative {2}%\n".format(project['name'], project['value']['tvl']['USD']['value'], project['value']['tvl']['USD']['relative_1d'])
        # tweet = 'Name: {0}, tvlUSD: {1}, USD 1day relative {2}%, tvlETH: {3}, ETH 1day relative {4}%'.format(project['name'], project['value']['tvl']['USD']['value'], project['value']['tvl']['USD']['relative_1d'], project['value']['tvl']['ETH']['value'], project['value']['tvl']['ETH']['relative_1d'])

    # initialize tweepy instance
    try:
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_secret)
        api = tweepy.API(auth)
            
        if tweet is not None:
            print(tweet)
            api.update_status(tweet)
        else:
            print('empty tweet')
    except Exception as e:
        print(e)

def tvl(coin, vs_currency, days, period='1w'):
    obj = DefiPulse()
    tvls = obj.getTVL(period)
    obj1 = CoinGecko()
    df = obj1.getCoinVolume(coin, vs_currency, days)

    path1 = obj.drawTVLinUSD(tvls, df)
    path2 = obj.drawTVLinETH(tvls, df)

    # initialize tweepy instance
    try:
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_secret)
        api = tweepy.API(auth)

        if os.path.exists(path1):
            api.update_with_media(filename=path1, status='Eth trading volume and Total Value Locked in USD #DeFi #Ethereum')
        else:
            print('empty tweet')
        if os.path.exists(path2):
            api.update_with_media(filename=path2, status='Eth trading volume and Total Value Locked in ETH #DeFi #Ethereum')
        else:
            print('empty tweet')
    except Exception as e:
        print(e)

    call('rm -rf /tmp/*', shell=True)

def tokenprices(coins, vs_currency, days):
    obj = CoinGecko()
    df = pd.DataFrame()
    for coin in coins:
        y = obj.getCoinData(coin, vs_currency, days)
        df = pd.concat([df, y[['Close']]], axis=1, sort=True, join='outer')
    return df

def draws(period='1w'):
    tokens = ['Uniswap', 'Maker', 'Aave', 'Compound', 'Synthetix']

    obj = DefiPulse()
    path = obj.drawPercent(tokens, period)

    # initialize tweepy instance
    try:
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_secret)
        api = tweepy.API(auth)

        if os.path.exists(path):
            api.update_with_media(filename=path, status='Weekly Total Value Lock change in DefiPulse #DeFi #Ethereum')
        else:
            print('empty tweet')
    except Exception as e:
        print(e)

    call('rm -rf /tmp/*', shell=True)

def debts():
    obj = DefiPulse()
    path = obj.drawDebt()

    # initialize tweepy instance
    try:
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_secret)
        api = tweepy.API(auth)

        if os.path.exists(path):
            api.update_with_media(filename=path, status='Weekly Outstanding Debt USD in DefiPulse #DeFi #Ethereum')
        else:
            print('empty tweet')
    except Exception as e:
        print(e)

    call('rm -rf /tmp/*', shell=True)

def tweet_with_image(path, tweet):
    # initialize tweepy instance
    try:
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_secret)
        api = tweepy.API(auth)

        if os.path.exists(path):
            api.update_with_media(filename=path, status=tweet)
        else:
            print('empty tweet')
    except Exception as e:
        print(e)

    call('rm -rf /tmp/*', shell=True)

def lambda_handler(event, context):
    if event['operation'] == 'rates':
        token = event['token']
        rates(token)
    elif event['operation'] == 'prices':
        prices()
    elif event['operation'] == 'tvl':
        token = 'ethereum'
        tvl_usd(token, 'usd', '7')
    elif event['operation'] == 'draws':
        draws()
    elif event['operation'] == 'debts':
        debts()
    elif event['operation'] == 'govtokens':
        coins = ['bitcoin', 'ethereum', 'maker', 'uniswap', 'compound-governance-token', 'havven', 'aave', 'yearn-finance']
        tickers = ['BTC', 'ETH', 'MKR', 'UNI', 'COMP', 'SNX', 'AAVE', 'YFI']
        df = tokenprices(coins, 'usd', '7')
        df.columns = tickers
        df.dropna(how='any', inplace=True)
        df_t = df.copy()
        df_t /= df.loc[df.index[0]]

        obj = CoinGecko()
        path = obj.draw(df_t, 'Weekly_Governance_Token_Price_Change')
        tweet = 'Weekly Governance Token Price Change #DeFi #Ethereum'
        tweet_with_image(path, tweet)
    elif event['operation'] == 'corrtokens':
        coins = ['bitcoin', 'ethereum', 'maker', 'uniswap', 'compound-governance-token', 'havven', 'aave', 'yearn-finance']
        tickers = ['BTC', 'ETH', 'MKR', 'UNI', 'COMP', 'SNX', 'AAVE', 'YFI']
        df = tokenprices(coins, 'usd', '7')
        df.columns = tickers
        df.dropna(how='any', inplace=True)
        df_c = df.copy()
        df_corr = pd.DataFrame()
        for t in tickers:
            df_c['pct_' + t] = df_c.loc[:, t].pct_change(1).fillna(df_c[t].pct_change(1).median())
            df_c['rol_' + t] = df_c.loc[:, 'pct_' + t].rolling(7).sum().fillna(df_c['pct_' + t].rolling(7).sum().median())
            pd.concat([df_corr, df_c['rol_' + t]], axis=1, sort=True, join='outer')

        df_corr = df_c.loc[:, df_c.columns.str.contains('rol')]
        df_corr.columns = tickers

        obj = CoinGecko()
        path = obj.draw(df_corr[7:], 'Rolling_7-days_change_of_DeFi_and_Crypto')
        tweet = 'Rolling 7 days change of DeFi and Crypto(%) #DeFi #Ethereum'
        tweet_with_image(path, tweet)

# call lambda_handler
if __name__ == "__main__":
    lambda_handler(json.loads(sys.argv[1]), {})
