import pymongo
import time
from TwitterSearch import *
from gender_detection import *

class TweetRetriever:
    def __init__(self):
        # it's about time to create a TwitterSearch object with our secret tokens
        self.ts = TwitterSearch(
                  consumer_key = 'L1QKedCUnrRlMAtSF0AZw',
                  consumer_secret = 'ULaNi4igQf2488fhgBNwJfN6kX9vuKkR80Y374Avm8',
                  access_token = '111056361-uSYLwKwPL6uVSPmzmQWjULLwPb1a2MfF0jAPdw3M',
                  access_token_secret = 'rALPPgqhil2M395CvZMZrMkA7OwFn8ICY1u6xLHuznqmT'
        )
        self.db = pymongo.MongoClient().tweets


    def retrieve_by_term(self, term):
        try:
            tso = TwitterSearchOrder() # create a TwitterSearchOrder object
            tso.set_keywords([term]) # let's define all words we would like to have a look for
            tso.set_language('es') # we want to see German tweets only
            tso.set_include_entities(False) # and don't give us all those entity information

            # this is where the fun actually starts :)
            for tweet in self.ts.search_tweets_iterable(tso):
                self.process_tweet(tweet)
        except TwitterSearchException as e: # take care of all those ugly errors if there are some,
            print(e)
            if(e.code == 429):
                print "Wait 15 minutes"
                time.sleep(900)


    def process_tweet(self, tweet):
        self.db.raw.insert(tweet)
        location = tweet['user']['location']
        m = re.search('.*(argentina|Argentina).*', location)
        if m is not None:
            self.db.raw_arg.insert(tweet)
            if not (tweet['retweeted'] or tweet['text'].startswith('RT @')):
                self.db.tweets_arg.insert(tweet)
                gender = get_gender_tweet(tweet)
                if((gender['screen_name_gender'] != 'UNKNOWN') or (gender['description_gender'] != 'UNKNOWN')):
                    self.db.tweets_arg_gender.insert(gender)

    def start(self, terms):
        for term in terms:
            print "Get tweets for: " + term
            self.retrieve_by_term(term)

TweetRetriever().start(['#JuegaBocaNoMeImportaMasNada', '#OrionMalaLeche', '#AutoFirmadoTorettoC5N', '#ElInvictoContinuaCabj', '#WeWillAlwaysBeHereForOurBoys1D', '#shoutalcorta', 'Carlos Bueno', 'Vangioni', 'Alperovich', 'Kasabian', 'Pharrell', 'CFK', 'CFKArgenina', 'Messi', 'Nisman'])
