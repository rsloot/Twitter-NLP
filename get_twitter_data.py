import os
import pickle
import twitter
import time
import datetime
import sys
import json

import numpy as np
import matplotlib.pyplot as plt

from auth_twitter import auth_twit
twitter_api = auth_twit(app_name='').auth()

import tweets_of_trends_analysis


def write_to(trends, cur_date, cur_time=None):
	'''
		writes trends data to file. Overwriting previous entries if same date.
	'''
	for k,v in trends.copy().items():
		if k != k.lower() and k != k.upper() and k.lower() in trends:
			trends[k] += trends.pop(k.lower())
		elif k !=k.upper() and k != k.lower() and k.upper() in trends:
			trends[k] += trends.pop(k.upper())

	try:
		with open('trends\%s.txt'%cur_date, 'r+') as f:
			d = json.loads(f.read())
			# print(d)
			for k,v in trends.items():
				d[k] = v #update the count in file
			# print(d)
			f.seek(0)
			f.truncate() # overwrite file
			json.dump(d, f)
			print('\n\n**TRENDS SAVED - %s**\n'%cur_time)
	except Exception as e:
		print(e)
		with open('trends\%s.txt'%cur_date, 'w+') as f:
			json.dump(trends, f)
			print('\n\n**TRENDS SAVED - %s**\n'%cur_time)

def plot_trends(trends, cur_date, save=False):
	import numpy as np
	for k,v in trends.copy().items():
		if k != k.lower() and k != k.upper() and k.lower() in trends:
			trends[k] += trends.pop(k.lower())
		elif k !=k.upper() and k != k.lower() and k.upper() in trends:
			trends[k] += trends.pop(k.upper())
	plt.figure(figsize=(len(trends)*3,20))
	scaled_values = [np.sqrt(i) for i in trends.values()]
	plt.bar(range(len(trends)), scaled_values, align='center')
	plt.xticks(range(len(trends)), trends.keys())
	plt.ylim(0,max(scaled_values)+10)
	plt.ylabel('Number of Tweets scaled using square root')
	plt.xlabel('Trending topics')
	plt.title('Trending topics for %s' % cur_date)
	if save:
		plt.savefig('tr%s.pdf'%cur_date)
	plt.show()


def quick_analysis(trends_file=None, pop_tweets_file=None, top_n=10):
	if trends_file and pop_tweets_file:
		try:
			with open(trends_file, 'r+') as trends_file:
				trends = json.loads(trends_file.read())
		except Exception as e:
			print('Trends file Error', e)
			return
		try:
			with open(pop_tweets_file, 'r+') as pop_tweets_file:
				pop_tweets_info = json.loads(pop_tweets_file.read())
		except Exception as e:
			print('Popular tweets file Error', e)
			return
		sorted_d = sorted(trends, key=trends.get, reverse=True)
		status_words = tweets_of_trends_analysis.get_words_from_status_text(pop_tweets_info)
		hashtags, mentions, word_counts = tweets_of_trends_analysis.extract_and_clean(status_words)
		tweets_of_trends_analysis.print_it(sorted_d=sorted_d[:top_n], word_counts=word_counts, 
				 mentions=mentions, hashtags=hashtags)
		plot_trends(trends, str(time.localtime()[:3]))



def get_twitter_trends(woeid='23424977', exclude='hashtags', how_long=-1, 
						view_plot=False, all_day=False, run_all_month=False,
						run_once=False):#, counter_dict={}):
	'''
		getting the twitter trends for a specified place (U.S.)

	Params:
			woeid: (http://woeid.rosselliot.co.nz/lookup/) where on eath ID, 
					defualt to United States (23424977)
			exclude: trends to exclude, defualt to excluding hashtags, i.e, #tbt
			how_long: int defining how many times to pull trends, defaulting 
						to 1 (once) if greater than one will pull trends once
						every 4 minutes for the number of hours indicated by 
						value passed.
			view_plot: will show bar plot of trending topics for the current 
						period, defualt to false. (boolean value)
			all_day: will override how_long parameter; pulling trending topics
						untilthe end of the current day.
			run_all_month: defaults to False, meaning will pull scripts each 
							day for the current month.
			run_once: if only wanting to pull trends for one day, or certain 
						amount of time, change to true.
						MUST BE TRUE if using how_long parameter.
	Saves trends in .txt file (timestamp.txt) in json form
	'''
	# n_sleep = 3 * (how_long-1)
	# i = 0
	# trends = {}
	# start_date = time.localtime()[:3] #todays date ([YYYY,MM,DD])
	# cur_date = '%s-%s-%s'%(start_date[1],start_date[2],start_date[0]) # DD-MM-YYYY
	# count=1
	try:
		while run_all_month or run_once or how_long:
			trends = {}
			start_date = time.localtime() #todays date ([YYYY,MM,DD])
			# cur_date = '%s-%s-%s'%(start_date.tm_mon, start_date.tm_mday, start_date.tm_year) # DD-MM-YYYY
			dt = datetime.datetime(start_date.tm_year, start_date.tm_mon,
							   start_date.tm_mday, 12-((24-start_date.tm_hour)%12),
							   start_date.tm_min, start_date.tm_sec)
			cur_date = '{:%m-%d-%Y}'.format(dt)

			count=1
			while run_once or how_long or all_day:
				try:
					if all_day:
						if time.localtime()[:3] != start_date[:3]:
							# all_day = false
							write_to(trends, cur_date, cur_time)
							break
					cur = twitter_api.trends.place(_id=woeid, exclude=exclude)[0]
					# print(json.dumps(cur, indent=1))
					trends_json = cur['trends']
					for i in trends_json:
					# if trend is not in dict, add it, otherwise update count	
						if i['name'] not in trends:
							if i['tweet_volume']:
								trends[i['name']] = i['tweet_volume']
						elif i['name'] in trends:
							trends[i['name']] = i['tweet_volume']
					ctime = time.localtime()
					dt = datetime.datetime(ctime.tm_year, ctime.tm_mon,
								   ctime.tm_mday, 12-((24-ctime.tm_hour)%12),
								   ctime.tm_min, ctime.tm_sec)
					cur_time = '{:%H:%M:%S}'.format(dt)
					print('[%s] Collecting trends...%d' % (cur_time, count))

					if how_long > 0:
						how_long -= 1
					if how_long == 0:
						tweets_of_trends_analysis.do_everything(trends_data=trends,
																save_tweets=True,
																analyze_tweets=True)
						break
					if run_once:
						tweets_of_trends_analysis.do_everything(trends_data=trends,
																save_tweets=False,
																analyze_tweets=True)
						break
					## get tweets for all current trends each hour
					## have to use different app to avoid rate limits hmmm
					#TODO
					# if counter_dict is None:
					# 	counter_dict = {}
					if (count*240) % 1920 == 0: #every 32 minutes (1920 seconds)
						tweets_of_trends_analysis.do_everything(trends_data=trends,
																save_tweets=True,
																analyze_tweets=False)#,
																#counter_dict=counter_dict)
						write_to(trends, cur_date, cur_time)
						# if '':
						# 	pass
						# elif:#TODO
						# 	pass
					# print(counter_dict)
					count += 1
					time.sleep(240) #every 4 minutes, 15 times an hour, Twitter rate max rate limit
				except KeyboardInterrupt:
					write_to(trends=trends, cur_date=cur_date, 
							 cur_time=cur_time)
					tweets_of_trends_analysis.do_everything(trends_data=trends,
															save_tweets=True,
															analyze_tweets=False)

			if view_plot:
				plot_trends(trends, cur_date)

			# Save trends
			# write_to(trends, cur_date)
			# print(trends, cur_date)

			if start_date[1] != time.localtime()[1]: #end when we start new month ([YYYY,MM,DD])
				break
			if run_once:
				break

	except KeyboardInterrupt:
		write_to(trends, cur_date)
		return



def main():
	if len(sys.argv) > 1:
		flags = sys.argv
		if flags[1] == '-a': # specify all day
			get_twitter_trends(exclude=None, all_day=True, run_all_month=True)
		if flags[1] == '-l': #specify how many pulls (once every 4 minutes)
			get_twitter_trends(exclude=None, how_long=int(flags[2]))
		if flags[1] == '-e': #exclude hashtags show plot
			get_twitter_trends(how_long=1, view_plot=True)
	else: #default, get all current trends, look at plot
		get_twitter_trends(exclude=None, how_long=1, view_plot=True)

	# home_tweets = twitter_api.statuses.home_timeline(count=n)
	# x = [twitter_api.statuses.home_timeline(count=int(sys.argv[1]))[0]['text'] /
				# for i in range(int(sys.argv[1]))]
	# print(len(home_tweets))
	# print()
	# print('\n\n'.join([home_tweets[i]['text'] for i in range(n)]))
	# print(sys.argv)
	# if len(sys.argv)>1:
	# 	get_twitter_trends(how_long=int(sys.argv[1]))
	# else:
	# 	get_twitter_trends(exclude=None)

	# print(help(get_twitter_trends))
if __name__ == '__main__':
	main()