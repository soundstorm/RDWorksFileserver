
# encoding: utf-8

from RDWorks.RDLaser import RDLaser
import time, socket
import sys
reload(sys)
sys.setdefaultencoding('utf8')

class RDClient(object):
	debug=False
	
	def __init__(self, addr="127.0.0.1"):
		RDLaser.getClient()
		self.addr = addr
		pass
	
	def setAddr(self, addr):
		self.addr = addr
	
	def recv(self):
		try:
			data, server_addr = RDLaser.getClient().recvfrom(RDLaser.BUF_SIZE)
		except socket.timeout:
			if self.debug:
				print u"\x1B[30;48;5;1m TIMEOUT REACHED \x1B[0m"	
			return (None, None)
		if self.debug:
			print u"\x1B[44m< "+server_addr[0]+": "+data.encode("HEX")+u"\x1B[0m  -  "+RDLaser.descramblestr(data).encode("HEX")
		return (data, server_addr)
	
	def send(self, data):
		scr = RDLaser.checksum(RDLaser.scramblestr(data))
		if self.debug:
			print u"\x1B[42m> "+self.addr+": "+(scr.encode("hex"))+u"\x1B[0m  -  "+data.encode("HEX")
		RDLaser.getClient().sendto(scr, (self.addr, RDLaser.SERVER_PORT))
		data, server_addr = self.recv()
		if (data != '\xc6'):
			return False
		return True
	
	def request(self, data):
		if not self.send(data):
			return None
		resp, server_addr = self.recv()
		if resp == None:
			return None
		resp = RDLaser.descramblestr(resp)
		if resp[2:4] == data[2:4]:
			return resp[4:]
		else:
			if self.debug:
				print u"\x1B[30;48;5;1m MESSAGE CODE MISMATCH %s / %s \x1B[0m" % (resp[2:4].encode("HEX"), data[2:4].encode("HEX"))
			return None
	
	def init(self):
		self.handshake()
		self.handshake()
		self.request(u"\xda\x00\x00\x04")
		self.request(u"\xda\x00\x00\x04")
	
	def handshake(self):
		return self.request(u"\xda\x00\x05\x7e") == u"\x06\x28\x41\x4a\x10"
	
	def getState(self):
		return self.request(RDLaser.LASER_STATE) == u"\x00\x40\x04\x0c\x00"
	
	def readSystemInfo(self, opt):
		data = self.request(opt)
		if data is None:
			return None
		else:
			val = RDLaser.toNumber(data[-5:])
			try:
				RDLaser.values[opt] = val
			except:
				pass
			return val
	
	def readBoardVersion(self):
		data = self.request(RDLaser.MAINBOARD_VERSION)
		if data is None:
			return ""
		return self.descramblestr(data[4:-1])
	
	def getSystemInfo(self):
		self.init()
		return {
			"totalontime": self.readSystemInfo(RDLaser.TOTAL_ON_TIME),
			"totalprocessingtime": self.readSystemInfo(RDLaser.TOTAL_PROCESSING_TIME),
			"totaltravelx": self.readSystemInfo(RDLaser.TOTAL_TRAVEL_X),
			"totaltravely": self.readSystemInfo(RDLaser.TOTAL_TRAVEL_Y),
			"totalprocessingtimes": self.readSystemInfo(RDLaser.TOTAL_PROCESSING_TIMES),
			"totallaserontime": self.readSystemInfo(RDLaser.TOTAL_LASER_ON_TIME),
			"previousprocessingtime": self.readSystemInfo(RDLaser.PREVIOUS_PROCESSING_TIME),
			"mainboardversion": self.readBoardVersion()
		}
	
	def moveAxis(self, axis, nm=10000, speed=100000):
		self.send(u"\xc9\x02" + RDLaser.fromNumber(speed))
		return self.send(u"\xd9" + chr(axis) + u"\x02" + RDLaser.toNumber(nm))
	
	def requestFilelist(self, filename=None, overwrite=False):
		filelist = []
		resp = self.request(u"\xda\x00\x04\x05")
		if resp == None:
			return filelist, False
		num_files = RDLaser.toNumber(resp)
		for i in range(0, num_files):
			resp = self.request(u"\xe8\x01"+RDLaser.fromNumber(i+1, 2))
			if resp == None:
				break
			filename_ = resp[:-1].upper()
			'''
			fileno = RDLaser.toNumber(resp[:2], 2)
			if i+1 != fileno:
				raise ValueError("Reported filenumber does not match iterator")
			'''
			filelist.append(filename_)
			if filename is not None and filename.upper() == filename_[:-1]:
				while not daemon:
					print "Duplicate Filename %s, overwrite?" % filename
					inp = raw_input("[Y/N] ")
					if inp.lower() == "y":
						overwrite=True
						break
					elif inp.lower() == "n":
						break
				if overwrite:
					self.send(u"\xe8\x00" + RDLaser.fromNumber(i+1, 2) + RDLaser.fromNumber(i+1, 2))
					return filelist, True
				return filelist, False
		if filename is not None:
			self.send(u"\xe8\x02\xe7\x01"+filename+u"\x00")
		return filelist, True
	
	'''
	da00057e #init
	da00057e #init
	da000004 #init
	da000004 #init
	da00057e #HANDSHAKE
	da000400 #LASER_STATE
	da000026 #CFG_X_BREADTH
	da000036 #CFG_Y_BREADTH
	da000021 #CFG_X_STEP_LENGTH
	da000031 #CFG_Y_STEP_LENGTH
	da00057e #HANDSHAKE
	da000b12 #unknown
	da00057e #HANDSHAKE
	da00057e #HANDSHAKE
	da000004 #unknown
	da000004 #unknown
-	e802e701 #filename
	'''
	
	# only descrambled rd files!
	def sendFile(self, file, name=None, overwrite=False):
		self.init()
		self.handshake()
		self.request(u"\xd2\x00\x04\x05")
		if not self.getState():
			return False
		self.handshake()
		self.request(u"\xd2\x00\x0b\x12")
		self.handshake()
		self.handshake()
		self.request(u"\xd2\x00\x04\x05")
		self.request(u"\xd2\x00\x04\x05")
		if name is not None:
			filelist, ok = self.requestFilelist(name, overwrite)
			if not ok:
				return False
			'''
			self.handshake()
			self.handshake()
			self.request(u"\xd2\x00\x04\x05")
			self.request(u"\xd2\x00\x04\x05")
			'''
		s = file.read(1470)
		while len(s):
			self.send(s)
			s = file.read(1470)
		file.close()
		if name is not None:
			self.send(u"\x01\x59\x70\x89\x60")
		return True
	
	def getFile(self, fileno, file):
		self.init()
		self.send(u"\xe5"+RDLaser.fromNumber(fileno, 2))
		while True:
			self.request(u"\xe5\x01\x01"+RDLaser.fromNumber(i, 5))
		file.close()
	
	def calculateTime(self, fileno):
		self.init()
		return RDLaser.toNumber(self.request(u"\xe8\x04"+RDLaser.fromNumber(fileno, 2)))
	
	#fileno = 0 will delete all
	def deleteFile(self, fileno):
		self.init()
		self.send(u"\xe8\x00"+RDLaser.fromNumber(fileno, 2)+RDLaser.fromNumber(fileno, 2))