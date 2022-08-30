## This file holds all info related to socket connections
## Notes:
##    - Any function using tempSockModify() MUST use "sock" as a keyword, or have the socket passed as the first argument!
import globe,sqlite3

#---------------#
#    Classes    #
#---------------#
class Curse():
	'''Create a database class.
	Execute a query by calling an instance as a function'''
	def __init__(self,name,db_path):
		self.name=name
		self.db_path=db_path

		#Create curse
		self.conn=sqlite3.connect(self.db_path)
		self.curse=self.conn.cursor()
	def __call__(self,query,data=(),results=True):
		self.curse.execute(query,data)

		if results:
			return self.curse.fetchall()

	def commit(self):
		'''Commit to database'''
		self.conn.commit()


#-----------------#
#    Functions    #
#-----------------#
def getWindow(sock,window=b'\r\n\r\n'):
	'''Get until a specific byte sequence'''
	to_ret=b''

	#Loop while the next byte isn't empty, and while the window hasn't been met
	cur_byte=True
	while to_ret[-(len(window)):]!=window and cur_byte!=b'':
		cur_byte=sock.recv(1)
		to_ret+=cur_byte
		# print(to_ret,flush=True)
		# print(to_ret[-(len(window)):]==window)

	return to_ret
