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



    def show_most_informative_features(self, clf, vectorizer, n=20):
        feature_names = vectorizer.get_feature_names()
        coefs_with_fns = sorted(zip(clf.coef_[0], feature_names))
        top = zip(coefs_with_fns[:n], coefs_with_fns[:-(n + 1):-1])
        for (coef_1, fn_1), (coef_2, fn_2) in top:
            print "\t%.4f\t%-15s\t\t%.4f\t%-15s" % (coef_1, fn_1, coef_2, fn_2)

    def execute(self, tweets, categories):

        data = []
        target = []

        for tweet in tweets:
            data.append(tweet['text'])
            target.append(categories[tweet['gender']])

        data_train, data_test, y_train, y_test = train_test_split(data, target, test_size=0.33, random_state=42)

        vectorizer = TfidfVectorizer(ngram_range=(1,6), tokenizer = self.tokenizer.tokenize, stop_words=['user', '#tag', 'url', '#userconjustinbieber'], strip_accents='unicode', min_df=15)
        print len(data_train)
        X_train = vectorizer.fit_transform(data_train)

        feature_names = vectorizer.get_feature_names()

        #####Save to file
        df = pd.DataFrame(X_train.sum(axis=0).transpose(), index=feature_names, columns=['Frequency'])
        sorted_df = df.sort(['Frequency'], ascending=False)

        sorted_df.to_csv('features.csv', encoding='utf-8')
        #####

        nb = MultinomialNB(alpha=.01)
        nb.fit(X_train, y_train)


        X_test = vectorizer.transform(data_test)
        s = nb.score(X_test, y_test)
        print s
        
        pred = nb.predict(X_test)
        score = metrics.f1_score(y_test, pred)
        print("f1-score:   %0.3f" % score)

        self.show_most_informative_features(nb, vectorizer)
 

    def start(self):

        db = pymongo.MongoClient().tweets
        tweets = list(db.tweets_text_6.find())#.limit(500)

        categories = {
            'Female': 0,
            'Male': 1
        }

        categories2 = {
            'Female': 1,
            'Male': 0
        }

        self.execute(tweets, categories)
        self.execute(tweets, categories2)
        


if __name__ == '__main__':

    genderDetectionText = GenderDetectionTextEx()
    genderDetectionText.start()