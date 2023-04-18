## This file holds the Reply class and any subclasses
'''To create custom reply classes, you can either add them here at the bottom, or import the "Reply" class into another file.
See the Ok and Failed classes for examples'''
import json
import globe

#---------------------#
#    Reply Classes    #
#---------------------#
class Reply():
	'''This is the base class for all actions to reply with
	I want the class to be able to add content length header if data exists and add_length is True.
	I'd like this class to be able to parse the data based on given Content-Length header (ex. If "application/json" header exists, parse the given data using "json.dumps()")'''
	def __init__(self,data,headers,status_code,hint,converter=lambda d: str(d).encode()):
		self.data=data  #Doesn't have to be a string, as long as it is convertable by the "converter" function
		self.headers=headers
		self.status_code=status_code
		self.hint=hint
		self.converter=converter  #This is a function that is used to convert the data to a string

	def __str__(self):
		'''Just decode self.bytes() if isascii, else return it as a string'''
		to_ret=self.bytes()
		return str(to_ret)[2:-1] if not to_ret.isascii() else to_ret.decode()

	def bytes(self):
		'''Convert everything into a nice HTTP reply'''
		to_ret=f"""{globe.HTTP_VERSION} {self.status_code} {self.hint}\r\n""".encode()

		#Add headers
		for h in self.headers:
			to_ret+=f"""{h}\r\n""".encode()

		#If there's data, convert to bytes via self.converter() and add the length as a header
		if self.data:
			databytes=self.converter(self.data)

			to_ret+=f"""Content-Length: {len(databytes)}\r\n\r\n""".encode()
			to_ret+=databytes

		return to_ret

	def addHeaders(self,h):
		'''Add a header to self.headers.
		"h" can be a string representing the header, or a list of headers'''
		if type(h)==list:
			self.headers+=h
		elif type(h)==str:
			self.headers.append(h)
		else:  #Throw error
			raise TypeError("h is neither a list or string")

	def getHTTPReply(self):
		'''Just return self.__str__ if for some reason we can't just call it'''
		return self.__str__()

class Ok(Reply):
	'''This is a default Ok reply'''
	@classmethod
	def JSONResponse(cls,response="Good",**kwargs):
		'''Convert from response to JSON. Returns an Ok object'''
		to_ret={"status":"OK","response":response}
		if kwargs:
			to_ret.update(kwargs)
		return cls(data=json.dumps(to_ret))

	def __init__(self,data=None,headers=None,status_code=200,hint="OK"):
		self.data={"status":"OK","response":"Good"} if not data else data
		self.headers=["Content-Type: application/json"] if not headers else headers
		Reply.__init__(self,self.data,self.headers,status_code,hint)

	# def JSONResponse(self,response="Good",**kwargs):
	# 	'''Convert from response to JSON. Returns a Failed object'''
	# 	self.converter=lambda d:json.dumps(d).encode()
	# 	self.data={"status":"Failed","response":response}
	# 	if kwargs:
	# 		self.data.update(kwargs)

class Failed(Reply):
	'''This is a default Failed reply'''
	@classmethod
	def JSONResponse(cls,response="Bad",**kwargs):
		'''Convert from response to JSON. Returns a Failed object'''
		to_ret={"status":"Failed","response":response}
		if kwargs:
			to_ret.update(kwargs)
		return cls(data=json.dumps(to_ret))

	def __init__(self,data=None,headers=None,status_code=500,hint="Internal Server Error"):
		self.data={"status":"Failed","response":"Bad"} if not data else data
		self.headers=["Content-Type: application/json"] if not headers else headers
		Reply.__init__(self,self.data,self.headers,status_code,hint)

	# def JSONResponse(self,response="Bad",**kwargs):
	# 	'''Convert from response to JSON. Returns a Failed object'''
	# 	self.converter=lambda d:json.dumps(d).encode()
	# 	self.data={"status":"Failed","response":response}
	# 	if kwargs:
	# 		self.data.update(kwargs)

		print(f"[|x:reply:Failed:JSONResponse:data]: {self.data}")
		return self




if __name__=="__main__":
	print(Ok.JSONResponse("Good job!"))
