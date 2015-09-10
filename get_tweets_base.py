import pymongo
from gender_detection import *
from gender_by_name import *
from gender_by_description import *
from ttp import ttp

gender_name = GenderName()
gender_slots = GenderSlots()
db = pymongo.MongoClient().twitts
dbTweets = pymongo.MongoClient().tweets
dbTweets = pymongo.MongoClient().tweets
p = ttp.Parser()

for tweet in db.othertwits.find().limit(100):
    id = tweet['_id']
    tweet_id = tweet['id']
    text = tweet['body']
    user_id = tweet['actor']['id']
    screen_name =  tweet['actor']['preferredUsername']
    name = tweet['actor']['displayName']
    description = tweet['actor']['summary']

    screen_name_gender = gender_name.get_gender_screen_name(screen_name)
    description_gender = 'UNKNOWN'

    if description is not None:
        description_gender = gender_slots.get_gender(description)

    tweet_with_gender = {'_id': id, 'id': tweet_id, 'user_id': user_id, 'text': text, 'screen_name': screen_name, 'name': name, 'description': description, \
    'screen_name_gender': screen_name_gender, 'description_gender': description_gender}
    
    if((screen_name_gender != 'UNKNOWN') or (description_gender != 'UNKNOWN')):
        try:
            #print "insert tweet!"
            dbTweets.tweets_base_gender.save(tweet_with_gender)

            if(not text.startswith("RT @")):
                if(screen_name_gender == 'Female'):
                    dbTweets.tweets_female.save(tweet_with_gender)
                if(screen_name_gender == 'Male'):
                    dbTweets.tweets_male.save(tweet_with_gender)

                result = p.parse(text)
                print result.users
                print result.tags
                print result.urls
            else:
                dbTweets.retweets.save(tweet_with_gender)
        except Exception as e:
            print "There was an error inserting the tweet: " + str(e)

