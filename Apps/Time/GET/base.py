## This base action simply redirects to getting the current server time.
## The curl command to call this (HTTPS enabled):
## curl -k https://localhost:8080/api/Time
import Apps.Time.GET.now as redir

def action(*args,**kwargs):
	#This action just redirects to getting the time now
	return redir.action(*args,**kwargs)
