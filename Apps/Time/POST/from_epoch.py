from datetime import datetime
import reply

def action(request_headers,request_data,url_args):
	'''Convert the given epoch time to a date/time string.
	Takes x-www-form-urlencoded data: epoch=123456789'''

	try:
		epoch=float(request_data["epoch"])
		return reply.Ok.JSONResponse(datetime.fromtimestamp(epoch).strftime("%Y.%m.%d-%H:%M:%S"))

	except Exception as e:
		return reply.Failed.JSONResponse(f"Invalid epoch time given: {e}")
