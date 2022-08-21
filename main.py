#!/usr/bin/python3
import socket,queue,os,ssl,signal
import globe,apps,parsing
from clients import Client

#Do not touch >:(
all_threads=[]

def main():
	#Setup server socket
	print(f"[|X:main]: Setting up server socket")
	serv=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	serv.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
	serv.bind((globe.SERV_IP,globe.SERV_PORT))
	serv.settimeout(globe.SERV_TIMEOUT)

	#Check if both CERT_PATH and KEY_PATH are enabled, and wrap the server socket in TLS if they are
	if globe.CERT_PATH and globe.KEY_PATH:
		print(f"[|X:main:TLS]: Wrapping sockets in TLS")
		print(f"[|X:main:TLS]: Certificate: {globe.CERT_PATH}")
		print(f"[|X:main:TLS]: Key: {globe.KEY_PATH}")
		#Create tls socket context
		tlscontext=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
		tlscontext.load_cert_chain(globe.CERT_PATH,globe.KEY_PATH)

		serv=tlscontext.wrap_socket(serv,server_side=True)

	#Setup thread listeners
	print(f"[|X:main]: Setting up thread handlers")
	for t in range(globe.THREAD_COUNT):
		all_threads.append(Client(t))
		all_threads[-1].start()

	#Look for apps in the current directory
	#This will update the global dict
	sigHandle_updateApps(sig_message=False)

	#Register sigalarm to update apps
	signal.signal(signal.SIGALRM,sigHandle_updateApps)


	#Start listening
	print(f"[|X:main]: Starting to listen on {globe.SERV_IP}:{globe.SERV_PORT}")
	serv.listen()

	while True:
		#A lot of TLS errors can hallen here, so we'll need to catch them all here
		try:
			new_client=serv.accept()
		except (TimeoutError,socket.timeout):
			continue
		#TLS exceptions
		#It seems like they are all caught by ssl.SSLError, and from what I can tell there are very few (if any) cases where the error is server side, so we can just close off the error and let the client figure it out :)
		except ssl.SSLError as e:
			print(f"[|X:main:TLS:error]: {e}")
			continue

		print(f"[|X:main]: Accepted {new_client}")
		Client.addClient(new_client)


#Note: This doesn't work unless the updated action is renamed
def sigHandle_updateApps(sig=None,frame=None,sig_message=True):
	'''Re-initialize all apps in globe.ALL_APPS'''
	if sig_message:
		print(f"[|X:main:sigHandle_updateApps]: SIGALRM caught! Reinitializing all apps")

	#Read the Apps/disabled file and ignore those apps

	disabled=parsing.disabledList() #1=apps,2=methods,3=actions
	print(f"[|X:main:sigHandle_updateApps:disabled]: {disabled}")

	for a in os.listdir("./Apps"):
		if os.path.isdir(f"./Apps/{a}") and a not in disabled["apps"]:
			globe.ALL_APPS[a]=apps.App(a,disabled_list=disabled)

	print("[|X:main]: Loaded apps:")
	for a in globe.ALL_APPS.values():
		print(str(a).replace('\n','\n  '))

if __name__=="__main__":
	try:
		main()
	except KeyboardInterrupt:
		print("\r\033[K")
