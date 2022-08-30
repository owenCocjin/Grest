## This base action takes an epoch time as input.
## The curl command to test this (HTTPS enabled):
## curl -k -X POST https://localhost:8080/api/Time/1661109578
import Apps.Time.POST.from_epoch as redir
import reply
action_as_input=True

def action(req_headers,req_data,url_args,base_input=None):
	'''Return from_epoch, but allow the action to be the base input'''
	if not base_input:
		return reply.Failed.JSONResponse("No epoch time given")

	try:
		return redir.action(req_headers,{"epoch":int(base_input)},url_args)
	except ValueError:
		return reply.Failed.JSONResponse("Invalid epoch time given",extra="Must pass an int")
