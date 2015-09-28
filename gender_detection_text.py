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
		self.word_features = []
		


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

		counter = Counter()
		counter.update(self.words)
		counter.update(self.bigrams)
		counter.update(self.trigrams)
		self.word_features = [k for k, v in counter.most_common(2000)]
		return self.documents

	def document_features(self, document):

		document_words = document
		features = {}
		for word in self.word_features:
			
			if type(word) is str:
				features['contains({})'.format(word)] = (word in document_words)
			
			if type(word) is tuple and len(word) == 2:
				isPresent = False
				for index, document_word in enumerate(document_words[:-1], start=0):
					if word[0] == document_word and word[1] == document_words[index+1]:
						isPresent = True
				features['contains({}_{})'.format(word[0], word[1])] = isPresent
			
			if type(word) is tuple and len(word) == 3:
				isPresent = False
				for index, document_word in enumerate(document_words[:-2], start=0):
					if word[0] == document_word and word[1] == document_words[index+1] and word[2] == document_words[index+2]:
						isPresent = True
				features['contains({}_{}_{})'.format(word[0], word[1], word[2])] = isPresent
		return features

	def get_training_sets(self, documents):

		random.shuffle(documents)
		length = len(documents)
		test_length = int(round(len(documents)*0.2))
		devtest_length = int(round((len(documents) - test_length)*0.2))
		
		train_documents = documents[(test_length+devtest_length):]
		devtest_documents = documents[test_length:(test_length+devtest_length)]
		test_documents = documents[:test_length]

		return (train_documents, devtest_documents, test_documents)


	def start(self):
		
		db = pymongo.MongoClient().tweets
		tweets = db.tweets_text_3.find().limit(5000)
		documents = self.get_documents(tweets)
		
		(train_documents, devtest_documents, test_documents) = self.get_training_sets(documents)

		train_set = [(self.document_features(d), c) for (t,d,c) in train_documents]
		devtest_set = [(self.document_features(d), c) for (t,d,c) in devtest_documents]
		test_set = [(self.document_features(d), c) for (t,d,c) in test_documents]

		classifier = nltk.NaiveBayesClassifier.train(train_set)

		print "train_set: " + str(len(train_set))

		print "devtest_set: " + str(len(devtest_set))

		print "test_set: " + str(len(test_set))

		print "dev performance: " + str(nltk.classify.accuracy(classifier, devtest_set))

		print "test performance: " + str(nltk.classify.accuracy(classifier, test_set))

		classifier.show_most_informative_features(10)

		female_test = [f for (f, c) in test_set if c == 'Female']
		male_test = [f for (f, c) in test_set if c == 'Male']

		females = np.array(classifier.classify_many(female_test))
		males = np.array(classifier.classify_many(male_test))
		print "Confusion matrix:\n%d\t%d\n%d\t%d" % (
          (females == 'Female').sum(), (females == 'Male').sum(),
          (males == 'Male').sum(), (males == 'Female').sum())
		


		
if __name__ == '__main__':

	genderDetectionText = GenderDetectionText()
	genderDetectionText.start()


