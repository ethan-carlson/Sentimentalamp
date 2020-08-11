import re
import tweepy
import time
from tweepy import OAuthHandler
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import twitter_samples, stopwords
from nltk.tag import pos_tag
from nltk.tokenize import word_tokenize
from nltk import FreqDist, classify, NaiveBayesClassifier

import string
import random
import serial as sl  

ser = sl.Serial('/dev/cu.SLAB_USBtoUART',9600)   

class TwitterClient(object):
    ''' 
    Generic Twitter Class for sentiment analysis. 
    '''

    def __init__(self):
        ''' 
        Class constructor or initialization method. 
        '''
        # keys and tokens from the Twitter Dev Console
        consumer_key = ''
        consumer_secret = ''
        access_token = ''
        access_token_secret = ''

        # attempt authentication
        try:
            # create OAuthHandler object
            self.auth = OAuthHandler(consumer_key, consumer_secret)
            # set access token and secret
            self.auth.set_access_token(access_token, access_token_secret)
            # create tweepy API object to fetch tweets
            self.api = tweepy.API(self.auth)
        except:
            print("Error: Authentication Failed")

    def clean_tweet(self, tweet):
        ''' 
        Utility function to clean tweet text by removing links, special characters 
        using simple regex statements. 
        '''
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

    def get_tweets(self, query, geocode, count=10, lang='en', result_type='recent'):
        ''' 
        Main function to fetch tweets and parse them. 
        '''
        # empty list to store parsed tweets
        tweets = []

        try:
            # call twitter api to fetch tweets
            fetched_tweets = self.api.search(
                q=query, count=count, lang=lang, result_type=result_type, geocode=geocode)

            # parsing tweets one by one
            for tweet in fetched_tweets:
                # empty dictionary to store required params of a tweet
                parsed_tweet = {}

                # saving text of tweet
                parsed_tweet['text'] = tweet.text

                # appending parsed tweet to tweets list
                if tweet.retweet_count > 0:
                    # if tweet has retweets, ensure that it is appended only once
                    if parsed_tweet not in tweets:
                        tweets.append(parsed_tweet['text'])
                else:
                    tweets.append(parsed_tweet['text'])

            # return parsed tweets
            return tweets

        except tweepy.TweepError as e:
            # print error (if any)
            print("Error : " + str(e))


def remove_noise(tweet_tokens, stop_words=()):

    cleaned_tokens = []

    for token, tag in pos_tag(tweet_tokens):
        token = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+#]|[!*\(\),]|'
                       '(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', token)
        token = re.sub("(@[A-Za-z0-9_]+)", "", token)

        if tag.startswith("NN"):
            pos = 'n'
        elif tag.startswith('VB'):
            pos = 'v'
        else:
            pos = 'a'

        lemmatizer = WordNetLemmatizer()
        token = lemmatizer.lemmatize(token, pos)

        if len(token) > 0 and token not in string.punctuation and token.lower() not in stop_words:
            cleaned_tokens.append(token.lower())
    return cleaned_tokens


def get_all_words(cleaned_tokens_list):
    for tokens in cleaned_tokens_list:
        for token in tokens:
            yield token


def get_tweets_for_model(cleaned_tokens_list):
    for tweet_tokens in cleaned_tokens_list:
        yield dict([token, True] for token in tweet_tokens)


def main():
    print("Entered Main")
    # creating object of TwitterClient Class
    api = TwitterClient()
    count = 100
    geocode = "42.361145,-71.057083,10mi"

    while(True):
        # calling function to get tweets
        tweets = api.get_tweets(query='the', count=count,
                                lang='en', result_type='recent', geocode=geocode)

        negtweets = []
        postweets = []
        poscount = 0
        negcount = 0

        for tweet in tweets:
            tweet_tokens = remove_noise(word_tokenize(tweet))
            sent = classifier.classify(
                dict([token, True] for token in tweet_tokens))
            if sent == 'Negative':
                negtweets.append(tweet)
                negcount += 1
            elif sent == 'Positive':
                postweets.append(tweet)
                poscount += 1

        # percentage of positive tweets
        pos_tweets = 100*poscount/count

        # percentage of negative tweets
        neg_tweets = 100*negcount/count

        pos_send = int(pos_tweets)
        neg_send = int(neg_tweets)

        #print(pos_send)
        data = str(pos_send)
        ser.write(data.encode('utf-8')) #Send data to arduino. Activate arduino read pin and write to serial 

        waiting = True
        while waiting:
            data1 = ser.readline()[:-2]
            if data1:
                waiting = False
        data1.decode()
        print(data1)

        #print(neg_send)
        data = str(neg_send)
        ser.write(data.encode('utf-8')) #Send data to arduino. Activate arduino read pin and write to serial 

        waiting = True
        while waiting:
            data2 = ser.readline()[:-2]
            if data2:
                waiting = False
        data2.decode()
        print(data2)


        time.sleep(5)

        # printing first 5 positive tweets
        #print("\n\nPositive tweets:")
        #for tweet in postweets[:10]:
        #    print(tweet)

        # printing first 5 negative tweets
        #print("\n\nNegative tweets:")
        #for tweet in negtweets[:10]:
        #    print(tweet)


if __name__ == "__main__":

    positive_tweets = twitter_samples.strings('positive_tweets.json')
    negative_tweets = twitter_samples.strings('negative_tweets.json')
    text = twitter_samples.strings('tweets.20150430-223406.json')
    tweet_tokens = twitter_samples.tokenized('positive_tweets.json')[0]

    stop_words = stopwords.words('english')

    positive_tweet_tokens = twitter_samples.tokenized('positive_tweets.json')
    negative_tweet_tokens = twitter_samples.tokenized('negative_tweets.json')

    positive_cleaned_tokens_list = []
    negative_cleaned_tokens_list = []

    for tokens in positive_tweet_tokens:
        positive_cleaned_tokens_list.append(remove_noise(tokens, stop_words))

    for tokens in negative_tweet_tokens:
        negative_cleaned_tokens_list.append(remove_noise(tokens, stop_words))

    all_pos_words = get_all_words(positive_cleaned_tokens_list)

    freq_dist_pos = FreqDist(all_pos_words)
    print(freq_dist_pos.most_common(10))

    positive_tokens_for_model = get_tweets_for_model(
        positive_cleaned_tokens_list)
    negative_tokens_for_model = get_tweets_for_model(
        negative_cleaned_tokens_list)

    positive_dataset = [(tweet_dict, "Positive")
                        for tweet_dict in positive_tokens_for_model]

    negative_dataset = [(tweet_dict, "Negative")
                        for tweet_dict in negative_tokens_for_model]

    dataset = positive_dataset + negative_dataset

    random.shuffle(dataset)

    train_data = dataset[:7000]
    test_data = dataset[7000:]

    classifier = NaiveBayesClassifier.train(train_data)

    print("Accuracy is:", classify.accuracy(classifier, test_data))

    print(classifier.show_most_informative_features(10))

    #custom_tweet = "I ordered just once from TerribleCo, they screwed up, never used the app again."

    #custom_tokens = remove_noise(word_tokenize(custom_tweet))

    main()
