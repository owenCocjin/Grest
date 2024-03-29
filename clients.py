## This file holds anything related to clients
import threading,json
from queue import Queue
import parsing,conn,globe
from errors import *

class Client(threading.Thread):
	'''"queue" is the client queue that these handlers will grab from.'''
	queue=Queue()

	@classmethod
	def addClient(cls,cli):
		'''"cli" is the tuple returned from socket.accept()'''
		cls.queue.put(cli)
		return cli

	def __init__(self,id):
		'''"id" is a generic UID'''
		threading.Thread.__init__(self,daemon=True)
		self.id=id
		self.cli=None
		self.cli_addr=None

	def run(self):
		'''Get the next client from the queue (blocking) and process it's request'''
		print(f"[|X:clients:Client]: Starting Client({self.id})")

		while True:
			self.cli,self.cli_addr=Client.queue.get()
			print(f"[|X:clients:Client]: Received client {self.cli_addr}")

			#Set client's values
			self.cli.setblocking(globe.CLI_BLOCKING)
			self.cli.settimeout(globe.CLI_TIMEOUT)

			#Get bytes from client
			#Try to get until \r\n\r\n, timeout otherwise
			try:
				recv_data=conn.getWindow(self.cli)
			except TimeoutError as e:
				print(f"[|X]:clients:Client]: {e}")
				#Unfortunately, I need to do sone janky shit here to use closeCli()
				e=ClientTimeoutError()
				e.closeCli(self.cli)
				continue

			print(f"[|X:clients:Client:recv_data]: {recv_data}")

			try:
				req_headers=parsing.httpHeaders(recv_data)
				req_data=None  #Clear here, somewhat arbitrary placement
			except HTTPParsingError as e:
				print(f"[|X]:clients:Client:error]: {e}")
				e.closeCli(self.cli)
				continue

			#If there is a Content-Length header, assume there is more data to be pulled from the client (it will be exactly that many bytes)
			bytes_to_pull=parsing.getFromDict_nocase("content-length",req_headers)
			if bytes_to_pull:
				try:
					req_data=self.cli.recv(int(bytes_to_pull))
				except TimeoutError as e:
					print(f"[|X:clients:Client]: {e}")
					e=ClientTimeoutError()
					e.closeCli(self.cli)
					continue
				except ValueError as e:
					print(f"[|X:clients:Client]: {e}")
					e=BadContentLengthError()
					e.closeCli(self.cli)
					continue

			#If there's a "content-type" header we will parse req_data as specified in the header
			try:
				content_type=parsing.getFromDict_nocase("content-type",req_headers)
				if content_type:
					req_data=parsing.content_type[content_type](req_data)
			except Exception as e:
				print(f"[|X:clients:Client]: Failed to parse the data with given content type: {e}")
				pass

			#Process the request and get the calling action
			try:
				results=self.determineAction(req_headers,req_data)  #This should return the conn.Reply + subclasses

				print(f"[|X:clients:Client:action data]: {results}")

				#Package the results (which should be a JSON string) into a proper HTTP message and send it off
				#To add: if results is a failure, it should NOT return a 200 OK
				self.cli.send(results.bytes())

			except APIError as e:
				print(f"[|X:clients:Client:{e.__class__.__name__}]: {e}")
				e.closeCli(self.cli)
				continue

			self.cli.close()

	def determineAction(self,request_headers,request_data):
		'''Determine what to do based on the type of request and the request path'''
		print(f"[|X:clients:Client:determineAction]: {request_headers['req_path']}")
		if not request_headers["req_path"].startswith(f"/{globe.API_PATH_TITLE}/"):
			raise APIPathError

		#Get the name of the requested app
		req_path=request_headers["req_path"].strip('/').split('/')  #Remove '/' from start/end

		#The second item in req_path should be the app name
		if len(req_path)<2:  #Missing app
			raise MissingAppError
		# elif len(req_path)<3:
		# 	raise MissingActionError


		#Renamed for simplicity
		req_app=req_path[1]
		req_action=req_path[2] if len(req_path)>=3 else 'base'
		req_method=request_headers["req_method"]
		url_args={}

		#Look for a question mark in the last item in req_path. If there is then there are url args in the request
		if '?' in req_path[-1]:
			#Get the position of the first '?' and isolate everything after that
			delimpos=req_path[-1].find('?')
			urlargs=req_path[-1][delimpos+1:]

			#Reset the req_action to the string before the delimiting '?'
			if req_action==req_path[-1]:
				req_action=req_action[:delimpos]

			#Try to delimit by ampersand
			urlargs=urlargs.split('&')

			print(f"[|X:clients:Clients:urlargs] {urlargs}")

			#Split each item by equal sign then add to a dict
			#If there are multiple equal signs then we will only use the first 2 values.
			#Everything else will be ignored
			for a in urlargs:
				delimpos=a.find('=')
				a=(a,None) if delimpos==-1 else (a[:delimpos],a[delimpos+1:])

				url_args[a[0]]=a[1] if len(a)>1 else None

		#Do more checks
		try:
			req_app_obj=globe.ALL_APPS[req_app]
		except KeyError:
			raise AppDoesntExistError

		if not req_app_obj.hasMethod(req_method):
			raise RequestMethodError
		#If action is missing/doesn't exist but there is a base action, return the base action instead
		elif req_app_obj.hasBaseAction(req_method) and \
			(req_action=="base" or \
				(req_app_obj.baseAcceptsInput(req_method) and not req_app_obj.hasAction(req_method,req_action))):
			if req_action=="base":
				return req_app_obj[req_method]._base_action(request_headers,request_data,url_args)
			else:
				return req_app_obj[req_method]._base_action(request_headers,request_data,url_args,base_input=req_action)

		elif not req_app_obj.hasAction(req_method,req_action):
			raise ActionDoesntExistError

		#Done parsing, execute the action and return it's data!
		return req_app_obj[req_method][req_action](request_headers,request_data,url_args)
