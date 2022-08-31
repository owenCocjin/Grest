## This file holds all errors
import json
import globe

class APIError(Exception):
	def __init__(self,message:str,code:int,hint:str,response:str,extra:str=None):
		'''"cli" is the client socket to send through
		"code" is the integer HTTP error code
		"hint" is the error hint (ex: 200 OK)
		"payload" is the response string
		"extra" is the extra error info'''

		Exception.__init__(self,message)
		self.code=code
		self.hint=hint
		self.response=response
		self.extra=extra
		#Build the payload to return
	def closeCli(self,cli):
		'''Close client with this error code'''
		#Build payload so it's easier to calculate it's length
		payload={"success":"Failed","response":self.response}
		if self.extra:
			payload["extra"]=self.extra
		payload=json.dumps(payload)

		cli.send(f"""{globe.HTTP_VERSION} {self.code} {self.hint}\r
Connection: close\r
Content-Type: application/json\r
Content-Length: {len(payload)}\r
\r
{payload}""".encode())
		cli.close()

#Alphabetic order
class APIPathError(APIError):
	def __init__(self,message="Bad path given"):
		APIError.__init__(self,message=message,code=400,hint="Bad Request",response="Client sent a bad API request",extra="Ensure the requested path follows: 'http://url:port/api/target_app/target_action'")
class ActionDoesntExistError(APIError):
	def __init__(self,message="Requested action doesn't exist"):
		APIError.__init__(self,message=message,code=404,hint="Not Found",response="Requested action doesn't exist",extra="This server is case sensitive. Make sure the requested action is in the correct case. Also check that the action exists under the requested method")
class AppDoesntExistError(APIError):
	def __init__(self,message="Requested app doesn't exist"):
		APIError.__init__(self,message=message,code=404,hint="Not Found",response="Requested app doesn't exist",extra="This server is case sensitive. Make sure the requested app name is in the correct case")
class BadContentLengthError(APIError):
	def __init__(self,message="Bad Content-Length given in header"):
		APIError.__init__(self,message=message,code=400,hint="Bad Request",response="Bad Content-Length given in header")
class BadContentTypeError(APIError):
	def __init__(self,message="Bad/Unrecognized Content-Type header given"):
		APIError.__init__(self,message=message,code=400,hint="Bad Request",response="A bad or unrecognized MIME type was passed in the Content-Type header")
class ClientTimeoutError(APIError):
	def __init__(self,message="Client timedout"):
		APIError.__init__(self,message=message,code=408,hint="Request Timeout",response="Server was waiting too long",extra="The client most likely took too long to send it's full message")
class HTTPParsingError(APIError):
	def __init__(self,message="(Generic) Failed to parse HTTP request"):
		APIError.__init__(self,message=message,code=500,hint="Internal Error",response="Failed to parse HTTP request")
class MissingAppError(APIError):
	def __init__(self,message="No app was given by client"):
		APIError.__init__(self,message=message,code=404,hint="Not Found",response="No app was requested",extra="Ensure the requested path follows: 'http://url:port/api/target_app/target_action'")
class MissingActionError(APIError):
	def __init__(self,message="No action was given by client"):
		APIError.__init__(self,message=message,code=404,hint="Not Found",response="No action was requested",extra="Ensure the requested path follows: 'http://url:port/api/target_app/target_action'")
class RequestMethodError(APIError):
	def __init__(self,message="Invalid/unsupported request method given"):
		APIError.__init__(self,message=message,code=501,hint="Not Implemented",response="Request method not supported")


#---------------#
#    Testing    #
#---------------#
if __name__=="__main__":
	# raise APIPathError()

	try:
		raise APIPathError
	except Exception as e:
		print(e)
