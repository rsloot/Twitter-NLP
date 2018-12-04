import twitter
import json
import numpy as np
from collections import Counter
import time
import datetime

import nltk
from nltk.stem import PorterStemmer
import string

from auth_twitter import auth_twit
# import get_tweet_data

twittur = auth_twit(app_name='treeing').auth()


def prettyprint_counts(trend, label, list_of_tuples):
#     print(trend)
	print("\n{:^25} | {:^6}".format(label, "Count"))
	print("*"*40)
	for k,v in list_of_tuples:
		print("{:25} | {:>6}".format(k,v))


def get_tweet_info(sorted_d, pop_tweets):
	'''
		params:
				sorted_d: sorted list of keys in trending_topic_tweets
				trending_topic_tweets: raw json from twitter api,

		return:
				pop_tweets_info: a dictionary with tweet text, hashtags, 
									and mentions
	'''
	pop_tweets_info = {}
	# null_status_returned = set()
	for k in sorted_d:
		n = len(pop_tweets[k]['statuses'])
		if n == 0: # No statuses
			# remove from sorted_d
			# null_status_returned.add(k)
			continue
		for i in range(n):
			if k in pop_tweets_info:
				pop_tweets_info[k]['tweets'] += \
									[pop_tweets[k]['statuses'][i]['text']]

				if pop_tweets[k]['statuses'][i]['entities']['hashtags']:
					pop_tweets_info[k]['hashtags'].append(pop_tweets[k]['statuses'][i]['entities']['hashtags'][0]['text'])

				if pop_tweets[k]['statuses'][i]['entities']['user_mentions']:
					for mention in pop_tweets[k]['statuses'][i]['entities']['user_mentions']:
						if 'mentions' in pop_tweets_info[k]:
							pop_tweets_info[k]['mentions'].append(mention['screen_name'])
						else:
							pop_tweets_info[k]['mentions'] = \
												mention['screen_name']
			else:
				pop_tweets_info[k] = {}
				if pop_tweets[k]['statuses'][i]['text']:
					pop_tweets_info[k]['tweets'] = [pop_tweets[k]['statuses'][i]['text']]
				else:
					pop_tweets[k]['tweets'] = []

				if pop_tweets[k]['statuses'][i]['entities']['hashtags']:
					pop_tweets_info[k]['hashtags'] = [pop_tweets[k]['statuses'][i]['entities']['hashtags'][0]['text']]
				else:
					pop_tweets_info[k]['hashtags'] = []

				if pop_tweets[k]['statuses'][i]['entities']['user_mentions']:
					for mention in pop_tweets[k]['statuses'][i]['entities']['user_mentions']:
						if 'mentions' in pop_tweets_info[k]:
							pop_tweets_info[k]['mentions'].append(mention['screen_name'])
						else:
							pop_tweets_info[k]['mentions'] = \
												[mention['screen_name']]
				else:
					pop_tweets_info[k]['mentions'] = []
	
	return pop_tweets_info

def combine_similar_case(sorted_d, pop_tweets_info, pop_tweets):
	dups = []
	for k,v in pop_tweets_info.items():
		if (k != k.lower() and k != k.upper() and k.lower() in pop_tweets):
			pop_tweets_info[k]['tweets'] += \
									pop_tweets_info[k.lower()].pop('tweets')
			pop_tweets_info[k]['mentions'] += \
									pop_tweets_info[k.lower()].pop('mentions')
			pop_tweets_info[k]['hashtags'] += \
									pop_tweets_info[k.lower()].pop('hashtags')
			dups.append(k.lower())
			# continue

		elif (k != k.upper() and k != k.lower() and k.upper() in pop_tweets):
			pop_tweets_info[k]['tweets'] += \
									pop_tweets_info[k.upper()].pop('tweets')
			pop_tweets_info[k]['mentions'] += \
									pop_tweets_info[k.upper()].pop('mentions')
			pop_tweets_info[k]['hashtags'] += \
									pop_tweets_info[k.upper()].pop('hashtags')
			dups.append(k.upper())
	if dups:
		for dup in dups:
			del pop_tweets_info[dup]
			sorted_d.remove(dup)
	return sorted_d, pop_tweets_info


def get_and_clean_tweet_info(sorted_d, save_tweets=True, 
							 cur_date=None):#, counter_dict={}):
	'''
		Get's the top-100 tweets associated with the trends of the current 
			hour, combining duplicate trends (same text different case).

		params:
				sorted_d: a list of the top trends sorted most active
							(based on tweet activity) to least active.

		return:
				pop_tweets_info: dictionary of segmented tweet info, tweet 
								text, mentions in the text,	and hashtags 
								in the text.
	'''
	pop_tweets = {}

	if cur_date is None:
		cur_date = time.localtime()
		dt = datetime.datetime(cur_date.tm_year, cur_date.tm_mon,
							   cur_date.tm_mday, 12-((24-cur_date.tm_hour)%12),
							   cur_date.tm_min, cur_date.tm_sec)
		cur_date = '{:%m-%d-%Y}'.format(dt)
	# try:
	# 	with open('tweets of trends/%s.txt'%cur_date, 'r+') as f:
	# 		pop_tweets_info = json.loads(f.read())
	# except FileNotFoundError as e:
	# 	pop_tweets_info = {}
		# print("All popular")
	for trend in sorted_d:
		pop_tweets[trend] = twittur.search.tweets(q=trend,
												  result_type='mixed',
												  count=100)

	# if pop_tweets_info and counter_dict:
	# 	for trend in sorted_d:

	# 		if trend in pop_tweets_info and counter_dict[trend]==2:
	# 			pop_tweets[trend] = twittur.search.tweets(q=trend, 
	# 											  result_type='mixed',
	# 											  count=100)
	# 			# print('mixed')
	# 			counter_dict[trend] = 0 # reset counter
	# 		elif trend in pop_tweets_info:
	# 			pop_tweets[trend] = twittur.search.tweets(q=trend, 
	# 											  result_type='recent',
	# 											  count=100)
	# 			# print('recent')
	# 			counter_dict[trend] += 1
	# 		else:
	# 			pop_tweets[trend] = twittur.search.tweets(q=trend, 
	# 											  result_type='popular',
	# 											  count=100)
	# 			# print('popular')
	# 			counter_dict[trend] = 1
	# else: ## All populars, new day/file
	# 	for trend in sorted_d:
	# 		pop_tweets[trend] = twittur.search.tweets(q=trend, 
	# 											  result_type='popular',
	# 											  count=100)
	# 		# print('popular')
	# 		counter_dict[trend] = 1
	# print('hi')

	# for k in sorted_d:
		# pop_tweets_info = get_tweet_info(sorted_d, pop_tweets)
	# dups = []
	# if pop_tweets_info:
	new_pop_tweets_info = get_tweet_info(sorted_d, pop_tweets)
	sorted_d, new_pop_tweets_info = combine_similar_case(sorted_d,
														 new_pop_tweets_info,
														 pop_tweets)
	# else:
		# new_pop_tweets_info = get_tweet_info(sorted_d, pop_tweets)
		# sorted_d, new_pop_tweets_info = combine_similar_case(sorted_d,
														 # pop_tweets_info)
		# pop_tweets_info = {}
		
				# continue

	
	for k in sorted_d.copy():
		## only reason not to have equal keys is if No Statuses were returned
		## remove these from sorted_d
		if k not in new_pop_tweets_info:
			sorted_d.remove(k)
	# ************************************************************************
	assert len(new_pop_tweets_info) == len(sorted_d), "ruh roh\nlen(sorted_d): %d\nlen(pop_tweets_info): %d"%(len(sorted_d), len(new_pop_tweets_info))
	# ************************************************************************
	#### REDUCING SIZE of SAVED FILEs
	new_tweet_dict = {}
	elements = ['hashtags', 'tweets', 'mentions']
	for k in new_pop_tweets_info:
		new_tweet_dict[k] = {}
		for el in elements:
			new_tweet_dict[k][el] = {}
#         	print(pop_tweets_info[k][el])
#         	break
			for i in new_pop_tweets_info[k][el]:
				if i in new_tweet_dict[k][el]:
					new_tweet_dict[k][el][i] += 1
				else:
					new_tweet_dict[k][el][i] = 1
     #####

	if save_tweets:
		cur_date = time.localtime()
		dt = datetime.datetime(cur_date.tm_year, cur_date.tm_mon,
							   cur_date.tm_mday, 12-((24-cur_date.tm_hour)%12),
							   cur_date.tm_min, cur_date.tm_sec)
		cur_time = '{:%m-%d-%Y %H:%M:%S}'.format(dt)
		save_date = '{:%m-%d-%Y}'.format(dt)

		try:
			with open('tweets of trends\%s.txt'%save_date, 'r+') as f:	
				d = json.loads(f.read())
				
				for trend in sorted_d:
					if trend in d:
						for el in elements: #keys are [tweets, mentions, hashtags]
							for i in new_tweet_dict[trend][el]:
								if i in d[trend][el]:
									d[trend][el][i] += new_tweet_dict[trend][el][i]
								else:
									d[trend][el][i] = new_tweet_dict[trend][el][i]
							# d[trend][el] += pop_tweets_info[trend][el] #update file
					else:
						d[trend] = {}
						for el in elements:
							d[trend][el] = new_tweet_dict[trend][el]

				f.seek(0)
				f.truncate() # overwrite file
				json.dump(d, f)
				print('\n\n**Tweets SAVED - %s**\n'%cur_time)
		except FileNotFoundError as e:
			print(e)
			with open('tweets of trends\%s.txt'%save_date, 'w+') as f:
				json.dump(new_tweet_dict, f)
				print('\n\n**Tweets SAVED - %s**\n'%cur_time)

	return new_pop_tweets_info#, counter_dict


def get_words_from_status_text(pop_tweets_info):
	status_words = {}
	for k,value in pop_tweets_info.items():
		for tweet in value['tweets']:
			if k in status_words:
				status_words[k] += tweet.split()
			else:
				status_words[k] = tweet.split()
	return status_words


def extract_and_clean(status_words):
	'''
		extracts hashtags and mentions from tweet text

		params:
			status_words: dictionary, keys are trends, values are words
							from the tweets associated with the trend.

		returns:
			tuple of three dictionaries, hashtags, mentions, and word_counts
	'''
	## Extracting hashtags and mentions from tweet text
	## Entities attribute sort of worthless
	## cleaning !ugh!
	# Removing Stopwords
	stop_words = nltk.corpus.stopwords.words('english') +\
					nltk.corpus.stopwords.words('spanish') +\
					list(string.punctuation) + ['rt']
	ps = PorterStemmer()

	word_counts = {k:Counter(v) for k,v in status_words.items()}
	cleaner_words = {k:Counter(v) for k,v in status_words.items()}

	hashtags = {}
	mentions = {}

	for trend, counter in word_counts.items():
		hashtags[trend] = {}
		mentions[trend] = {}
		for key_word, value in counter.most_common():
			stripped_key_word = \
						key_word.strip(string.punctuation.replace('@', ''))
			if '#' in key_word:
				hashtags[trend][key_word] = word_counts[trend].pop(key_word)
			elif '@' in key_word:
				if key_word[-1] == ':':
					if key_word[:-1] in mentions[trend]:
						mentions[trend][key_word[:-1]] += \
											word_counts[trend].pop(key_word)
					else:
						mentions[trend][key_word[:-1]] = \
											word_counts[trend].pop(key_word)
				else:
					mentions[trend][stripped_key_word] = \
											word_counts[trend].pop(key_word)
			# remove single characters
			elif len(key_word) < 2:
				word_counts[trend].pop(key_word)
			#             # count += 1
			elif ps.stem(key_word.lower()) in stop_words:
				word_counts[trend].pop(key_word)
			#             # count += 1
			elif key_word.lower() in stop_words:
				word_counts[trend].pop(key_word)
			#             # count += 1
			# if ending with punctuation, remove and store in key w/o punct
			elif key_word[-1] in string.punctuation:
				if key_word[:-1] in counter:
					word_counts[trend][key_word[:-1]] += \
											word_counts[trend].pop(key_word)
				else:
					word_counts[trend][key_word[:-1]] = \
											word_counts[trend].pop(key_word)
			# if lower duplicate in keys
			# example if have 'Hello' and 'hello' remove 'hello' and store
			# values in 'Hello'
			elif (key_word != key_word.lower() and 
				  key_word != key_word.upper() and 
				  key_word.lower() in counter):
					word_counts[trend][key_word] += \
									word_counts[trend].pop(key_word.lower())
			# if upper duplicate in keys, i.e., 'Hello' and 'HELLO', 
			# remove 'HELLO' store values in 'Hello'
			elif (key_word != key_word.upper() and 
				  key_word != key_word.lower() and 
				  key_word.upper() in counter):
				word_counts[trend][key_word] +=\
									word_counts[trend].pop(key_word.upper())
	# print('{0} words removed'.format(count))

	return (hashtags, mentions, word_counts)


def print_it(sorted_d, word_counts, mentions, hashtags):
	for sorted_trend in sorted_d:
		print('\n\n{:^35}'.format(sorted_trend))

		for label, data in (('Words', word_counts[sorted_trend]),
							('Mentions', mentions[sorted_trend]),
							('Hashtags', hashtags[sorted_trend])):

			n=20
			sorted_data_keys = sorted(data, key=data.get, reverse=True)
			top_n = [(k,data[k]) for i,k in enumerate(sorted_data_keys) if i<n]
		#         print(trend)
			prettyprint_counts(sorted_trend, label, top_n)
		# break
	print('\n\n\nhi :)')


def do_everything(trends_data, save_tweets=True,
				  analyze_tweets=False):#, counter_dict={}):
	if trends_data is None:
		return
	for k,v in trends_data.items():
		if v is None:
			trends_data[k] = 0
	sorted_d = sorted(trends_data, key=trends_data.get, reverse=True)
	pop_tweets_info = get_and_clean_tweet_info(sorted_d=sorted_d, 
											  save_tweets=save_tweets)
	# pop_tweets_info, counter_dict = get_and_clean_tweet_info(sorted_d=sorted_d, 
	# 										  save_tweets=save_tweets, 
	# 										  counter_dict=counter_dict)
	if analyze_tweets:
		status_words = get_words_from_status_text(pop_tweets_info)
		hashtags, mentions, word_counts = extract_and_clean(status_words)
		print_it(sorted_d=sorted_d, word_counts=word_counts, 
				 mentions=mentions, hashtags=hashtags)
		# plot_trends(trends_data, time.localtime()[:3])
	# print(counter_dict)
	# return counter_dict

import sys
def main():

	if len(sys.argv) > 1:
		# print(len(sys.argv))
		f_name = sys.argv[1]
		try:
			with open(f_name, 'r') as f:
				data = json.loads(f.read())
		except Exception as e:
			print('you fucked up')
			return

		if data:
			for k,v in data.items():
				if v is None:
					data[k] = 0
			sorted_d = sorted(data, key=data.get, reverse=True)
		else:
			return 'Some Error'
				# break
			# pop_tweets_statuses = {}

		if len(sys.argv) > 2:
			if sys.argv[2] == '-get':
				pop_tweets_info = get_and_clean_tweet_info(sorted_d=sorted_d, 
														   save_tweets=True)

			if sys.argv[2] == '-o':
				try:
					with open('test_tweets.txt', 'r+') as tweet_info_file:
						pop_tweets_info = json.load(tweet_info_file)
				except Exception as e:
					print(e)
					return
			if sys.argv[2] == '-a':
				do_everything(trends_data=data, analyze_tweets=True)
				

	# status_words = get_words_from_status_text(pop_tweets_info)
	# hashtags, mentions, word_counts = extract_and_clean(status_words)
	# print_it(sorted_d=sorted_d, word_counts=word_counts, 
	# 		 mentions=mentions, hashtags=hashtags)

	# ## Extracting hashtags and mentions from tweet text
	# ## Entities attribute sort of worthless
	# ## cleaning !ugh!
	# # Removing Stopwords
	# word_counts = {k:Counter(v) for k,v in status_words.items()}
	# stop_words = nltk.corpus.stopwords.words('english') +\
	# 				nltk.corpus.stopwords.words('spanish') +\
	# 				list(string.punctuation) + ['rt']
	# ps = PorterStemmer()

	# word_counts = {k:Counter(v) for k,v in status_words.items()}
	# cleaner_words = {k:Counter(v) for k,v in status_words.items()}

	# hashtags = {}
	# mentions = {}

	# for trend, counter in word_counts.items():
	# 	hashtags[trend] = {}
	# 	mentions[trend] = {}
	# 	for key_word, value in counter.most_common():
	# 		stripped_key_word = \
	# 					key_word.strip(string.punctuation.replace('@', ''))
	# 		if '#' in key_word:
	# 			hashtags[trend][key_word] = word_counts[trend].pop(key_word)
	# 		elif '@' in key_word:
	# 			if key_word[-1] == ':':
	# 				if key_word[:-1] in mentions[trend]:
	# 					mentions[trend][key_word[:-1]] += \
	# 										word_counts[trend].pop(key_word)
	# 				else:
	# 					mentions[trend][key_word[:-1]] = \
	# 										word_counts[trend].pop(key_word)
	# 			else:
	# 				mentions[trend][stripped_key_word] = \
	# 										word_counts[trend].pop(key_word)
	# 		elif len(key_word) < 2:
	# 			word_counts[trend].pop(key_word)
	# 		#             # count += 1
	# 		elif ps.stem(key_word.lower()) in stop_words:
	# 			word_counts[trend].pop(key_word)
	# 		#             # count += 1
	# 		elif key_word.lower() in stop_words:
	# 			word_counts[trend].pop(key_word)
	# 		#             # count += 1
	# 		elif key_word[-1] in string.punctuation:
	# 			if key_word[:-1] in counter:
	# 				word_counts[trend][key_word[:-1]] += \
	# 										word_counts[trend].pop(key_word)
	# 			else:
	# 				word_counts[trend][key_word[:-1]] = \
	# 										word_counts[trend].pop(key_word)
	# 		elif (key_word != key_word.lower() and 
	# 			  key_word != key_word.upper() and 
	# 			  key_word.lower() in counter):
	# 				word_counts[trend][key_word] += \
	# 								word_counts[trend].pop(key_word.lower())
	# 		elif (key_word != key_word.upper() and 
	# 			  key_word != key_word.lower() and 
	# 			  key_word.upper() in counter):
	# 			word_counts[trend][key_word] +=\
	# 								word_counts[trend].pop(key_word.upper())
	# # print('{0} words removed'.format(count))

	##  word_counts --> {trend: {Counter: {'words': word_count}}...}
	## remove punctuation from end of words, so can be counted same
	#*******
	# for key_trend, v_counter in word_counts.items():
	# 	for key_word, word_count in v_counter.most_common():
	# 		if key_word[-1] in string.punctuation:
	# 			if key_word[:-1] in v_counter:
	# 				word_counts[key_trend][key_word[:-1]] += \
	# 									word_counts[key_trend].pop(key_word)
	# 			else:
	# 				word_counts[key_trend][key_word[:-1]] = \
	# 									word_counts[key_trend].pop(key_word)
	## Removing case variation in words in tweets, 
	## e.g., so Hello is counted same as hello
	# for key_trend, v_counter in word_counts.items():
	# 	for key_word, word_count in v_counter.most_common():
	# 		if (key_word != key_word.lower() and 
	# 			key_word.lower() in v_counter):

	# 			word_counts[key_trend][key_word] += \
	# 							word_counts[key_trend].pop(key_word.lower())

	# ****************

	# for sorted_trend in sorted_d:
	# 	print('\n\n{:^35}'.format(sorted_trend))

	# 	for label, data in (('Words', word_counts[sorted_trend]),
	# 						('Mentions', mentions[sorted_trend]),
	# 						('Hashtags', hashtags[sorted_trend])):

	# 		n=20
	# 		sorted_data_keys = sorted(data, key=data.get, reverse=True)
	# 		top_n = [(k,data[k]) for i,k in enumerate(sorted_data_keys) if i<n]
	# 	#         print(trend)
	# 		prettyprint_counts(sorted_trend, label, top_n)
	# 	break
	# print('\n\n\nhi :)')

if __name__ == '__main__':
	main()