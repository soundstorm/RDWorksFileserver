import socket, os

filedir = "./rdfiles/"

buf_size = 4096

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(('', 50200))

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.bind(('', 40200))
client.settimeout(1) #non-blocking

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
def generateNumber(number, bytes=5):
	s = ""
	for i in range(-bytes+1, 1):
		s += chr((number >> (-7 * i)) & 0x7F)
	return s


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

def ssend(addr, data):
	if data[:3] == "e20989".decode("HEX"):
		uns = str(descramble(ord(data[3])))+" - "+descramblestr(data[4:-1])
	else:
		uns = descramblestr(data)
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
	client.sendto(data, (addr, 40200))
	data, server_addr = client.recv()
	if (data != '\xc6'):
		return False
	return True

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
	pass

def sendSystemInfo(addr, opt):
	# 0x01 = TOTAL ON TIME            (s)
	# 0x02 = TOT PROCESSING TIME      (s)
	# 0x03 = TOTAL PROCESSING TIMES   (#)
	# 0x08 = PREVIOUS PROCESSING TIME (ms)
	# 0x11 = TOTAL TRAVEL Y           (m)
	# 0x23 = TOTAL TRAVEL X           (m)
	ssend(addr, scramblestr("\xda\x01\x04"+chr(opt)+generateNumber(0)))
'''
	"01f3d4898d09": scramblestr("\xda\x01\x04\x01"+generateNumber(123)).encode("HEX"),	#TOTAL ON TIME            (s)
	"0275d4898d8b": scramblestr("\xda\x01\x04\x02"+generateNumber(123)).encode("HEX"),	#TOTAL PROCESSING TIME    (s)
	"0215d4898d2b": scramblestr("\xda\x01\x04\x23"+generateNumber(123)).encode("HEX"),	#TOTAL TRAVEL X           (m)
	"0225d4898d3b": scramblestr("\xda\x01\x04\x33"+generateNumber(123)).encode("HEX"),	#TOTAL TRAVEL Y           (m)
	"01f5d4898d0b": scramblestr("\xda\x01\x04\x03"+generateNumber(123)).encode("HEX"),	#Total processing times   (#)
	"0203d4898d19": scramblestr("\xda\x01\x04\x11"+generateNumber(123)).encode("HEX"),	#TOTAL LASER ON TIME      (s)
	"026bd4898d81": scramblestr("\xda\x01\x04\x08"+generateNumber(123)).encode("HEX"),	#PREVIOUS PROCESSING TIME (ms)
	"01e1d4890d77": scramblestr("\xda\x01\x05\x7f"+"VERSION").encode("HEX"), #MAINBOARD VERSION
'''

#currently we need this
def callback(addr, data):
# HANDSHAKE, MODEL, STATE?
	if data == "\x02\x61\xd4\x89\x0d\xf7":
#		                          DA  01  05  7E:
		ssend(addr, scramblestr("\xda\x01\x05\x7e\x06\x28\x41\x4a\x10"))
# Filelist request
	elif data == "\x01\xf7\xd4\x89\x8d\x0d":
		sendFilelist(addr)
# System info request
	elif data[2:-1] == "\xd4\x89\x8d":
		sendSystemInfo(addr, descramble(ord(data[-1])))
# Model number query
	elif data == "\x01\xe1\xd4\x89\x0d\x77":
		ssend(addr, scramblestr("\xda\x01\x05\x7f"+"RD-FS 0.1 by Luca Zimmermann"+"\x00"))
# Generic answer
###
# Query is as following:
# 0x89 0xXX 0xDA 0x00 0xYY 0xZZ
# Answers are in following format:
# 0xDA 0x01 0xYY 0xZZ ...
# Rest of the answer (...) does not noticably change anything
###
	elif data[2:4] == "\xd4\x89":
		ssend(addr, "\xd4\x09"+data[4:]+"\x89\x89\x89\x89\x89")
# Specific codes (deprecated)
	elif data.encode("hex") in responses:
		ssend(addr, responses[data.encode("hex")])



def loop():
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

crecv()

while True:
	loop()
