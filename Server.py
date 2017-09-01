from socket import *
import sys
import os
import threading
import shlex

HOST = ''
PORT = 7734

peerList = []
RFCIndexList = []

class Currently_active_Peer:
	def __init__(self,hostname='None',uploadport='NONE'):
		self.hostname = hostname
		self.uploadport = uploadport

	def __str__(self):
		return 'Hostname : ' + str(self.hostname) +' with uploadPort as ' + str(self.uploadport) 

class RFC_Index_node:
	def __init__(self,RFCnumber = 'NONE',title = 'NONE',HostnamePeer = 'NONE',uploadport = 'NONE'):
		self.RFCnumber = RFCnumber
		self.title = title
		self.HostnamePeer = HostnamePeer
		self.uploadport = uploadport

	def __str__(self):
		return 'RFC '+str(self.RFCnumber)+' '+str(self.title)+' '+str(self.HostnamePeer)+' '+str(self.uploadport)

def clientThreadHandler(clientSocket,clientAddress):
	try:

		while True:
			response = clientSocket.recv(1024)
			if len(response) == 0:
				clientSocket.close()
				return
			i =0
			for i in xrange(len(response)):
				if response[i] == '!':
					break
			output = '-----------------------------------------------------------\nThe Client has requested the following:\n'
			new_response = response[:i]
			output = output + response[:i]

			print output + '\n----------------------------------------------------\n'
			dict_msg = shlex.split(new_response)
			if dict_msg[0] == 'ADD':
				addRFC(new_response,clientSocket)
			elif dict_msg[0] == 'LIST':
				List(new_response, clientSocket)
			elif dict_msg[0] == 'LOOKUP':
				lookUp(new_response,clientSocket)
			elif dict_msg[0] == 'DEL':
				deletePeer(new_response,clientSocket)
	except KeyboardInterrupt:
		serversocket.close()
		sys.exit(0)

def make_msg_long(msg):
	iterator = 1024 - len(msg)
	while iterator > 0:
		msg = msg + '!'
		iterator =iterator -1
	return msg

def addRFC(response,clientSocket):
	dict_msg = shlex.split(response)
	Rfcnumber = dict_msg[2]
	Hostname = dict_msg[5]
	Uploadport = dict_msg[7]
	title1= dict_msg[9:]
	title = ' '.join(title1)

	addPeer = Currently_active_Peer(Hostname, Uploadport)
	peerList.append(addPeer)
	addRfc = RFC_Index_node(Rfcnumber,title,Hostname, Uploadport)
	RFCIndexList.append(addRfc)
	msg = 'RFC '+str(Rfcnumber)+' '+str(title)+' '+str(Hostname)+' '+str(Uploadport)
	msg = 'P2P-CI/1.0 200 OK\n' + str(msg)
	new_msg = make_msg_long(msg)
	clientSocket.send(new_msg)
	return 0

def List(response,clientSocket):
	code = 0
	status = ''
	rfclist = []
	if len(RFCIndexList) == 0:
		message = 'P2P-CI/1.0 404 NOT FOUND'
		new_message = make_msg_long(message) 
		clientSocket.send(new_message) 
	else:
		counter =0
		message = 'P2P-CI/1.0 200 OK \n'
		for rfc in RFCIndexList:
			if not (rfc.HostnamePeer == None and rfc.uploadport == None) :
				counter +=1
				message = message + str(rfc)+ '\n'
		if counter >0 :
			new_message = make_msg_long(message)
			clientSocket.send(new_message)
		elif counter ==0:
			message = 'P2P-CI/1.0 404 NOT FOUND'
			new_message = make_msg_long(message)
			clientSocket.send(new_message)
		counter =0
	return 0

def lookUp(response,clientSocket):
	dict_msg = shlex.split(response)
	number = dict_msg[2]
	title1= dict_msg[9:]
	Title = ' '.join(title1)
	count =0
	msg = ''
	for i in RFCIndexList:
		if i.RFCnumber == number and i.title == Title and i.HostnamePeer !=None:
			count +=1
			if count ==1:
				msg = 'P2P-CI/1.0 200 OK\n'
			msg = msg + 'RFC '+str(i.RFCnumber)+' '+str(i.title)+' '+str(i.HostnamePeer)+' '+str(i.uploadport)
	if count > 0:
		new_msg = make_msg_long(msg)
		clientSocket.send(new_msg)
	if count == 0:
		message = 'P2P-CI/1.0 404 NOT FOUND'
		new_message = make_msg_long(message)
		clientSocket.send(new_message)

def deletePeer(response,clientSocket):
	dict_msg = shlex.split(response)
	Hostname = dict_msg[4]
	Uploadport = dict_msg[6]
	#temp =[]
	for i in RFCIndexList:
		#print i
		if i.HostnamePeer == Hostname and i.uploadport == Uploadport:
			i.HostnamePeer = None
			i.uploadport = None
		#print i

	for i in peerList:
		if i.hostname == Hostname and i.uploadport == Uploadport:
			i.hostname = None
			i.uploadport = None

	#RFCIndexList = RFCIndexList - temp
	message = 'P2P-CI/1.0 200 OK \n'
	new_message = make_msg_long(message)
	clientSocket.send(new_message)

def main():
	serversocket = socket(AF_INET, SOCK_STREAM)
	print '.............................................'
	print 'Server Socket Created'
	try:
		serversocket.bind((HOST,PORT))
	except error, msg:
		print 'Bind failed. Error Code: ' + str(msg[0]) + ' Message ' + str(msg[1])
		sys.exit()
	try:
		while True:
			serversocket.listen(10)
			print '............................................'
			#print 'Waiting for a client to connect\n'
			(conn,addr) = serversocket.accept()
			#print '\nConnection accepted on port number : ',addr[1]
			#thread.start_new_thread(clientThreadHandler,(conn,addr))
			server_thread = threading.Thread(target = clientThreadHandler, args = (conn,addr))
			server_thread.start()
		serversocket.close()
	except KeyboardInterrupt:
		serversocket.close()
		sys.exit(0)


if __name__ == '__main__':
	main()
