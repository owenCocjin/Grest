## This file holds all authentication methods
import re,base64,sqlite3
import parsing,reply

class Auth():
	'''Specific criteria are required if using a database to authenticate.
	Below is a list of the table names/column names & types that are required by which auth methods:

	Table: [tokens]
	  Cols: | token BLOB |
	Required by:
	  - bearer

	Table: [auth]
	  Cols: | username VARCHAR | password VARCHAR |
	Required by:
	  - basic
	'''
	invalid_chars=['-',' ',"'",'"','/',',']

	def __init__(self,request_headers,*,db_path:str=None,return_cols:list=['*']):
		self.request_headers=request_headers
		self.db_path=db_path
		self.return_cols=''
		#Convert return_cols to a valid SQL string
		for c in return_cols:
			for bad_c in Auth.invalid_chars:
				c=c.replace(bad_c,'')
			self.return_cols+=f"""{c},"""
		self.return_cols=self.return_cols[:-1]

		self.return_data=None

		#Try connecting to given database
		if self.db_path:  #Try authenticating with the given db
			print(f"[|X:parsing:Auth]: Connecting to db: {self.db_path}")

			#Connect to DB
			self.db=sqlite3.connect(self.db_path)
			self.curse=self.db.cursor()
		else:
			self.db=None
			self.curse=None

	def exec(self,query,data=(),fetchall=True):
		self.curse.execute(query,data)
		if fetchall:
			return self.curse.fetchall()


	#----------------------#
	#    Auth Functions    #
	#----------------------#
	def bearer(self):
		'''Returns a generic JSON response (given by reply.Ok.JSONResponse()/reply.Failed.JSONResponse())
		An OK indicates the authentication was successful.
		On success, "response" in the return will be the raw data of the query, or the base64 decoded auth if applicable.
		Note: When authenticating against a database, the client's given token is kept as a bytes object, allowing for non-ASCII tokens. This means the token type in the database MUST be "BLOB"'''
		#Authenticate the user using the "Authorization" header
		auth=parsing.getFromDict_nocase("authorization",self.request_headers)
		if not auth:
			return reply.Failed.JSONResponse("Must authenticate user first")

		auth=auth.strip()

		#Check that the user's authentication is valid (make sure the token is in the auth db)
		try:
			#Check that the auth is formatted properly
			auth=re.fullmatch(b"^Bearer\s([0-9a-zA-Z\+\/\=]{4,})$",auth)

			if not auth:
				return reply.Failed.JSONResponse("Invalid auth headers format")

			auth=base64.b64decode(auth.group(1))  #Use groups to retrieve just the base64 encoded data
			print(f"[|X:parsing:Auth:bearer:auth]: {auth}")

			if self.db_path:
				#Try to fetch data from the given db_path
				self.return_data=self.exec(f"SELECT {self.return_cols} FROM tokens WHERE token=?",data=(auth,))

				if not self.return_data:  #No username was found
					return reply.Failed.JSONResponse("Failed to authenticate with given credentials")

				return reply.Ok.JSONResponse(self.return_data)
			else:
				return reply.Ok.JSONResponse(auth)

		except (UnicodeDecodeError,base64.binascii.Error) as e:
			return reply.Failed.JSONResponse("Failed to authenticate with given credentials",extra=str(e))

	def basic(self):
		'''Returns a generic JSON response (given by reply.Ok.JSONResponse()/reply.Failed.JSONResponse())
		An OK indicates the authentication was successful.
		On success, "response" in the return will be the raw data of the query, or the base64 decoded auth if applicable (user:pass).'''
		#Authenticate the user using the "Authorization" header
		auth=parsing.getFromDict_nocase("authorization",self.request_headers)
		if not auth:
			return reply.Failed.JSONResponse("Must authenticate user first")

		auth=auth.strip()

		#Check that the user's authentication is valid (make sure the token is in the auth db)
		try:
			#Check that the auth is formatted properly
			auth=re.fullmatch(b"^Basic\s([0-9a-zA-Z\+\/\=]{4,})$",auth)

			if not auth:
				return reply.Failed.JSONResponse("Invalid auth headers format")

			auth=base64.b64decode(auth.group(1)).decode().strip()  #Use groups to retrieve just the base64 encoded data
			delimpos=auth.find(':')
			username=auth[:delimpos]
			password=auth[delimpos+1:]

			print(f"[|X:parsing:Auth:basic:username]: {username}")
			print(f"[|X:parsing:Auth:basic:password]: {password}")

			if self.db_path:
				#Try to fetch data from the given db_path
				self.return_data=self.exec(f"SELECT {self.return_cols} FROM auth WHERE username=? AND password=?",data=(username,password))

				if not self.return_data:  #No username was found
					return reply.Failed.JSONResponse("Failed to authenticate with given credentials")

				return reply.Ok.JSONResponse(self.return_data)
			else:
				return reply.Ok.JSONResponse(auth)

		except (UnicodeDecodeError) as e:
			return reply.Failed.JSONResponse("Failed to authenticate with given credentials",extra=str(e))
