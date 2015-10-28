import re
import nltk
import pymongo
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import BernoulliNB, MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.cross_validation import train_test_split
from sklearn import metrics
from sklearn.pipeline import Pipeline





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

    def execute(self, classifier, tweets, categories):

        data = []
        target = []

        for tweet in tweets:
            data.append(tweet['text'])
            target.append(categories[tweet['gender']])

        data_train, data_test, y_train, y_test = train_test_split(data, target, test_size=0.33, random_state=42)

        
        vectorizer = TfidfVectorizer(ngram_range=(1,6), tokenizer = self.tokenizer.tokenize, stop_words=['user', '#tag', 'url', '#userconjustinbieber'], strip_accents='unicode', min_df=10)
        
        pipeline = Pipeline([('feature_extraction', vectorizer), ('classifier', classifier)])


        #feature_names = vectorizer.get_feature_names()

        #####Save to file
        #df = pd.DataFrame(X_train.sum(axis=0).transpose(), index=feature_names, columns=['Frequency'])
        #sorted_df = df.sort(['Frequency'], ascending=False)

        #sorted_df.to_csv('features.csv', encoding='utf-8')
        #####

        pipeline.fit(data_train, y_train)


        s = pipeline.score(data_test, y_test)
        print s
        
        pred = pipeline.predict(data_test)
        score = metrics.f1_score(y_test, pred)
        print("f1-score:   %0.3f" % score)

        #self.show_most_informative_features(classifier, vectorizer)
 

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

        for i in range(0, 10, 1):
            alpha = i / 10.0
            nb = MultinomialNB(alpha=alpha)
            print "MultinomialNB Male, alpha: " + str(alpha)
            self.execute(nb, tweets, categories)
            print "MultinomialNB Female, alpha: " + str(alpha)
            self.execute(nb, tweets, categories2)

        for i in range(0, 10, 1):
            alpha = i / 10.0
            nb = BernoulliNB(alpha=alpha)
            print "BernoulliNB Male, alpha: " + str(alpha)
            self.execute(nb, tweets, categories)
            print "BernoulliNB Female, alpha: " + str(alpha)
            self.execute(nb, tweets, categories2)

        for i in range(0, 10, 1):
            alpha = i / 10.0
            svc = LinearSVC(C=alpha, loss='l2', penalty='l2', dual=False, tol=1e-3)
            print "LinearSVC Male, C: " + str(alpha)
            self.execute(nb, tweets, categories)
            print "LinearSVC Female, C: " + str(alpha)
            self.execute(nb, tweets, categories2)

if __name__ == '__main__':

    genderDetectionText = GenderDetectionTextEx()
    genderDetectionText.start()