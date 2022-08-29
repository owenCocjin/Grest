## This file holds everything related to parsing data
import re,sqlite3,base64,json,random
import globe
from conn import genericOK,genericFailed

content_type={}  #This will be a dict of {content-type header val: func}

name_generation={}  #This will hold all the methods to generate names
rand_len=(16,32)
rand_charset="qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM0123456789_"
rand_hex_len=(16,32)
rand_hex_charset="abcdef0123456789"

def decodeURLEncoding(d):
	'''Returns a bytes object of URL decoded data.
	Returns None on failure'''
	to_ret=b''

	#Decode 'd' to a str if it's encoded (should be decodeable)
	d=d.decode() if type(d)==bytes else d

	#Manually create an iterator so we can manually skip characters
	looper=iter(d)

	#Go through one character at a time, and if it's a '%', interpret the next 2 chars as hex
	try:
		for b in looper:
			if b=='%':
				#Get next 2 bytes, convert to hex, and add to to_ret
				manual_byte=f"{next(looper,None)}{next(looper,None)}"
				# print(manual_byte)
				to_ret+=bytes.fromhex(manual_byte)
			else:
				to_ret+=b.encode()
	except ValueError:
		return None

	return to_ret

def getFromDict_nocase(t,d):
	'''Return a value from a dictionary (d) where the key and target (t) are case insensitive.
	Return None is nothing is found'''
	t=t.lower()

	for k,v in d.items():
		if k.lower()==t:
			return v
	return None

def httpHeaders(req):
	'''Go through "req" and parse it as an HTTP request.
	"req" is a bytes object.
	Returns a tuple: (dict,bytes), where:
	Dict of all the headers: {str:bytes}.
	Bytes of any data sent in the body'''
	to_ret_dict={}

	req=[l.strip() for l in req.split(b'\n')]  #Remove trailing spaces

	#Assume first line is the header, and pass it through a regex check
	req[0]=req[0].decode()

	if not re.fullmatch(f"({'|'.join(globe.SUPPORTED_METHODS)})\s(/.*)+\sHTTP/1.[1-2]",req[0]):
		print(f"[|X:parsing:httpRequest]: Received bad HTTP request header")
		raise globe.HTTPParsingError("Received bad/unsupported HTTP request (header)")

	#Separate request type, path, and version
	reqheader=req[0].split(' ')
	to_ret_dict["req_method"]=reqheader[0]
	to_ret_dict["req_path"]=reqheader[1]
	to_ret_dict["req_version"]=reqheader[2]

	#Go through the rest of the header and create a dict using the headers
	for h in req[1:]:
		delim=h.find(b':')
		to_ret_dict[h[:delim].decode().strip()]=h[delim+1:].strip()

	return to_ret_dict

def postFormURLDecode(d:bytes,urldecode=False):
	'''Convert application/x-www-form-urlencoded POST data to a dict.
	If "urldecode" is True, decode each dict item into a bytes object
	Returns a dict: {str:str(possibly urlencoded)}
	Returns None on failure'''
	to_ret={}

	try:
		data=d.split(b'&')
		for d in data:
			k,v=d.split(b'=')
			to_ret[k.decode()]=decodeURLEncoding(v) if urldecode else v.decode()

	except UnicodeDecodeError as e:
		return None

	return to_ret

def postFormData(d:bytes,h:str):
	'''Parses multipart/form-data data and returns a dict of all values found within it.
	d is the POST data
	h is the Content-Type header data (any data after the first ';' in the header).
	Returns None on error'''
	print(f"[|X:parsing:postFormData:d]: {d}")
	print(f"[|X:parsing:postFormData:h]: {h}")
	#Split by boundary (which should be defined in the header data)
	if "boundary" not in h:
		return None
	boundary_data=d.split(f"""--{h["boundary"]}""".encode())  #Have to encode because this is all bytes data
	print(f"[|X:parsing:postFormData:boundary_data]: {boundary_data}")

	return None

#-------------------------------#
#    Content-Type Processing    #
#-------------------------------#
#To add more MIME types, follow the existing examples in the "content_type" variable under the classes
class MIMEType():
	def __init__(self,name,subtypes):
		self.name=name
		self.subtypes={s.name:s for s in subtypes}

	def __getitem__(self,s):
		return self.subtypes[s]

class MIMESubtype():
	def __init__(self,name,processing_func,takes_args=False):
		'''name is the subtype name.
		processing_func is the function that processes the data of this subtype.
		takes_args if True, will allow the client to pass the Content-Type params (as a dict) to self.processing_func'''
		self.name=name
		self.processing_func=processing_func
		self.takes_args=takes_args
	def __call__(self,*args,**kwargs):
		return self.processing_func(*args,**kwargs)

#Add new MIME types here
content_type={
	"application":MIMEType("application",[
		MIMESubtype("x-www-form-urlencoded",postFormURLDecode,False),
		MIMESubtype("json",json.loads,False)
		]
	),
	"multipart":MIMEType("multipart",[
		MIMESubtype("form-data",postFormData,True)
		]
	)
}


#--------------#
#    Custom    #
#--------------#
def disabledList():
	'''Go through the "disabled" file and add each line to it's respective list'''
	disabled_apps=[]
	disabled_methods=[]
	disabled_actions=[]

	try:
		with open("./Apps/disabled",'r') as f:
			for line in f.readlines():
				#Skip empty lines and commented lines
				line=line.strip()
				if not line or line[0]=='#':
					continue

				#If there are any periods in the line, split by that.
				#We can then leverage the fact that once split, there will be 1 item for an app, 2 for a method, and 3 for an action
				line=line.split('.')
				if len(line)==1:
					disabled_apps+=line  #Don't append so we don't create a 2d list
				elif len(line)==2:
					disabled_methods.append(line)
				elif len(line)==3:
					disabled_actions.append(line)
	except FileNotFoundError:
		pass

	return {"apps":disabled_apps,
			"methods":disabled_methods,
			"actions":disabled_actions}

def generateRandomName(name,hex=False):
	'''Parse the random name (for lengths) and return a random string name.
	Return None on failures
	Uses hex charset if hex==True'''
	charset=rand_charset if not hex else rand_hex_charset
	name=name[1:].strip()
	name_len_range=rand_len

	# print(f"name: {name}")

	#If there's just a star, just generate a random name
	if name!='':
		#Extract the numbers, if they exist
		try:
			name_len_range=(*[int(i) for i in name.split('-')],)  #Convert to a set just because
			# print(f"name_len_range: {name_len_range}")

			#Error checking
			if name_len_range[0]==0:  #Can't allow this
				return None

			#Process data
			if len(name_len_range)==1 or name_len_range[1]=='':  #Set target_len to range_low
				name_len_range=name_len_range*2  #Essentially jsut use the 1 number
			elif name_len_range[0]>name_len_range[1]:  #Swap around so they're in order
				name_len_range=name_len_range[::-1]

		except ValueError:
			#Can't continue with this
			return None

	#Generate the name and return it
	return ''.join(random.choices(charset,k=random.randint(*name_len_range)))

def generateRandomHexName(name):
	'''Uses generateRandomName() function with hex==True'''
	return generateRandomName(name,hex=True)


	#-----------------------#
	#    Name Generation    #
	#-----------------------#
name_generation['*']=generateRandomName
name_generation['&']=generateRandomHexName


#---------------#
#    Testing    #
#---------------#
if __name__=="__main__":
	print("Good:")
	print(generateRandomHexName('*'))
	print(generateRandomHexName('*5'))
	print(generateRandomHexName('*5-10'))
	print("Bad:")
	print(generateRandomHexName('*a'))
	print(generateRandomHexName('*0'))
	print(generateRandomHexName('*10-4'))
	print(generateRandomHexName('*-10'))
	print(generateRandomHexName('*5-s'))

	# print("decodeURLEncoding")
	# print("Good: ")
	# print(decodeURLEncoding(b"Hello%20there"))
	# print(decodeURLEncoding(b"Hello%20there%21"))
	# print("Bad: ")
	# print(decodeURLEncoding(b"Hello%2!there"))
	# print(decodeURLEncoding(b"Hello%20there%"))
	#
	# print("postFormURLDecode: ")
	# print("Good: ")
	# print(postFormURLDecode(b"key=value&something=else"))
	# print(postFormURLDecode(b"key=value&something=else%20here%00",urldecode=True))
	# print("Bad: ")
