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

		token_regex = re.compile(ur'\w+|#[a-zA-Z0-9_]+|:[OoDdSsPp3\)\(\|/\$\_]+|-\.-|-_-|\(8[\)]?|;\)|\u2665|[\uD800-\uDBFF][\uDC00-\uDFFF]|<3|\w+\'\w+|\w+', re.U|re.I)
		self.emoji_regex = re.compile(ur'\u2665|[\uD800-\uDBFF][\uDC00-\uDFFF]', re.U|re.I) #TODO: change by twitter regex
		self.word_regex = re.compile(ur'user|#tag|url|^[0-9]*$', re.U|re.I)

		self.tokenizer = nltk.RegexpTokenizer(token_regex)

		self.documents = []
		self.words = []
		self.bigrams = []
		self.trigrams = []
		self.fourgrams = []
		self.fivegrams = []
		self.sixgrams = []
		self.word_features = []
		


	def get_documents(self, tweets):

		r = re.compile(ur'user|#tag|url|^[0-9]*$')
		no_words = lambda x: not r.match(x)

		for tweet in tweets:

			tokens = [self.word_decode(t.lower()) for t in self.tokenizer.tokenize(tweet['text'])]

			# Count words that are not user, #tag, url and take documents with more than 2 words 
			filtered_tokens = filter(no_words, tokens)
			if(len(filtered_tokens) > 2):

				self.documents.append((tweet, tokens, tweet['gender']))
				self.words.extend(filtered_tokens)
				self.bigrams.extend([gram for gram in list(nltk.bigrams(tokens)) if len(filter(no_words, list(gram))) == 2])
				self.trigrams.extend([gram for gram in list(nltk.trigrams(tokens)) if len(filter(no_words, list(gram))) == 3])
				self.fourgrams.extend([gram for gram in list(nltk.ngrams(tokens, 4)) if len(filter(no_words, list(gram))) == 4])
				self.fivegrams.extend([gram for gram in list(nltk.ngrams(tokens, 5)) if len(filter(no_words, list(gram))) == 5])
				self.sixgrams.extend([gram for gram in list(nltk.ngrams(tokens, 6)) if len(filter(no_words, list(gram))) == 6])

		counter = Counter()
		counter.update(self.words)
		counter.update(self.bigrams)
		counter.update(self.trigrams)
		counter.update(self.fourgrams)
		counter.update(self.fivegrams)
		counter.update(self.sixgrams)
		self.word_features = [k for k, v in counter.most_common(2000)]
		#self.word_features = [k for k, v in counter.iteritems() if v > 4]
		
		with open('features.txt', 'w') as f:
			for k, v in counter.most_common(8000):
				line = unicode(k) + "\t" + str(v)
				f.write(line.encode('utf-8') + '\n')
		return self.documents

	def document_features(self, document):

		document_words = document
		features = {}
		for word in self.word_features:
			
			if type(word) is str:
				features[u'contains({})'.format(word)] = (word in document_words)
			
			if type(word) is tuple and len(word) == 2:
				isPresent = False
				for index, document_word in enumerate(document_words[:-1], start=0):
					if word[0] == document_word and word[1] == document_words[index+1]:
						isPresent = True
				features[u'contains({}_{})'.format(word[0], word[1])] = isPresent
			
			if type(word) is tuple and len(word) == 3:
				isPresent = False
				for index, document_word in enumerate(document_words[:-2], start=0):
					if word[0] == document_word and word[1] == document_words[index+1] and word[2] == document_words[index+2]:
						isPresent = True
				features[u'contains({}_{}_{})'.format(word[0], word[1], word[2])] = isPresent

			if type(word) is tuple and len(word) == 4:
				isPresent = False
				for index, document_word in enumerate(document_words[:-3], start=0):
					if word[0] == document_word and word[1] == document_words[index+1] and word[2] == document_words[index+2] and word[3] == document_words[index+3]:
						isPresent = True
				features[u'contains({}_{}_{}_{})'.format(word[0], word[1], word[2], word[3])] = isPresent

			if type(word) is tuple and len(word) == 5:
				isPresent = False
				for index, document_word in enumerate(document_words[:-4], start=0):
					if word[0] == document_word and word[1] == document_words[index+1] and word[2] == document_words[index+2] and word[3] == document_words[index+3] and word[4] == document_words[index+4]:
						isPresent = True
				features[u'contains({}_{}_{}_{}_{})'.format(word[0], word[1], word[2], word[3], word[4])] = isPresent

			if type(word) is tuple and len(word) == 6:
				isPresent = False
				for index, document_word in enumerate(document_words[:-5], start=0):
					if word[0] == document_word and word[1] == document_words[index+1] and word[2] == document_words[index+2] and word[3] == document_words[index+3] and word[4] == document_words[index+4] and word[5] == document_words[index+5]:
						isPresent = True
				features[u'contains({}_{}_{}_{}_{}_{})'.format(word[0], word[1], word[2], word[3], word[4], word[5])] = isPresent

		return features

	def get_training_sets(self, documents):

		random.shuffle(documents)
		length = len(documents)
		test_length = int(round(len(documents)*0.15))
		devtest_length = int(round((len(documents) - test_length)*0.15))
		
		train_documents = documents[(test_length+devtest_length):]
		devtest_documents = documents[test_length:(test_length+devtest_length)]
		test_documents = documents[:test_length]

		return (train_documents, devtest_documents, test_documents)

	def word_decode(self, word):

		if self.emoji_regex.match(word):
			return word
		return unidecode.unidecode(word)


	def start(self):
		
		db = pymongo.MongoClient().tweets
		tweets = db.tweets_text_6.find()#.limit(500)
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

		classifier.show_most_informative_features(100)

		female_test = [f for (f, c) in test_set if c == 'Female']
		male_test = [f for (f, c) in test_set if c == 'Male']

		females = np.array(classifier.classify_many(female_test))
		males = np.array(classifier.classify_many(male_test))
		print "Confusion matrix:\n%d\t%d\n%d\t%d" % ((females == 'Female').sum(), (females == 'Male').sum(),(males == 'Male').sum(), (males == 'Female').sum())
		


		
if __name__ == '__main__':

	genderDetectionText = GenderDetectionText()
	genderDetectionText.start()


