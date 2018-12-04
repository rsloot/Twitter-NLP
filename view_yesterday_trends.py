import get_twitter_data
import time
import datetime
import json

month_dic = {31: [1,3,5,7,8,10,12], 28: [2], 30: [4,6,9,11]}

def main():

	start_date = time.localtime()
	dt = datetime.datetime(start_date.tm_year, start_date.tm_mon,
	                   start_date.tm_mday, 12-((24-start_date.tm_hour)%12),
	                   start_date.tm_min, start_date.tm_sec)
	if dt.day == 1: #new month, adjust yesterday to last day of prev month
		month = dt.month-1
		for k,v in month_dic.items():
			if month in v:
				dt = datetime.datetime(start_date.tm_year, month, k)
	else:
		dt = datetime.datetime(start_date.tm_year, start_date.tm_mon,
	                   start_date.tm_mday-1, 12-((24-start_date.tm_hour)%12),
	                   start_date.tm_min, start_date.tm_sec)

	cur_date = '{:%m-%d-%Y}'.format(dt)
	
	print(cur_date)
	with open('trends/%s.txt'%cur_date, 'r+') as f:
	    trends = json.loads(f.read())
	    # if '#MTVHottest' in trends:
	    #     del trends['#MTVHottest']

	get_twitter_data.plot_trends(trends, cur_date, save=True)#.savefig('tr', format='pdf')

if __name__ == '__main__':
	main()