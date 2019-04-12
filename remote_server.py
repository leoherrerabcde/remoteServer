
import sys
import requests
import socket
import os
import argparse
import json

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
		strValue = frame[pos_ini:]
	else:
		strValue = frame[pos_ini:pos_end]
		
	strpos = "Ini: " + str(pos_ini) + " End:" + str(pos_end)
	print strpos
	return strValue
	
def getFrameType(frame):
	frameType = getValueFromMsg(frame, "Header")
	return frameType

def makeAliveMsgResponse(counter):
	msg = "<Header:AliveMessage,AliveCounter:"
	msg += str(counter)
	msg += ">"
	return msg
	
def makePostMsgResponse(txt):
	msg = "<Header:RestService,method:post,body:"
	msg += txt
	msg += ">"
	return msg
	
def makeGetMsgResponse(data):
	msg = "<Header:RestService,method:get,body:"
	msg += data
	msg += ">"
	return msg	

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

msg = "<DeviceName:RestService,ServicePID:"
msg += str(os.getpid())
msg += ">"

print "Sending: %s" %(msg)
print

s.send(msg)

print "the socket has successfully connected on port == %s" %(host_ip)

bufferIn = ""

while True:
	print "Waiting for data..."
	data =s.recv(4096)
	if data == "":
		break
	print "Received data."
	bufferIn += data
	#print bufferIn[0,30]
	#print "..."
	#print bufferIn[-30,]
	while True:
		pos_ini = bufferIn.find("<")
		if pos_ini < 0:
			bufferIn = ""
			print "Socket Disconnection"
			break;
		else:
			pos_end = bufferIn.find(">")
			strpos = "Ini: " + str(pos_ini) + " End:" + str(pos_end)
			print strpos
			if pos_end > pos_ini:
				frame = bufferIn[pos_ini+1:pos_end]
				bufferIn = bufferIn[:pos_ini]
				#print "Frame: " 
				#print frame
				frame_type = getFrameType(frame)
				print "Frame Type: %s" %(frame_type)
				if frame_type == "AliveMessage":
					counter = getValueFromMsg(frame, "AliveCounter")
					print "Counter:"
					print counter
					counterPlusOne = int(counter)+1
					msg = makeAliveMsgResponse(counterPlusOne)
					print "Sending Alive Message: %s" %(msg)
					s.send(msg)
				elif frame_type == "RestService":
					bufferIn = bufferIn[pos_end+1:]
					url = getValueFromMsg(frame,"url")
					method = getValueFromMsg(frame,"method")
					body = getValueFromMsg(frame,"body")
					body_rec = body[:100]
					body_rec += " ... "
					body_rec += body[:-30]
					print "url : %s" %(url)
					print "method : %s" %(method)
					print "body : %s" %(body_rec)
					if method == "get":
						print "Sending get request. Waiting response."
						r = requests.get(url, params = body)
						if r.status_code == requests.codes.ok:
							msg = makeGetMsgResponse(json.dumps(r.json()))
							s.send(msg)
					elif method == "post":
						print "Sending post request. Waiting response."
						r = requests.post(url, data = body)
						msg = makePostMsgResponse(r.status_code)
						s.send(msg)
					print "Response sent."
		break

print "Application Closed Normally"
