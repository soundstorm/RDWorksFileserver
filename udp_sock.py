import socket, os, signal, traceback, time

filedir = "./rdfiles/"

buf_size = 4096
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

HANDSHAKE                = "0261d4890df7".decode("HEX")

TOTAL_ON_TIME            = "01f3d4898d09".decode("HEX")
TOTAL_PROCESSING_TIME    = "0275d4898d8b".decode("HEX")
TOTAL_TRAVEL_X           = "0215d4898d2b".decode("HEX")
TOTAL_TRAVEL_Y           = "0225d4898d3b".decode("HEX")
TOTAL_PROCESSING_TIMES   = "01f5d4898d0b".decode("HEX")
TOTAL_LASER_ON_TIME      = "0203d4898d19".decode("HEX")
PREVIOUS_PROCESSING_TIME = "026bd4898d08".decode("HEX")
MAINBOARD_VERSION        = "01e1d4890d77".decode("HEX")

POSITION_AXIS_X          = "0213d4898d29".decode("HEX")
POSITION_AXIS_Y          = "0223d4898d39".decode("HEX")
POSITION_AXIS_Z          = "0233d4898d49".decode("HEX")
POSITION_AXIS_A          = "0243d4898d59".decode("HEX")

# thanks to http://stefan.schuermans.info/rdcam/scrambling.html
MAGIC = 0x88

def scramble(p):
	a = (p & 0x7E) | ((p >> 7) & 0x01) | ((p << 7) & 0x80)
	b = a ^ MAGIC
	s = (b + 1) & 0xFF
	return s

def scramblestr(string):
	s = ""
	for c in string:
		s += chr(scramble(ord(c)))
	return s

def descramble(s):
	a = (s + 0xFF) & 0xFF
	b = a ^ MAGIC
	p = (b & 0x7E) | ((b >> 7) & 0x01) | ((b << 7) & 0x80)
	return p

def descramblestr(string):
	p = ""
	for c in string:
		p += chr(descramble(ord(c)))
	return p

# transmitted as 7-bit, 0x80 is reserved (but would be semi-valid here too)
def generateNumber(n, bytes=5):
	s = ""
	for i in range(-bytes+1, 1):
		s += chr((n >> (-7 * i)) & 0x7F)
	return s

def parseNumber(s, chars=5):
	n = 0
	for i in range(-chars, 0):
		n |= ord(s[i]) << (-7 * (i+1))
	return n


def ssend(addr, data):
	if data[:3] == "\xe2\x09\x89":
		uns = str(descramble(ord(data[3])))+" - "+descramblestr(data[4:-1])
	else:
		uns = descramblestr(data).encode("HEX")
	print "\x1B[32m> "+addr+": "+(data.encode("hex"))+"\x1B[0m  -  "+uns
	server.sendto(data, (addr, 40200))

def srecv():
	data, addr = server.recvfrom(buf_size)
	print "\x1B[33m< "+addr[0]+": "+data.encode("HEX")+"\x1B[0m  -  "+descramblestr(data).encode("HEX")
	ssend(addr[0], '\xC6') #send ACK
	return (data, addr)

def crecv():
	try:
		data, addr = client.recvfrom(buf_size)
	except Exception:
		print "\x1B[30;48;5;1m TIMEOUT REACHED \x1B[0m"	
		return (None, None)
	print "\x1B[43m< "+addr[0]+": "+data.encode("HEX")+"\x1B[0m  -  "+descramblestr(data).encode("HEX")
	return (data, addr)

def csend(addr, data):
	print "\x1B[42m> "+addr+": "+(data.encode("hex"))+"\x1B[0m  -  "+descramblestr(data).encode("HEX")
	client.sendto(data, (addr, 50200))
	data, server_addr = crecv()
	if (data != '\xc6'):
		return False
	return True

def request(addr, data):
	if not csend(addr, data):
		return None
	resp, addr = crecv()
	if resp[2:4] == data[4:6]:
		return resp
	else:
		print "\x1B[30;48;5;1m MESSAGE CODE MISMATCH %04x / %04x \x1B[0m" % (resp[2:4], data[4:6])
		return None

responses = {
#	                               DA  01  05  7E:                 XX
	"0261d4890df7": scramblestr("\xda\x01\x05\x7e\x06\x28\x41\x4a\x10"), #HANDSHAKE1, MODELNUMBER?
	# It seems like this could contain any data, even 0xDA 0x01 0x00 0x00 ... 0x00 is accepted
#	 897bda000004
#	"0273d489898d": scramblestr("\xda\x01\x00\x04\x00\x00\x00\x00\x23"), #HANDSHAKE2
# INIT
#	2x HANDSHAKE1
#	2x HANDSHAKE2
#	1x HANDSHAKE1

# see callback() below for more details
#	 897bda000400
#	"0273d4898d89": scramblestr("\xda\x01\x04\x00\x00\x00\x00\x00\x00"), #STATE1
#	 891cda000026
#	"0295d48989af": scramblestr("\xda\x01\x00\x26\x00\x00\x2a\x5c\x60"), #STATE2
#	 892cda000036
#	"02a5d48989bf": scramblestr("\xda\x01\x00\x36\x00\x00\x1e\x42\x20"), #STATE3
#	 8907da000021
#	"020fd4898929": scramblestr("\xda\x01\x00\x21\x00\x04\x27\x21\x5c"), #STATE4
#	 8917da000031
#	"021fd4898939": scramblestr("\xda\x01\x00\x31\x00\x02\x02\x20\x1f"), #STATE5

## VENDOR SETTINGS
# 028fd48989a9

#############################################################################################
######################################### FILETRANSFER ######################################
#############################################################################################

# if file should be started only, this part is skipped
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#	1x HANDSHAKE1
#	 0972da000b12
	"01fbd489039b": scramblestr("\xda\x01\x0b\x12\x0f\x11\x64\x00\x00"), #now RDWorks may request for filename
#	2x HANDSHAKE1
#	2x HANDSHAKE2
#
#	"01f7d4898d0d": "d4098d0d89898989"+SCRAMBLED(NUMOFFILES),          #da 01 04 05 00 00 00 00 NUMOFFILES
# from now on all the responses start with 0xE2 0x09 0x89 SCRAMBLED(NUM+FILENAME) 0x89
# these messages contain all the files saved on the laser
# if RD Works found a duplicate filename above, it stops communication right after the filename and shows dialogbox
# it is then resumed with the following messages:
#	"027fe28989018901" # no response needed, but skipped when no duplicate
# but anyway would continue with following
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# we are about to start the file transfer
#	1x HANDSHAKE1
#	1x HANDSHAKE2
#	2x HANDSHAKE1
#	2x HANDSHAKE2
# if download only, the filename is sent here, but does not need a reply
# at least here the file transfer starts if not cancelled before
# file transfer closes with
#	"0159708960"
# which does not expect any answer but ACK
#############################################################################################
}

def handshake(addr):
	return request(addr, "\x02\x61\xd4\x89\x0d\xf7") == "\xd4\x09\x0d\xf7\x8f\xa1\x49\xc3\x99"

def getStates(addr):
	request(addr, "\x02\x73\xd4\x89\x8d\x89")
	request(addr, "\x02\x95\xd4\x89\x89\xaf")
	request(addr, "\x02\xa5\xd4\x89\x89\xbf")
	request(addr, "\x02\x0f\xd4\x89\x89\x29")
	request(addr, "\x02\x1f\xd4\x89\x89\x39")

def init(addr):
	handshake(addr)
	handshake(addr)
	request(addr, "\x02\x73\xd4\x89\x89\x8d")
	request(addr, "\x02\x73\xd4\x89\x89\x8d")
	
	

def sendFilelist(addr):
	print "\x1B[31m# SEND FILELIST\x1B[0m"
	files = next(os.walk(filedir))[2]
	fname = ""
	ssend(addr, "\xd4\x09\x8d\x0D\x89\x89\x89\x89"+chr(scramble(len(files))))
	for i in range(0, len(files)):
		data, sender_addr = srecv()
		if len(data) == 8 and descramble(ord(data[-1])) is i:
#		   and data[:3] == "\x0b" + chr(26 + i) + "\e8"
			print "\x1B[31m# DUPLICATE FILE, NO LONGER SEND FILELIST\x1B[0m"
			return
		elif descramble(ord(data[-1])) is not i+1:
			print "\x1B[31m# INVALID REQUEST, CANCELLED DOWNLOAD?\x1B[0m"
			callback(addr, data)
			return
		if files[i].find('.') >= 0:
			fname = files[i][:files[i].find('.')]
		else:
			fname = files[i]
		ssend(sender_addr[0], "\xe2\x09\x89"+scramblestr(chr(i+1)+fname[:8].upper())+"\x89")
	print("\x1B[31m# FILELIST SENT\x1B[0m")

def requestFilelist(addr):
	return []

# name=None implies direct start of transmitted file
def sendFile(addr, file, name=None):
	init(addr)
	handshake(addr)
	request(addr, "\x02\x73\xd4\x89\x89\x8d")
	getStates(addr)
	handshake(addr)
	request(addr, "\x01\xfb\xd4\x89\x03\x9b")
	handshake(addr)
	handshake(addr)
	request(addr, "\x02\x73\xd4\x89\x89\x8d")
	request(addr, "\x02\x73\xd4\x89\x89\x8d")
	if name is not None:
		filelist = requestFilelist(addr)
		handshake(addr)
		handshake(addr)
		request(addr, "\x02\x73\xd4\x89\x89\x8d")
		request(addr, "\x02\x73\xd4\x89\x89\x8d")
	#TODO: split file and transmit here
	if name is not None:
		csend(addr, "\x01\x59\x70\x89\x60")

def sendSystemInfo(addr, opt):
	# 0x01 = TOTAL ON TIME            (s)
	# 0x02 = TOT PROCESSING TIME      (s)
	# 0x03 = TOTAL PROCESSING TIMES   (#)
	# 0x08 = PREVIOUS PROCESSING TIME (ms)
	# 0x11 = TOTAL TRAVEL Y           (m)
	# 0x23 = TOTAL TRAVEL X           (m)
	ssend(addr, scramblestr("\xda\x01\x04"+chr(opt)+generateNumber(0)))

def readSystemInfo(addr, opt):
	if (opt == 0x01):
		data = request(addr, TOTAL_ON_TIME)
	elif (opt == 0x02):
		data = request(addr, TOTAL_PROCESSING_TIME)
	elif (opt == 0x03):
		data = request(addr, TOTAL_PROCESSING_TIMES)
	elif (opt == 0x08):
		data = request(addr, PREVIOUS_PROCESSING_TIME)
	elif (opt == 0x11):
		data = request(addr, TOTAL_LASER_ON_TIME)
	elif (opt == 0x23):
		data = request(addr, TOTAL_TRAVEL_X)
	elif (opt == 0x33):
		data = request(addr, TOTAL_TRAVEL_Y)
	elif (opt == 0x29):
		data = request(addr, POSITION_AXIS_X)
	elif (opt == 0x39):
		data = request(addr, POSITION_AXIS_Y)
	elif (opt == 0x49):
		data = request(addr, POSITION_AXIS_Z)
	elif (opt == 0x59):
		data = request(addr, POSITION_AXIS_A)
	else:
		return -1
	if data is None:
		return -1
	else:
		return parseNumber(descramblestr(data[-5:]))

def readBoardVersion(addr):
	data = request(addr, MAINBOARD_VERSION)
	if data is None:
		return ""
	return descramblestr(data[4:-1])

def getSystemInfo(addr):
	init(addr)
	return {
		"totalontime": readSystemInfo(addr, 0x01),
		"totalprocessingtime": readSystemInfo(addr, 0x02),
		"totaltravelx": readSystemInfo(addr, 0x23),
		"totaltravely": readSystemInfo(addr, 0x33),
		"totalprocessingtimes": readSystemInfo(addr, 0x03),
		"totallaserontime": readSystemInfo(addr, 0x11),
		"previousprocessingtime": readSystemInfo(addr, 0x08),
		"mainboardversion": readBoardVersion(addr)
	}

#currently we need this
def callback(addr, data):
# HANDSHAKE, MODEL, STATE?
	if data == HANDSHAKE:
#		                          DA  01  05  7E:
		ssend(addr, scramblestr("\xda\x01\x05\x7e\x06\x28\x41\x4a\x10"))
# Filelist request
	elif data == "\x01\xf7\xd4\x89\x8d\x0d":
		sendFilelist(addr)
# System info request
	elif data[2:-1] == "\xd4\x89\x8d":
		sendSystemInfo(addr, descramble(ord(data[-1])))
# Model number query
	elif data == MAINBOARD_VERSION:
		ssend(addr, scramblestr("\xda\x01\x05\x7f"+"RD-FS 0.1 by Luca Zimmermann"+"\x00"))
# Generic answer
###
# Query is as following:
# 0x89 0xXX 0xDA 0x00 0xYY 0xZZ
# Answers are in following format:
# 0xDA 0x01 0xYY 0xZZ ...
# so each request [4:6] must match response [2:4]
# Rest of the answer (...) does not noticably change anything as far as tested
###
	elif data[2:4] == "\xd4\x89":
		ssend(addr, "\xd4\x09"+data[4:]+"\x89\x89\x89\x89\x89")
# Specific codes (deprecated)
	elif data.encode("hex") in responses:
		ssend(addr, responses[data.encode("hex")])



def serve():
	filetransfer = False
	file = None
	while True:
		data, sender_addr = srecv()
		# Handle file download
		if len(data) > 6:
			if file is None:
				if data[2:6] == "\xe2\x8b\x70\x09": # We got the filename here
					file = open(filedir+descramblestr(data[6:-1])+".rd",'w')
				else:
					file = open(filedir+"DIRECT.rd",'w')
					file.write(data[2:]) # I don't know how to interpret those two bytes
			else:
				file.write(data[2:])
		else:
			if file is not None:
				file.close()
			callback(sender_addr[0], data)
			return data
	return None

pid = os.fork()
if not pid:
	print "SERVER STARTED"
	server.bind(('', 50200))
	while True:
		serve()
	os.exit(0)

try:
	client.bind(('', 40200))
	client.settimeout(1) #set non-blocking
	crecv() #timeout test
	print getSystemInfo('127.0.0.1') #request test
	while True:
		time.sleep(10)
except Exception as e:
	traceback.print_exc()
	print e
#cleanup
os.kill(pid, signal.SIGTERM)