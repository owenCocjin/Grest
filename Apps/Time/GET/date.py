import time
import reply

def action(request_headers,request_data,url_args):
	'''Return just the date'''
	return reply.Ok.JSONResponse(time.strftime("%Y.%m.%d"))
