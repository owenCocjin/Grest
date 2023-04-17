import reply

def action(request_headers,request_data,url_args):
	'''Simply replies with all data'''
	print(f"[|X:reflect:request_headers]: {request_headers}")
	print(f"[|X:reflect:request_data]: {request_data}")
	print(f"[|X:reflect:url_args]: {url_args}")
	return reply.Ok.JSONResponse("All data",
			request_headers=str(request_headers),
			request_data=str(request_data),
			url_args=str(url_args))
