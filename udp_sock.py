import socket, os, signal, traceback, time

filedir = "./rdfiles/"
LASER_IP = "192.168.0.21"


buf_size = 4096
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

debug = True

CMD_STOP                 = "00dbd209".decode("HEX")
CMD_PAUSE_CONTINUE       = "00ddd20b".decode("HEX")
CMD_HOME_XY              = "06ce52998989898989898989898989".decode("HEX") #goto abs coord (0|0)
CMD_HOME_Z               = "0177d2a5".decode("HEX")
CMD_HOME_U               = "f67ed82d".decode("HEX")
CMD_FOCUS                = "0971d82e".decode("HEX")

HANDSHAKE                = "0261d4890df7".decode("HEX")

CFG_X_SETTINGS           = "028fd48989a9".decode("HEX") #binary
CFG_X_STEP_LENGTH        = "020fd4898929".decode("HEX") #picometer
CFG_X_MAX_SPEED          = "0211d489892b".decode("HEX") #nanometer/s
CFG_X_JUMPOFF_SPEED      = "0293d48989ad".decode("HEX") #nanometer/s
CFG_X_MAX_ACC            = "0213d489892d".decode("HEX") #nanometer/s^2
CFG_X_BREADTH            = "0295d48989af".decode("HEX") #nanometer
CFG_X_KEY_JUMPOFF_SPEED  = "0215d489892f".decode("HEX") #nanometer/s
CFG_X_KEY_ACC            = "0287d48989a1".decode("HEX") #nanometer/s^2
CFG_X_ESTOP_ACC          = "0207d4898921".decode("HEX") #nanometer/s^2
CFG_X_HOME_OFFSET        = "0289d48989a3".decode("HEX") #nanometer

CFG_X_SETTINGS           = "029fd48989b9".decode("HEX") #binary
CFG_Y_STEP_LENGTH        = "021fd4898939".decode("HEX") #picometer
CFG_Y_MAX_SPEED          = "0221d489893b".decode("HEX") #nanometer/s
CFG_Y_JUMPOFF_SPEED      = "02a3d48989bd".decode("HEX") #nanometer/s
CFG_Y_MAX_ACC            = "0223d489893d".decode("HEX") #nanometer/s^2
CFG_Y_BREADTH            = "02a5d48989bf".decode("HEX") #nanometer
CFG_Y_KEY_JUMPOFF_SPEED  = "0225d489893f".decode("HEX") #nanometer/s
CFG_Y_KEY_ACC            = "0297d48989b1".decode("HEX") #nanometer/s^2
CFG_Y_ESTOP_ACC          = "0217d4898931".decode("HEX") #nanometer/s^2
CFG_Y_HOME_OFFSET        = "0299d48989b3".decode("HEX") #nanometer

CFG_Z_SETTINGS           = "02afd48989c9".decode("HEX") #binary
CFG_Z_STEP_LENGTH        = "022fd4898949".decode("HEX") #picometer
CFG_Z_MAX_SPEED          = "0231d489894b".decode("HEX") #nanometer/s
CFG_Z_JUMPOFF_SPEED      = "02b3d48989cd".decode("HEX") #nanometer/s
CFG_Z_MAX_ACC            = "0233d489894d".decode("HEX") #nanometer/s^2
CFG_Z_BREADTH            = "02b5d48989cf".decode("HEX") #nanometer
CFG_Z_KEY_JUMPOFF_SPEED  = "0235d489894f".decode("HEX") #nanometer/s
CFG_Z_KEY_ACC            = "02a7d48989c1".decode("HEX") #nanometer/s^2
CFG_Z_ESTOP_ACC          = "0227d4898941".decode("HEX") #nanometer/s^2
CFG_Z_HOME_OFFSET        = "02a9d48989c3".decode("HEX") #nanometer

CFG_U_SETTINGS           = "02bfd48989d9".decode("HEX") #binary
CFG_U_STEP_LENGTH        = "023fd4898959".decode("HEX") #picometer
CFG_U_MAX_SPEED          = "0241d489895b".decode("HEX") #nanometer/s
CFG_U_JUMPOFF_SPEED      = "02c3d48989dd".decode("HEX") #nanometer/s
CFG_U_MAX_ACC            = "0243d489895d".decode("HEX") #nanometer/s^2
CFG_U_BREADTH            = "02c5d48989df".decode("HEX") #nanometer
CFG_U_KEY_JUMPOFF_SPEED  = "0245d489895f".decode("HEX") #nanometer/s
CFG_U_KEY_ACC            = "02b7d48989d1".decode("HEX") #nanometer/s^2
CFG_U_ESTOP_ACC          = "0237d4898951".decode("HEX") #nanometer/s^2
CFG_U_HOME_OFFSET        = "02b9d48989d3".decode("HEX") #nanometer

CFG_LASER12_TYPE         = "027fd4898999".decode("HEX") #binary
# glass/RF/RF+preignition
CFG_LASER34              = "0297d4898baf".decode("HEX") #binary

CFG_LASER1_POWER_MIN     = "0281d489899b".decode("HEX") #percent
CFG_LASER1_POWER_MAX     = "0201d489891b".decode("HEX") #percent
CFG_LASER1_FREQUENCE     = "01ffd4898919".decode("HEX") #Hz
CFG_LASER1_PREIG_FREQ    = "0279d4898993".decode("HEX") #Hz
CFG_LASER1_PREIG_PULSE   = "01f9d4898913".decode("HEX") #1/10 percent

CFG_LASER2_POWER_MIN     = "0277d4898991".decode("HEX") #percent
CFG_LASER2_POWER_MAX     = "01f7d4898911".decode("HEX") #percent
CFG_LASER2_FREQUENCE     = "0205d489891f".decode("HEX") #Hz
CFG_LASER2_PREIG_FREQ    = "027bd4898995".decode("HEX") #Hz
CFG_LASER2_PREIG_PULSE   = "01fbd4898915".decode("HEX") #1/10 percent

CFG_LASER3_POWER_MIN     = "0251d489896b".decode("HEX") #percent
CFG_LASER3_POWER_MAX     = "02d3d48989ed".decode("HEX") #percent
CFG_LASER3_FREQUENCE     = "0253d489896d".decode("HEX") #Hz
CFG_LASER3_PREIG_FREQ    = "02d5d48989ef".decode("HEX") #Hz
CFG_LASER3_PREIG_PULSE   = "0255d489896f".decode("HEX") #1/10 percent

CFG_LASER4_POWER_MIN     = "02c7d48989e1".decode("HEX") #percent
CFG_LASER4_POWER_MAX     = "0247d4898961".decode("HEX") #percent
CFG_LASER4_FREQUENCE     = "02c9d48989e3".decode("HEX") #Hz
CFG_LASER4_PREIG_FREQ    = "0249d4898963".decode("HEX") #Hz
CFG_LASER4_PREIG_PULSE   = "02cbd48989e5".decode("HEX") #1/10 percent

CFG_LASER_ATTENUATION    = "0285d489899f".decode("HEX") #1/10 percent
CFG_HEAD_DISTANCE        = "027dd4898997".decode("HEX") #nanometer
CFG_ENABLE_AUTOLAYOUT    = "0273d489898d".decode("HEX") #binary
#02cfd48989e9
CFG_FEED_TRANSMISSION    = "0271d4898b89".decode("HEX") #binary
CFG_BROKEN_DELAY         = "01edd4898b05".decode("HEX") #milliseconds

LASER_STATE              = "0273d4898d89".decode("HEX")

TOTAL_ON_TIME            = "01f3d4898d09".decode("HEX") #seconds
TOTAL_PROCESSING_TIME    = "0275d4898d8b".decode("HEX") #seconds
TOTAL_TRAVEL_X           = "0215d4898d2b".decode("HEX") #meters
TOTAL_TRAVEL_Y           = "0225d4898d3b".decode("HEX") #meters
TOTAL_PROCESSING_TIMES   = "01f5d4898d0b".decode("HEX") #count
TOTAL_LASER_ON_TIME      = "0203d4898d19".decode("HEX") #seconds
PREVIOUS_PROCESSING_TIME = "026bd4898d08".decode("HEX") #milliseconds
PREVIOUS_WORK_TIME       = "026bd4898d81".decode("HEX") #milliseconds
MAINBOARD_VERSION        = "01e1d4890d77".decode("HEX") #string

POSITION_AXIS_X          = "0213d4898d29".decode("HEX") #nanometer
POSITION_AXIS_Y          = "0223d4898d39".decode("HEX") #nanometer
POSITION_AXIS_Z          = "0233d4898d49".decode("HEX") #nanometer
POSITION_AXIS_U          = "0243d4898d59".decode("HEX") #nanometer

#03e152098b898989c799

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
	if debug:
		print "\x1B[32m> "+addr+": "+(data.encode("hex"))+"\x1B[0m  -  "+uns
	server.sendto(data, (addr, 40200))

def srecv():
	data, addr = server.recvfrom(buf_size)
	if debug:
		print "\x1B[33m< "+addr[0]+": "+data.encode("HEX")+"\x1B[0m  -  "+descramblestr(data).encode("HEX")
	ssend(addr[0], '\xC6') #send ACK
	return (data, addr)

def crecv():
	try:
		data, addr = client.recvfrom(buf_size)
	except Exception:
		if debug:
			print "\x1B[30;48;5;1m TIMEOUT REACHED \x1B[0m"	
		return (None, None)
	if debug:
		print "\x1B[43m< "+addr[0]+": "+data.encode("HEX")+"\x1B[0m  -  "+descramblestr(data).encode("HEX")
	return (data, addr)

def csend(addr, data):
	if debug:
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
		if debug:
			print "\x1B[30;48;5;1m MESSAGE CODE MISMATCH %04x / %04x \x1B[0m" % (resp[2:4], data[4:6])
		return None

def respond(addr, data, n):
	ssend(addr, "\xd4\x09"+data[4:6]+scramblestr(generateNumber(n)))

#see checksum.txt
def generateChecksum(n):
	return ""

responses = {
#	                               DA  01  05  7E:                 XX
	"0261d4890df7": scramblestr("\xda\x01\x05\x7e\x06\x28\x41\x4a\x10"), #HANDSHAKE1, MODELNUMBER?
	# It seems like this could contain any data, even 0xDA 0x01 0x00 0x00 ... 0x00 is accepted
#	 897bda000004
#	"0273d489898d": scramblestr("\xda\x01\x00\x04\x00\x00\x00\x00\x23"), #HANDSHAKE2
#
#d409898d898989892b

# INIT
#	2x HANDSHAKE1
#	2x HANDSHAKE2
#	1x HANDSHAKE1

# see callback() below for more details
#	 897bda000400
#	"0273d4898d89": scramblestr("\xda\x01\x04\x00\x00\x00\x00\x00\x00"), #STATE1
#PAUSE/DOWNLOAD: d4098d8989c98d810b
#PAUSE/STOP    : d4098d8989c98d810b -> PAUSE/RUNNING STATE
#STOP/STOP       d4098d8989c98d8589

#	 891cda000026
#	"0295d48989af": scramblestr("\xda\x01\x00\x26\x00\x00\x2a\x5c\x60"), #STATE2
#d40989af8989a3d5e9
#d40989af8989a3d5e9
#d40989af8989a3d5e9

#	 892cda000036
#	"02a5d48989bf": scramblestr("\xda\x01\x00\x36\x00\x00\x1e\x42\x20"), #STATE3
#d40989bf898997cba9
#d40989bf898997cba9
#d40989bf898997cba9

#	 8907da000021
#	"020fd4898929": scramblestr("\xda\x01\x00\x21\x00\x04\x27\x21\x5c"), #STATE4
#d4098929898d2f29d5
#d4098929898d2f29d5
#d4098929898d2f29d5

#	 8917da000031
#	"021fd4898939": scramblestr("\xda\x01\x00\x31\x00\x02\x02\x20\x1f"), #STATE5
#d4098939898b8ba917
#d4098939898b8ba917
#d4098939898b8ba917

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
	request(addr, LASER_STATE) #LASER in pause/job active
	request(addr, CFG_X_BREADTH) #LASER X/Width d40989af+number
	request(addr, CFG_Y_BREADTH) #LASER Y/Depth
	request(addr, CFG_X_STEP_LENGTH) #Laser X Step length (picometer)
	request(addr, CFG_Y_STEP_LENGTH) #Laser Y Step length (picometer)

def init(addr):
	handshake(addr)
	handshake(addr)
	request(addr, "\x02\x73\xd4\x89\x89\x8d")
	request(addr, "\x02\x73\xd4\x89\x89\x8d")

def processFile(addr, id):
	#0977e8030001
	#8909e8030002
	#...
	pass

def requestFile(addr, id):
	#09f6e50001
	#0988e50002
	#...
	pass

def deleteFile(addr, id):
	#8906e80000010001
	#0b1ae80000020002
	#...
	pass

def sendFilelist(addr):
	print "\x1B[31m# SEND FILELIST\x1B[0m"
	files = next(os.walk(filedir))[2]
	fname = ""
	ssend(addr, scramblestr("\xda\x01\x04\x05" + generateNumber(len(files))))
	for i in range(0, len(files)):
		data, sender_addr = srecv()
		if len(data) == 8 and descramble(ord(data[-1])) is i:
#		   and data[:3] == "\x0b" + chr(26 + i) + "\e8"
			print "\x1B[31m# DUPLICATE FILE, NO LONGER SEND FILELIST\x1B[0m"
			return
		#request processing time
		elif data[-2] == "\x0f":
			callback(addr, data)
			data, sender_addr = srecv()
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
	# 0x02 = TOTAL PROCESSING TIME    (s)
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
		data = request(addr, POSITION_AXIS_U)
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

def disableLasers(addr):
	pass
#0962c601 0000 - number (1/10 percent) is shifted left by 4 bit
#8903c621 0000
#8965c602 0000
#8904c622 0000

# HOMING XY
#0b93c9020000060d20
#disableLasers()
#8dc4d9100000000000000000000000

def moveAxis(addr, axis, nm=10000, speed=100000):
	csend(addr, scramblestr(generateChecksum("") + "\xc9\x02" + generateNumber(speed)))
	return csend(addr, scramblestr(generateChecksum("") + "\xd9" + chr(axis) + "\x02" + generateNumber(nm)))

#currently we need this
def callback(addr, data):
# HANDSHAKE, MODEL, STATE?
	if data == HANDSHAKE:
	#                              DA  01  05  7E:
		ssend(addr, scramblestr("\xda\x01\x05\x7e\x06\x28\x41\x4a\x10"))
	#STATE
	#elif data == "\x02\x73\xd4\x89\x8d\x89":
	#	ssend(addr, "d4098d8989c98d810b".decode("HEX"))
	elif data == "02cfd48989e9".decode("HEX"):
		respond(addr, data, 65535)
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


print bin(parseNumber(descramblestr("89c98d810b".decode("HEX")))) #pause/running
print bin(parseNumber(descramblestr("89c98d8589".decode("HEX"))))

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
	#moveAxis(LASER_IP, 0, 1000) #test that
	import sys
	#request the current position
	while True:
		sys.stdout.write("X: %07.3f  Y: %07.3f\x1B[0K\r" % (readSystemInfo(LASER_IP, 0x29) / 1000.0, readSystemInfo(LASER_IP, 0x39) / 1000.0))
		sys.stdout.flush()
		time.sleep(.2)
except Exception as e:
	traceback.print_exc()
	print e
#cleanup
os.kill(pid, signal.SIGTERM)