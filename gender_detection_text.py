import pymongo
import pandas as pd
from collections import Counter
import json, re, codecs
import nltk
from nltk.util import ngrams
import random
import unidecode
import numpy as np
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
import matplotlib.pyplot as plt
from sklearn.cross_validation import train_test_split
from sklearn import metrics


class GenderDetectionText:

	def __init__(self):

		token_regex = re.compile(r'\w+|#[a-zA-Z0-9_]+|:[OoDdSsPp3\)\(\|/\$\_]+|-\.-|-_-|\(8[\)]?|;\)|\w+\'\w+|\w+', re.U|re.I)
		self.tokenizer = nltk.RegexpTokenizer(token_regex)

		self.documents = []
		self.words = []
		self.bigrams = []
		self.trigrams = []
		


	def get_documents(self, tweets):

		no_words = lambda x: x not in ['user', '#tag', 'url']

		for tweet in tweets:

			tokens = [unidecode.unidecode(t.lower()) for t in self.tokenizer.tokenize(tweet['text'])]

			# Count words that are not user, #tag, url and take documents with more than 2 words 
			filtered_tokens = filter(no_words, tokens)
			if(len(filtered_tokens) > 2):

				self.documents.append((tweet, filtered_tokens, tweet['gender']))
				self.words.extend(filtered_tokens)
				self.bigrams.extend(list(nltk.bigrams(tokens)))
				self.trigrams.extend(list(nltk.trigrams(tokens)))

		return self.documents

		
if __name__ == '__main__':

	db = pymongo.MongoClient().tweets
	tweets = db.tweets_text_3.find().limit(10)
	genderDetectionText = GenderDetectionText()
	genderDetectionText.get_documents(tweets)


	print genderDetectionText.words

	print genderDetectionText.bigrams

	print genderDetectionText.trigrams

