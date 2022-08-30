import os
import globe,reply

def action(*args,**kwargs):
	'''List all apps'''
	return reply.Ok.JSONResponse([a for a in globe.ALL_APPS])
