import time

def action(request_headers,request_data,url_args):
	'''Return just the date'''
	return {"status":"OK","response":time.strftime("%Y.%m.%d")}
