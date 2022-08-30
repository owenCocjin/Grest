## DO NOT USE THIS DATABASE!!!
## IT HAS KNOWN KEYS!!!
## Token:
##   username: tester
##   token:    2RRdjEqDbiSzq+4o/MwciEoqjpXYVeZIrkiA5g93qHY=
import parsing,reply
from auth import Auth

def action(request_headers,request_data,url_args):
	'''Do not use this database!!!
	It has shared and known keys!'''
	AuthDB=Auth(request_headers,db_path="./Apps/DummyAuth/authentication.db",return_cols=["username"])
	auth=AuthDB.bearer()

	if auth!=reply.Ok:  #If something went wrong while authenticating
		return auth  #This will return the error associated with the specific failure
	else:  #Authentication succeeded, and returned the "username" column
		print(f"""Authenticated as: {auth["response"][0][0]}""")
		return auth
