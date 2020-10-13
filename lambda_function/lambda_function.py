import os
import sys
import json
import tweepy
import requests
from defipulse import DefiPulse
from subprocess import call

# Data Preprocessing and Feature Engineering
consumer_key = os.environ.get('TWITTER_CONSUMER_KEY', 'ap-northeast-1')
consumer_secret = os.environ.get('TWITTER_CONSUMER_SECRET', 'ap-northeast-1')
access_token = os.environ.get('TWITTER_ACCESS_TOKEN', 'ap-northeast-1')
access_secret = os.environ.get('TWITTER_ACCESS_SECRET', 'ap-northeast-1')

def rates(token):
    obj = DefiPulse()
    rates = obj.getRates(token)
    tokens = ['Maker', 'dYdX', 'Compound', 'Fulcrum']

    tweet = "Current DeFi Rates\n"
    for token in tokens:
        tweet = tweet + "{0}, lend: {1}%, borrow: {2}%\n".format(token, rates['rates'][token]['lend']['rate'], rates['rates'][token]['borrow']['rate'])

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

    tweet = "Current DeFi Top3\n"
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

def draws(period='1w'):
    obj = DefiPulse()
    # projects, names = obj.getProjects()
    # tokens = names[0:10] # only top 10 tokens

    path = obj.drawPercent(period)
    # initialize tweepy instance
    try:
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_secret)
        api = tweepy.API(auth)

        if os.path.exists(path):
            api.update_with_media(filename=path, status='Weekly Total Value Lock change')
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
    elif event['operation'] == 'draws':
        draws()

# call lambda_handler
if __name__ == "__main__":
    lambda_handler(json.loads(sys.argv[1]), {})

