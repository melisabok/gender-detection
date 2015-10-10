import re
import nltk
import pymongo
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import BernoulliNB, MultinomialNB
from sklearn.cross_validation import train_test_split
from sklearn import metrics





class GenderDetectionTextEx:

    def __init__(self):
        token_regex = re.compile(ur'\w+|#[a-zA-Z0-9_]+|:[OoDdSsPp3\)\(\|/\$\_]+|-\.-|-_-|\(8[\)]?|;\)|\u2665|[\uD800-\uDBFF][\uDC00-\uDFFF]|<3|\w+\'\w+|\w+', re.U|re.I)
        self.tokenizer = nltk.RegexpTokenizer(token_regex)


        self.count_vectorizer = CountVectorizer(ngram_range=(1,6), tokenizer = self.tokenizer.tokenize, stop_words=['user', '#tag', 'url', '#userconjustinbieber'], strip_accents='unicode')

    def most_informative_feature_for_binary_classification(self, classifier, n=10):
        class_labels = classifier.classes_
        feature_names = self.count_vectorizer.get_feature_names()
        topn_class1 = sorted(zip(classifier.coef_[0], feature_names))[:n]
        topn_class2 = sorted(zip(classifier.coef_[0], feature_names))[-n:]

        for coef, feat in topn_class1:
            print 'Female', coef, feat

        print

        for coef, feat in reversed(topn_class2):
            print 'Male', coef, feat

    def start(self):

        db = pymongo.MongoClient().tweets
        tweets = db.tweets_text_6.find()#.limit(500)
        data = []
        target = []
        categories = ['Female', 'Male']

        for tweet in tweets:
            data.append(tweet['text'])
            target.append(0 if tweet['gender'] == 'Female' else 1)

        data_train, data_test, y_train, y_test = train_test_split(data, target, test_size=0.33, random_state=42)

        X_train = self.count_vectorizer.fit_transform(data_train)

        feature_names = self.count_vectorizer.get_feature_names()

        #####Save to file
        df = pd.DataFrame(X_train.sum(axis=0).transpose(), index=feature_names, columns=['Frequency'])
        sorted_df = df.sort(['Frequency'], ascending=False)

        sorted_df.to_csv('features.csv', encoding='utf-8')
        #####

        nb = MultinomialNB(alpha=.01)
        nb.fit(X_train, y_train)


        X_test = self.count_vectorizer.transform(data_test)
        s = nb.score(X_test, y_test)
        print s
        
        pred = nb.predict(X_test)
        score = metrics.f1_score(y_test, pred)
        print("f1-score:   %0.3f" % score)

        self.most_informative_feature_for_binary_classification(nb, 100)





if __name__ == '__main__':

    genderDetectionText = GenderDetectionTextEx()
    genderDetectionText.start()