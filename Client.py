from socket import *
import os
import threading
import shlex
import sys
from multiprocessing import Process
import time
import platform
import datetime

servername = 'localhost'
serverport = 7734
HOST =''
hostname = ''
uploadport = '8282'

class RFC_Index_node:
	def __init__(self,RFCnumber = 'NONE',title = 'NONE',HostnamePeer = 'NONE',uploadport = 'NONE'):
		self.RFCnumber = RFCnumber
		self.title = title
		self.HostnamePeer = HostnamePeer
		self.uploadport = uploadport

	def __str__(self):
		return 'RFC '+str(self.RFCnumber)+' '+str(self.title)+' '+str(self.HostnamePeer)+' '+str(self.uploadport)


def peerThreadHandler(peersocket,peeraddress):
	response = peersocket.recv(1024)
	print response
	
	dict_msg = shlex.split(response)
	filename = 'RFC'+dict_msg[2] +'.txt'
	cur_directory = os.getcwd()
	fileList = os.listdir(cur_directory)
	if filename in fileList:
		#print "Found the file in the IP directory"
		last_m_date = time.strftime("%a, %d %b %Y %H:%M:%S ",time.gmtime(os.path.getmtime(filename))) + 'GMT\n'
		OS = platform.system() + ' ' + platform.release()
		date_now = time.strftime("%a, %d %b %Y %H:%M:%S",time.gmtime()) + 'GMT\n'
		filesize = os.path.getsize(filename)
		msg = 'P2P-CI/1.0 200 OK\nDate: ' + str(date_now) +'\nOS: ' + str(OS) + '\nLast-Modified: ' + str(last_m_date) + '\nContent-Length: ' + str(filesize) + '\nContent-Type: text/text\n'   
		peersocket.sendall(msg)
		filefd = open(filename,"r")
		data =filefd.read(1024)
		while data:
			peersocket.send(data)
			data = filefd.read(1024)
		filefd.close()
		peersocket.close()
	else:
		#print 'RFC Not Found'
		peersocket.close()
	sys.exit(0)

def peer_download(downloadsocket,hostname):
	rfcnumber = raw_input('Enter the RFC number to be downloaded: ')
	#downloadsocket.send('Hello! I would like to make a connection with your server!!!!.....')
	#print downloadsocket.recv(1024) 
	msg = 'GET RFC ' + rfcnumber + ' P2P-CI/1.0\nHost: ' + str(hostname) + '\nOS: ' + platform.system() + ' ' + platform.release()
	downloadsocket.send(msg)
	data = downloadsocket.recv(1024)
	while data:
		print data
		data = downloadsocket.recv(1024)
	downloadsocket.close()
	print 'Enter your choice:'
	return 0


def peer_server():
	global uploadport
	#print '#############################################\n'
	#print threading.currentThread().getName(),'Starting'
	peersocket = socket(AF_INET,SOCK_STREAM)
	peer_ip =''
	peer_port = int(uploadport)
	try:
		peersocket.bind((peer_ip,peer_port))
	except error, msg:
		print 'Bind failed. Error Code: ' + str(msg[0]) + ' Message ' + str(msg[1])
		sys.exit()
	
	try:
		while True:
			peersocket.listen(1)
			(conn,addr) = peersocket.accept()
			print '\nConnection accepted on port number : ',addr[1]
			peer_thread = threading.Thread(target = peerThreadHandler, args = (conn,addr))
			peer_thread.start()
		peersocket.close()
	except KeyboardInterrupt:
		peersocket.close()
		sys.exit(0)
	return
def make_msg_long(msg):
	iterator = 1024 - len(msg)
	while iterator > 0:
		msg = msg + '!'
		iterator =iterator -1
	return msg

def addRFC(clientsocket,rfcnumber=None,rfctitle=None):
	global servername
	global hostname
	hostname = gethostname()
	if rfctitle == None:
		rfcnumber = raw_input('Enter the RFC number: ')
		rfctitle = raw_input('Enter the RFC title : ') 
	#msg = 'ADD RFC 123 P2P-CI/1.0\n HOST: thishost.csc.ncsu.edu\n Port: 5678\n Title: IPV6'
	msg = 'ADD RFC ' + str(rfcnumber) + ' P2P-CI/1.0\nHOST: ' + str(hostname) + '\nPort: ' + str(uploadport) + '\nTitle: ' + str(rfctitle)
	print msg
	msg_new = make_msg_long(msg)
	clientsocket.send(msg_new)
	response = clientsocket.recv(1024)
	#print '...................\n' + response
	#print 'Length of response:' + str(len(response))
	i =0
	for i in xrange(len(response)):
		if response[i] == '!':
			break
	new_response = response[:i]		
	#print 'REponse length : ' + str(len(response))
	print '......................\n' + str(new_response)
	return 0

def ListRFC(clientsocket):
	global servername
	global uploadport
	global hostname
	hostname = gethostname()
	msg = 'LIST ALL P2P-CI/1.0\nHOST: ' + str(hostname) + '\nPort: ' + str(uploadport) + '\n'
	#msg = 'LIST ALL P2P-CI/1.0\n HOST: thishost.csc.ncsu.edu\n Port: 5678'
	new_msg = make_msg_long(msg)
	clientsocket.send(new_msg)
	response = clientsocket.recv(1024)
	#print 'Response length Originally is : ' + str(len(response))
	i =0
	for i in xrange(len(response)):
		if response[i] == '!':
			break
	new_response = response[:i]		
#	print 'REponse length : ' + str(len(response))
	print '......................\n' + str(new_response)
	return 0
	#print '....................\n'+ response

def LookupRFC(clientsocket):
	global servername
	global uploadport
	global hostname
	hostname = gethostname()
	rfcnumber = raw_input('Enter the RFC number: ')
	rfctitle = raw_input('Enter the RFC title: ')
	msg = 'LOOKUP RFC ' + str(rfcnumber) + ' P2P-CI/1.0\nHost: ' + str(hostname) + '\nPort: ' + str(uploadport) + '\nTitle: ' + str(rfctitle)
	new_msg = make_msg_long(msg)
	#msg = 'LOOKUP RFC 3457 P2P-CI/1.0\nHost: thishost.csc.ncsu.edu\nPort: 5678\nTitle: IPSec'
	clientsocket.send(new_msg)
	response = clientsocket.recv(1024)
	print 'Response length Originally is : ' + str(len(response))
	i =0
	for i in xrange(len(response)):
		if response[i] == '!':
			break
	new_response = response[:i]		
#	print 'REponse length : ' + str(len(response))
	print '......................\n' + str(new_response)
	return 0
	#print '................\n'+response

def deletePeer(clientsocket):
	global servername
	global hostname
	hostname = gethostname()
	msg = 'DEL PEER P2P-CI/1.0\nHOST: ' + str(hostname) + '\nPort: ' + str(uploadport)
	new_msg = make_msg_long(msg)
	#print msg
	clientsocket.send(new_msg)
	response = clientsocket.recv(1024)
	i =0
	for i in xrange(len(response)):
		if response[i] == '!':
			break
	new_response = response[:i]		
	print '......................\n' + str(new_response)
	return 0

def menu():
	
	print '------------Menu------------------'
	print '1. Add RFC'
	print '2. List all RFCs'
	print '3. Lookup a particular RFC'
	print '4. Download from peer'
	print '5. Exit( Press Ctrl+Z after getting OK status)'

def connect_to_server():
	global uploadport
	global servername
	hostname = gethostname()
	servername = raw_input('Enter the Centralized server IP address: ')
	clientsocket = socket(AF_INET, SOCK_STREAM)
	clientsocket.connect((servername,serverport))
	addRFC(clientsocket,123,'A Proferred Official ICP')
	while True:
		menu()
		selection = raw_input('Enter your choice:')
		if selection == '1':
			addRFC(clientsocket)
		elif selection == '2':
			ListRFC(clientsocket)
		elif selection == '3':
			LookupRFC(clientsocket)
		elif selection == '4':
			downloadname = raw_input('Enter the hostname of the peer server: ')
			downloadport = raw_input('Enter the uploadport number of the peer: ')
			downloadsocket = socket(AF_INET, SOCK_STREAM)
			downloadsocket.connect((downloadname,int(downloadport)))
			peer_download(downloadsocket,downloadname)
			print 'Enter your choice:'
		elif selection == '5':
			deletePeer(clientsocket)
			break				
			#clientsocket.close()
			#sys.exit(0)
		else:
			print 'Wrong Selection, Please Enter number from 1-5'
	return	

def main():
	global uploadport
	lock = threading.Lock()
	uploadport = raw_input('Enter the upload port: ')
	try:
		
		peer_server_thread = threading.Thread(name = 'Peer_server_thread',target = peer_server)
		peer_server_thread.setDaemon(True)
		peer_server_thread.start()
		connect_server_thread = threading.Thread(name = 'server_connect_thread',target = connect_to_server)
		connect_server_thread.setDaemon(True)
		connect_server_thread.start()
		connect_server_thread.join()
		peer_server_thread.join()

	except KeyboardInterrupt:
		sys.exit(0)


if __name__ == '__main__':
	main()
