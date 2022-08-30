import time,base64
import reply

def action(request_headers,request_data,url_args):
	to_ret=None
	#Base64 decode the given format time if passed
	if "format" in url_args:
		try:
			format=base64.b64decode(url_args["format"]).decode()
		except:
			return reply.Failed.JSONResponse("Format value is invalid",extra="Make sure it is base64 encoded and adheers to the standard strftime() formatting")
	else:
		format="%Y.%m.%d-%H:%M:%S"

	if "time_only" in url_args:
		to_ret=reply.Ok.JSONResponse(f"{time.strftime(format)}")
	else:
		to_ret=reply.Ok.JSONResponse(f"The current time (on the server) is: {time.strftime(format)}")

	#Add epoch as header just for fun :)
	to_ret.addHeaders(f"Epoch: {int(time.time())}")

	return to_ret
