
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
	
def getBodyFromMsg(frame,name):
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
	pos_ini = frame.find("|",pos_ini)
	if pos_ini < pos_end:
		print "Label:%s" %label
		strpos = "Ini: " + str(pos_ini) + " End:" + str(pos_end)
		print strpos
		print frame
		return ""
	pos_ini = pos_ini + 1
	pos_end = frame.find("|",pos_ini)
	#strpos = "Ini: " + str(pos_ini) + " End:" + str(pos_end)
	#print strpos
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
	msg += "|"
	msg += txt
	msg += "|"
	msg += ">"
	return msg
	
def makeGetMsgResponse(data):
	msg = "<Header:RestService,method:get,body:"
	msg += "|"
	msg += data
	msg += "|"
	msg += ">"
	print data[:20]
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
					print "url : %s" %(url)
					print "method : %s" %(method)
					#json_text = "[{'numero_registro':'1','fec_init_transac':'2019/02/07 00:48:50','id_dispensador':'01','id_bombero':'2119d67203c632','id_receptor':'11111','rfid_veh_receptor':'072017120600000072','valor_odometro':'0000','valor_horometro':'0000','tipo_transac':'7','flujometro_ini':'0','flujometro_fin':'0','fec_fin_transac':'2019/02/07 00:50:37','litros':'0'}]"
					json_text = [{"numero_registro":"1","fec_init_transac":"2019/02/07 00:48:50","id_dispensador":"01","id_bombero":"2119d67203c632","id_receptor":"11111","rfid_veh_receptor":"072017120600000072","valor_odometro":"0000","valor_horometro":"0000","tipo_transac":"7","flujometro_ini":"0","flujometro_fin":"0","fec_fin_transac":"2019/02/07 00:50:37","litros":"0"}]
					my_url = "http://157.230.225.248:3000/api/control"
					if method == "get":
						body = getValueFromMsg(frame,"body")
						body_rec = body[:100]
						body_rec += " ... "
						body_rec += body[:-30]
						print "body : %s" %(body_rec)
						print "Sending get request. Waiting response."
						r = requests.get(url, params = body)
						if r.status_code == requests.codes.ok:
							msg = makeGetMsgResponse(json.dumps(r.json()))
							s.send(msg)
							print "Response sent."
					elif method == "post":
						body = getBodyFromMsg(frame,"body")
						body_rec = body[:100]
						body_rec += " ... "
						body_rec += body[:-30]
						print "body : %s" %(body_rec)
						print body
						print "Sending post request. Waiting response."
						json_body = json.loads(body)
						r = requests.post(url, json = json_body)
						#r = requests.post(url, json = json_text)
						print "r.status_code = %s" %r.status_code
						print r.text
						if r.status_code == requests.codes.ok:
							msg = makePostMsgResponse(json.dumps(r.json()))
							s.send(msg)
							print "Response sent."
		break

print "Application Closed Normally"
