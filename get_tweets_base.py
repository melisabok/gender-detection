import pymongo
from gender_detection import *
from gender_by_name import *
from gender_by_description import *
from ttp import ttp

class TweetsProcessor:

    def __init__(self):
        self.gender_name = GenderName()
        self.gender_slots = GenderSlots()
        self.db = pymongo.MongoClient().twitts
        self.dbTweets = pymongo.MongoClient().tweets
        self.parser = ttp.Parser()

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
        result = self.parser.parse(text)
        for user in result.users:
            text = text.replace(user, "user")
        for tag in result.tags:
            text = text.replace(tag, "tag")
        for url in result.urls:
            text = text.replace(url, "[url]")
        
        tweet_text = {"_id": id, "text": text, "gender": gender}

        self.dbTweets.tweets_text.save(tweet_text)


    def process(self, tweet_with_gender):

        tweet_with_gender = self.get_gender(tweet_with_gender)
        screen_name_gender = tweet_with_gender['screen_name_gender']
        description_gender = tweet_with_gender['description_gender']
        text = tweet_with_gender['text']

        if((screen_name_gender != 'UNKNOWN') or (description_gender != 'UNKNOWN')):
            try:
                
                self.dbTweets.tweets_base_gender.save(tweet_with_gender)

                if(not text.startswith("RT @")):
                    if(screen_name_gender == 'Female'):
                        self.dbTweets.tweets_female.save(tweet_with_gender)
                        self.parse_text(tweet_with_gender)
                    if(screen_name_gender == 'Male'):
                        self.dbTweets.tweets_male.save(tweet_with_gender)
                        self.parse_text(tweet_with_gender)

                    
                else:
                    self.dbTweets.retweets.save(tweet_with_gender)
            except Exception as e:
                print "There was an error inserting the tweet: " + str(e)


    def get_from_gnip(self):

        for tweet in self.db.othertwits.find():
            id = tweet['_id']
            tweet_id = tweet['id']
            text = tweet['body']
            user_id = tweet['actor']['id']
            screen_name =  tweet['actor']['preferredUsername']
            name = tweet['actor']['displayName']
            description = tweet['actor']['summary']
            screen_name_gender = 'UNKNOWN'
            description_gender = 'UNKNOWN'

            tweet_with_gender = {'_id': id, 'id': tweet_id, 'user_id': user_id, 'text': text, 'screen_name': screen_name, 'name': name, 'description': description, \
            'screen_name_gender': screen_name_gender, 'description_gender': description_gender}
            
            self.process(tweet_with_gender)

    def start(self):
        self.get_from_gnip()

if __name__ == '__main__':
    TweetsProcessor().start()       




