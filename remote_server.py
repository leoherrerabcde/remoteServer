
import sys
import requests
import socket
import os
import argparse

def getValueFromMsg(frame,name):
	pos_ini = frame.find(name)
	if pos_ini < 0:
		return ""
	pos_end = frame.find(":", pos_ini+len(name))
	if pos_end <  pos_ini+len(name) :
		return ""
	label = frame[pos_ini:pos_end].strip()
	if label != name:
		return ""
	pos_ini = pos_end + 1
	pos_end = frame.find(",",pos_ini)
	if pos_end <= pos_ini:
		return ""
	strValue = frame[pos_ini,pos_end]
	return
	
def getFrameType(frame):
	frameType = getValueFromMsg(frame, "Header")
	return

def makeAliveMsgResponse(counter):
	msg = "<Header:AliveMessage,AliveCounter:"
	msg += str(counter)
	msg += ">"
	return
	
#parsing Command Line Arguments

parser = argparse.ArgumentParser()
parser.add_argument('--remote_port', type=int, required=True)
args = parser.parse_args()
remotePort = args.remote_port
#print(args.counter + 1)

url = "http://192.168.8.102:3000/api/areas"

print "Remote Server Initializing..."
#print url
#print

#r = requests.get(url)

#print "The get request response is:"
#print (r.text)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host_ip = socket.gethostbyname('127.0.0.1') 

print "Trying to connect to Host:%s:%s" %(host_ip,remotePort)

s.connect((host_ip, remotePort))

msg = "{DeviceName:RestService,ServicePID:"
msg += str(os.getpid())
msg += "}"

print "Sending: %s" %(msg)
print

s.send(msg)

print "the socket has successfully connected on port == %s" %(host_ip)

bufferIn = ""

while True:
	data =s.recv(1024)
	bufferIn += data
	while True:
		pos_ini = bufferIn.find("<")
		if pos_ini < 0:
			bufferIn = ""
			break;
		else:
			pos_end = bufferIn.find(">")
			if pos_end > pos_ini:
				frame = bufferIn[pos_ini+1, pos_end]
				frame_type = getFrameType(frame)
				if frame_type == "AliveMessage":
					counter = getValueFromMsg(frame, "AliveCounter")
					counter+=1
					msg = makeAliveMsgResponse(counter)
					s.send(msg)
				elif frame_type == "AliveMessage":
					bufferIn = bufferIn[pos_end+1:]
					url = getValueFromMsg(frame,"url")
					method = getValueFromMsg(frame,"method")
					body = getValueFromMsg(frame,"body")
					print "url : %s" %(url)
					print "method : %s" %(method)
					print "body : %s" %(body)
