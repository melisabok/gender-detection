import pymongo
import csv
from gender_by_name import *
from gender_by_description import *


def get_gender_tweets(tweets):
	gender_name = GenderName()
	gender_slots = GenderSlots()

	for tweet in tweets:
		text = tweet['text']
		screen_name =  tweet['user']['screen_name']
		name = tweet['user']['name']
		description = tweet['user']['description']
		screen_name_gender = gender_name.get_gender_screen_name(screen_name)
		description_gender = gender_slots.get_gender(description)
		text_gender = gender_slots.get_gender(text)

		tweet_with_gender = {'text': text, 'screen_name': screen_name, 'name': name, 'description': description, \
		'screen_name_gender': screen_name_gender, 'description_gender': description_gender, 'text_gender': text_gender}

		db.tweets_with_gender.insert(tweet_with_gender)


	print db.tweets_arg.count()

def get_gender_tweet(tweet):
	gender_name = GenderName()
	gender_slots = GenderSlots()

	tweet_id = tweet['id']
	text = tweet['text']
	user_id = tweet['user']['id']
	screen_name =  tweet['user']['screen_name']
	name = tweet['user']['name']
	description = tweet['user']['description']
	screen_name_gender = gender_name.get_gender_screen_name(screen_name)
	description_gender = gender_slots.get_gender(description)

	tweet_with_gender = {'id': tweet_id, 'user_id': user_id, 'text': text, 'screen_name': screen_name, 'name': name, 'description': description, \
	'screen_name_gender': screen_name_gender, 'description_gender': description_gender}

	return tweet_with_gender
	#db.tweets_with_gender.insert(tweet_with_gender)


#db = pymongo.MongoClient().tweets
#get_gender_tweets(db.tweets_arg.find())