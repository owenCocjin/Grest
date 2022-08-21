from datetime import datetime
from conn import genericOK,genericFailed

def action(request_headers,request_data,url_args):
	'''Convert the given epoch time to a date/time string.
	Takes x-www-form-urlencoded data: epoch=123456789'''

	try:
		epoch=float(request_data["epoch"])
		return genericOK(datetime.fromtimestamp(epoch).strftime("%Y.%m.%d-%H:%M:%S"))

	except Exception as e:
		return genericFailed(f"Invalid epoch time given: {e}")
