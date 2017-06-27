import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import json
import time
import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
import string
import glob
import os
import gensim
from gensim import corpora
from nltk import pos_tag, word_tokenize
import csv
import datetime
from nltk.probability import FreqDist

def read_status(t_id):
	"""
	INPUT: None
	OUTPUT: pandas data frame from file
	"""
	return pd.read_csv("%s_tweets.csv" %t_id)


def filter_date (start_date, end_date, df):

	df["created_at"] = pd.to_datetime(df["created_at"])  
	mask = (df["created_at"] > start_date) & (df["created_at"] <= end_date)
	df = df.loc[mask]

	return df

def filter_language (df):
	df['lang'] = ''
	df['prob'] = ''

	for index, row in df.iterrows():
		df['lang'][index], df['prob'][index] = langid.classify(row['text'])

	return df[df.lang == 'en']

def topic_detection(df_column):
	stop = set(stopwords.words('english'))
	exclude = set(string.punctuation) 
	lemma = WordNetLemmatizer()

	def clean(doc):
		stop_free = " ".join([i for i in str(doc).lower().split() if i not in stop])
		punc_free = ''.join(ch for ch in stop_free if ch not in exclude)
		normalized = " ".join(lemma.lemmatize(word) for word in punc_free.decode('utf-8').split())
		return normalized

	reviews_clean = [clean(reviews).split() for reviews in df_column]

	# Creating the term dictionary of our courpus, where every unique term is assigned an index. 
	dictionary = corpora.Dictionary(reviews_clean)

	# Converting list of documents (corpus) into Document Term Matrix using dictionary prepared above.
	doc_term_matrix = [dictionary.doc2bow(review) for review in reviews_clean]

	# Creating the object for LDA model using gensim library
	Lda = gensim.models.ldamodel.LdaModel

	# Running and Trainign LDA model on the document term matrix.
	ldamodel = Lda(doc_term_matrix, num_topics=5, id2word = dictionary, passes=50)

	return ldamodel.print_topics(num_topics=5, num_words=5)

def most_engaging_content(df_tweets):

	df_tweets['engagement'] = df_tweets['retweet_count'] + df_tweets['favorite_count'] 
	i = pd.Index(df_tweets["engagement"]).get_loc(df_tweets.engagement.max())

	return df_tweets["text"][i]


def freq_words(df_tweets):
	fdist1 = FreqDist(df_tweets['text'])
	fdist1.most_common(10) 

	return fdist1.most_common(10) 

def super_users(t_id):
	df_follower = pd.read_csv("%sfollowers.csv" %t_id)
	superusers = df_tweets['comment_author'].value_counts()
	return superusers[:5]

def run_analysis(t_id, start_date, end_date): 

	df_tweets = filter_date(start_date, end_date, read_status(t_id))
	print "Done importing statuses."

	num_status = df_tweets['id'].count()

	status_topics = topic_detection(df_tweets['text'])
	print "Done topic detection on statuses."


	print "Calculating engagement."
	df_tweets['engagement'] = df_tweets['retweet_count'] + df_tweets['favorite_count']
	print "Calculating daily engagement."
	start = datetime.datetime.strptime(start_date, "%Y-%m-%d")
	end = datetime.datetime.strptime(end_date, "%Y-%m-%d")
	eng = df_tweets['engagement'].sum()/(end-start).days
	frequent_words = freq_words(df_tweets)
	print "Done analyzing frequent words"
	print "Done analyzing average comments length"
	#superusers = super_users(df_tweets)
	#print "Done analyzing superusers"

	time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	period = str(start_date) + " - " + str(end_date)

	with open('%s_tweets_analysis.csv' % t_id, 'wb') as file:
		print "Opening new files to write."
		w = csv.writer(file)
		w.writerow(["t_id","time_of_analysis", "period_selected", "num_of_status", "daily_engagement", 
			"frequently_used_words"])
		w.writerow([t_id, time, period, num_status, eng,
			frequent_words])


if __name__ == "__main__":


	run_analysis(t_id, start_date, end_date)