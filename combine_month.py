import numpy as np
import os
import json

def combine_tweets(month_name, month_number):
	tweet_files = list(os.walk(top='./tweets of trends'))
	month_dict = {}
	for date in tweet_files[0][2]:
		date_str = date[:date.find('.')]
		if str(month_number) in date[:2]:
			with open('./tweets of trends/'+date, 'r+') as day_file:
				# d[i] = None
				month_dict[date_str] = json.loads(day_file.read())

			# break
	# exp = {1: 'hello', 2:'world'}r
	with open(f'./Monthly_tweets/{month_name}.txt', 'w+') as f:
		# f.seek()
		json.dump(month_dict, f)

def combine_trends(month_name, month_number):
	trend_file_list = list(os.walk(top='./trends'))
	trends_dict = {}
	for date in trend_file_list[0][2]:
		date_str = date[:date.find('.')]
		if str(month_number) in date[:2]:
			with open('./trends/' + date, 'r+') as day_file:
				# d[i] = None
				trends_dict[date_str] = json.loads(day_file.read())

			# break
	# exp = {1: 'hello', 2:'world'}
	with open(f'./Monthly_trends/{month_name}.txt', 'w+') as f:
		# f.seek()
		json.dump(trends_dict, f)

def main():
	combine_tweets('October', 10)
	combine_trends('October', 10)

if __name__ == '__main__':
	main()

