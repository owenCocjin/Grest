import time
import reply

def action(request_headers,request_data,url_args):
	'''Sleeps for n seconds'''
	if "length" not in url_args:
		return reply.Failed.JSONResponse("""Missing "length" arg!""")

	try:
		time.sleep(float(url_args["length"]))
		return reply.Ok.JSONResponse()
	except ValueError:
		return reply.Failed.JSONResponse(f"Invalid time: {url_args['length']}")