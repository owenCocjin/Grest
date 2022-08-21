import os
import globe

def action(*args,**kwargs):
	'''List all apps'''
	return {"status":"OK","response":[a for a in globe.ALL_APPS]}
