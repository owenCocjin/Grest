import json
import reply

def action(request_headers,request_data,url_args):
	'''Simply replies with all data'''
	print(f"[|X:reflect:request_headers]: {request_headers}")
	print(f"[|X:reflect:request_data]: {request_data}")
	print(f"[|X:reflect:url_args]: {url_args}")
	try:
		return reply.Ok.JSONResponse("All data",
				request_headers=request_headers,
				request_data=str(request_data) if type(request_data)!=dict else request_data,
				url_args=url_args)
	except Exception as e:
		return reply.Failed.JSONResponse(f"{e.__class__.__name__}: {e}")