## This holds all global/config values
import os

'''-------------#
#    main.py    #
#-------------'''
#Important!
SERV_IP="0.0.0.0"
SERV_PORT=8080

#Not as important!
# SERV_TIMEOUT=60  #Seconds
SERV_TIMEOUT=60  #Seconds
CLI_TIMEOUT=1  #Seconds
CLI_BLOCKING=True
THREAD_COUNT=5

'''----------------#
#    clients.py    #
#----------------'''
# SUPPORTED_METHODS=["GET","POST"]
#The line below has more methods
SUPPORTED_METHODS=["GET","POST","PUT","PATCH","DELETE"]

'''---------#
#    TLS    #
#---------'''
CERT_PATH="./TLSCerts/cert.pem"
#CERT_PATH=None
KEY_PATH="./TLSCerts/priv.key"
#KEY_PATH=None



#-----------------#
#    Constants    #
#-----------------#
#Do not touch!
FULL_PATH=os.getcwd()
HTTP_VERSION="HTTP/1.1"

#------------#
#    Apps    #
#------------#
#Do not touch!
ALL_APPS={}  #List of all apps
