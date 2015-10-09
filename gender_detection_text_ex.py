from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import BernoulliNB, MultinomialNB
from sklearn.datasets import fetch_20newsgroups
import re
import nltk
import pymongo
import pandas as pd




class GenderDetectionTextEx:

	def __init__(self):
		token_regex = re.compile(ur'\w+|#[a-zA-Z0-9_]+|:[OoDdSsPp3\)\(\|/\$\_]+|-\.-|-_-|\(8[\)]?|;\)|\u2665|[\uD800-\uDBFF][\uDC00-\uDFFF]|<3|\w+\'\w+|\w+', re.U|re.I)
		self.tokenizer = nltk.RegexpTokenizer(token_regex)


		self.count_vectorizer = CountVectorizer(ngram_range=(1,6), tokenizer = self.tokenizer.tokenize, stop_words=['user', '#tag', 'url', '#userconjustinbieber'], strip_accents='unicode')

		self.data = []
		self.target = []

		self.train_X = []
		self.train_Y = []

		self.test_X = []
		self.test_Y = []

	def start(self):

		db = pymongo.MongoClient().tweets
		tweets = db.tweets_text_6.find()#.limit(500)

		for tweet in tweets:
			self.data.append(tweet['text'])
			self.target.append(tweet['gender'])

		matrix = self.count_vectorizer.fit_transform(self.data)

		feature_names = self.count_vectorizer.get_feature_names()

		df = pd.DataFrame(matrix.sum(axis=0).transpose(), index=feature_names, columns=['Frequency'])
		sorted_df = df.sort(['Frequency'], ascending=False)

		
		sorted_df.to_csv('features.csv', encoding='utf-8')

if __name__ == '__main__':

	genderDetectionText = GenderDetectionTextEx()
	genderDetectionText.start()