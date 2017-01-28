import socket, os

filedir = "./rdfiles/"

buf_size = 4096

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('', 50200))


# thanks to http://stefan.schuermans.info/rdcam/scrambling.html
MAGIC = 0x88

def scramblestr(string):
	s = ""
	for c in string:
		s += chr(scramble(ord(c)))
	return s

def scramble(p):
	a = (p & 0x7E) | ((p >> 7) & 0x01) | ((p << 7) & 0x80)
	b = a ^ MAGIC
	s = (b + 1) & 0xFF
	return s

def descramblestr(string):
	p = ""
	for c in string:
		p += chr(descramble(ord(c)))
	return p

def descramble(s):
	a = (s + 0xFF) & 0xFF
	b = a ^ MAGIC
	p = (b & 0x7E) | ((b >> 7) & 0x01) | ((b << 7) & 0x80)
	return p

responses = {
	"0261d4890df7": "d4090df78fa149c399", #HANDSHAKE1
	"0273d489898d": "d409898d898989892b", #HANDSHAKE2
# INIT
#	2x HANDSHAKE1
#	2x HANDSHAKE2
#	1x HANDSHAKE1
	"0273d4898d89": "d4098d8989c98d8589", #STATE1
	"0295d48989af": "d40989af8989a3d5e9", #STATE2
	"02a5d48989bf": "d40989bf898997cba9", #STATE3
	"020fd4898929": "d4098929898d2f29d5", #STATE4
	"021fd4898939": "d4098939898b8ba917", #STATE5


#############################################################################################
######################################### FILETRANSFER ######################################
#############################################################################################

# if file should be started only, this part is skipped
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#	1x HANDSHAKE1
	"01fbd489039b": "d409039b0719ed8989", #now RDWorks may request for filename
#	2x HANDSHAKE1
#	2x HANDSHAKE2
#
#	"01f7d4898d0d": "d4098d0d89898989"+SCRAMBLED(NUMOFFILES),          #da 01 04 05 00 00 00 00 NUMOFFILES
# from now on all the responses start with 0xE2 0x09 0x89 SCRAMBLED(NUM+FILENAME) 0x89
# these messages contain all the files saved on the laser
# if RD Works found a duplicate filename above, it stops communication right after the filename and shows dialogbox
# it is then resumed with the following messages:
#	"027fe28989018901" # no response needed, but skipped when no duplicate
# but anyway would continue with
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
# which does not expect any answer
#############################################################################################

#PAUSE/CONTINUE:
#	2x HANDSHAKE1
#	2x HANDSHAKE2
#	1x HANDSHAKE1
#	STATE1-5
}

def recv():
	data, addr = s.recvfrom(buf_size)
	uns = descramblestr(data)
	print "\x1B[33m< "+addr[0]+": "+data.encode("HEX")+"\x1B[0m  -  "+uns.encode("HEX")
	send(addr[0], '\xC6') #send ACK
	return (data, addr)

def send(addr, data):
	if data[:3] == "e20989".decode("HEX"):
		uns = str(descramble(ord(data[3])))+" - "
		for c in data[4:-1]:
			uns += chr(descramble(ord(c)))
	else:
		uns = ""
		for c in data:
			uns += "%02x " % descramble(ord(c))
	print "\x1B[32m> "+addr+": "+(data.encode("hex"))+"\x1B[0m  -  "+uns
	s.sendto(data, (addr, 40200))

def sendFilelist(addr):
	print "\x1B[31m# SEND FILELIST\x1B[0m"
	files = next(os.walk(filedir))[2]
	fname = ""
	send(addr, "\xd4\x09\x8d\x0D\x89\x89\x89\x89"+chr(scramble(len(files))))
	for i in range(0, len(files)):
		data, sender_addr = recv()
		if data == "\x02\x7f\xe2\x89\x89\x01\x89\x01":
			print "\x1B[31m# DUPLICATE FILE, NO LONGER SEND FILELIST\x1B[0m"
			return
		elif descramble(ord(data[-1])) is not i+1:
			print "\x1B[31m# INVALID REQUEST\x1B[0m"
			return
		if files[i].find('.') >= 0:
			fname = files[i][:files[i].find('.')]
		else:
			fname = files[i]
		send(sender_addr[0], "\xe2\x09\x89"+scramblestr(chr(i+1)+fname[:8].upper())+"\x89")
	print("\x1B[31m# FILELIST SENT\x1B[0m")

#currently we need this
def callback(addr, data):
	if data == "\x01\xf7\xd4\x89\x8d\x0d":
		sendFilelist(addr)
	elif data.encode("hex") in responses:
		send(addr, responses[data.encode("hex")].decode("hex"))

def loop():
	filetransfer = False
	file = None
	while True:
		data, sender_addr = recv()
		# Handle file download
		if len(data) > 6:
			if file is None:
				if data[2:6] == "\xe2\x8b\x70\x09":
					file = open(filedir+descramblestr(data[6:-1])+".rd",'w')
				else:
					file = open(filedir+"direct.rd",'w')
					file.write(data[2:]) #I don't know how to interpret those two bytes
			else:
				file.write(data[2:])
		else:
			if file is not None:
				file.close()
			callback(sender_addr[0], data)
			return data
	return None

while True:
	loop()
