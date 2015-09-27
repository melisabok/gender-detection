import pymongo
from gender_detection import *
from gender_by_name import *
from gender_by_description import *
from ttp import ttp
from multiprocessing import Pool

class TweetsProcessor:

    def __init__(self):
        self.gender_name = GenderName()
        self.gender_slots = GenderSlots()
        self.db = pymongo.MongoClient().twitts
        self.dbTweets = pymongo.MongoClient().tweets
        self.parser = ttp.Parser()
        self.uniques = set()
        

    def get_gender(self, tweet_with_gender):

        tweet_with_gender['screen_name_gender'] = self.gender_name.get_gender_screen_name(tweet_with_gender['screen_name'])
        description = tweet_with_gender['description']
        if description is not None:
            tweet_with_gender['description_gender'] = self.gender_slots.get_gender(description)
        return tweet_with_gender

    def parse_text(self, tweet_with_gender):

        id = tweet_with_gender['_id']
        text = tweet_with_gender['text']
        gender = tweet_with_gender['screen_name_gender']
        screen_name = tweet_with_gender['screen_name']
        result = self.parser.parse(text)
        for user in result.users:
            text = text.replace(user, "user")
        for tag in result.tags:
            text = text.replace(tag, "tag")
        for url in result.urls:
            text = text.replace(url, "[url]")
        
        tweet_text = {"_id": id, "text": text, "gender": gender, "screen_name": screen_name}

        self.dbTweets.tweets_text.save(tweet_text)

    def is_text_valid(self, text):

        first50 = text[:25]
        if first50 not in self.uniques:
            self.uniques.add(first50)

            return True   
        else:
            return False


    def process_text(self, tweet_with_gender):

        id = tweet_with_gender['_id']
        text = tweet_with_gender['text']
        gender = tweet_with_gender['screen_name_gender']
        screen_name = tweet_with_gender['screen_name']
        if(not text.startswith("RT")):
            
            result = self.parser.parse(text)
            for user in result.users:
                text = text.replace(user, "user")
            for tag in result.tags:
                text = text.replace(tag, "tag")
            for url in result.urls:
                text = text.replace(url, "[url]")       

            if self.is_text_valid(text):
                tweet_text = {"_id": id, "text": text, "gender": gender, "screen_name": screen_name}
                self.dbTweets.tweets_text_3.save(tweet_text)
            else:
                print "Filtered: " + text
        else:
            self.dbTweets.retweets.save(tweet_with_gender)



    def process_gender(self, tweet_without_gender):

        tweet_with_gender = self.get_gender(tweet_without_gender)

        screen_name_gender = tweet_with_gender['screen_name_gender']
        description_gender = tweet_with_gender['description_gender']
        
        if (screen_name_gender != 'UNKNOWN'):
            try:
                self.dbTweets.tweets_base_gender.save(tweet_with_gender)
                self.process_text(tweet_with_gender)
            except Exception as e:
                print "There was an error inserting the base tweet: " + str(e)
        else:
            try:
                self.dbTweets.tweets_base_unknown.save(tweet_with_gender)
            except Exception as e:
                print "There was an error inserting the unkonwn gender tweet: " + str(e)            



    def get_from_gnip(self, tweet):

        #for tweet in self.db.othertwits.find():
        id = tweet['_id']
        tweet_id = tweet['id']
        text = tweet['body']
        user_id = tweet['actor']['id']
        screen_name =  tweet['actor']['preferredUsername']
        name = tweet['actor']['displayName']
        description = tweet['actor']['summary']
        screen_name_gender = 'UNKNOWN'
        description_gender = 'UNKNOWN'

        tweet_without_gender = {'_id': id, 'id': tweet_id, 'user_id': user_id, 'text': text, 'screen_name': screen_name, 'name': name, 'description': description, \
        'screen_name_gender': screen_name_gender, 'description_gender': description_gender}
            
        self.process_gender(tweet_without_gender)

    def start(self):
        self.get_from_gnip()

def process(tweet):
    #tweetsProcessor = TweetsProcessor()
    tweetsProcessor.get_from_gnip(tweet)

tweetsProcessor = TweetsProcessor()

if __name__ == '__main__':
    p = Pool(4)
    
    
    db = pymongo.MongoClient().twitts
    tweets = db.othertwits.find()
    p.map(process, tweets)


           




