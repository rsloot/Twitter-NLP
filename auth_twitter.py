import pickle
import twitter
import os


class auth_twit(object):
	def __init__(self, app_name=None, con_key=None, con_sec=None, acc_tok=None, acc_tok_sec=None):
		self.app_name = app_name
		# elif app_name and con_key and con_sec and acc_tok and acc_tok_sec:
		self.app_name = app_name
		self.con_key = con_key
		self.con_sec = con_sec
		self.acc_tok = acc_tok
		self.acc_tok_sec = acc_tok_sec
		# self.app(app_name, con_key, con_sec, acc_tok, acc_tok_sec)
	def auth(self):
		try:
			creds = pickle.load(open('secret_twitter_credentials_%s.pkl'%self.app_name,'rb'))
			auth = twitter.oauth.OAuth(creds['Access Token'],
									   creds['Access Token Secret'],
									   creds['Consumer Key'],
									   creds['Consumer Secret'])
			twitter_api = twitter.Twitter(auth=auth)
			# print('1')
			return twitter_api
		except Exception as e:
			# raise e
			print(e)
		
	def app(self):
		if not os.path.exists('secret_twitter_credentials_%s.pkl'%self.app_name):
			Twitter={}
			Twitter['Consumer Key'] = self.con_key
			Twitter['Consumer Secret'] = self.con_sec
			Twitter['Access Token'] = self.acc_tok
			Twitter['Access Token Secret'] = self.acc_tok_sec
			with open('secret_twitter_credentials_%s.pkl'%self.app_name,'wb') as f:
				pickle.dump(Twitter, f)
		# else:
		# 	Twitter=pickle.load(open('secret_twitter_credentials_%s.pkl'%self.app_name,'rb'))
		return self.auth()

	

# if __name__ == '__main__':
# 	main()