
# encoding: utf-8

from RDWorks.RDLaser import RDLaser
import time, os
import sys
reload(sys)
sys.setdefaultencoding('utf8')

class RDServer(RDLaser):
	debug = False
	
	def __init__(self, filedir="./rdfiles/"):
		RDLaser.getServer()
		self.filedir = filedir
		self.responses = {
			"da00057e": u"\xda\x01\x05\x7e\x06\x28\x41\x4a\x10",
			"da000b12": u"\xda\x01\x0b\x12\x0f\x11\x64\x00\x00",
		}
		pass

	def send(self, addr, data):
		scr = RDLaser.scramblestr(data)
		if self.debug:
			if data[:3] == u"\xe8\x01\x00":
				uns = str(ord(data[3]))+" - "+data[4:-1]
			else:
				uns = data.encode("HEX")
			print u"\x1B[32m> "+addr+": "+(scr.encode("hex"))+u"\x1B[0m  -  "+uns
		RDLaser.getServer().sendto(scr, (addr, RDLaser.CLIENT_PORT))
	
	def recv(self):
		data, addr = RDLaser.getServer().recvfrom(RDLaser.BUF_SIZE)
		if data[:2] != RDLaser.checksum(data[2:])[:2]:
			print data[0:2].encode("HEX")
			if self.debug:
				print(u"\x1B[31mCHECKSUM MISMATCH\x1B[0m")
			return ("", addr)
		data = RDLaser.descramblestr(data[2:])
		if self.debug:
			print(u"\x1B[34m< "+addr[0]+": "+RDLaser.scramblestr(data).encode("HEX")+u"\x1B[0m  -  "+data.encode("HEX"))
		self.send(addr[0], '\xcc') #send ACK
		return (data, addr)
	
	def respond(self, addr, data, n):
		self.send(addr, u"\xda\x01"+data[2:4]+RDLaser.fromNumber(n))
	
	def sendSystemInfo(self, addr, opt):
		# 0x01 = TOTAL ON TIME            (s)
		# 0x02 = TOTAL PROCESSING TIME    (s)
		# 0x03 = TOTAL PROCESSING TIMES   (#)
		# 0x08 = PREVIOUS PROCESSING TIME (ms)
		# 0x11 = TOTAL TRAVEL Y           (m)
		# 0x23 = TOTAL TRAVEL X           (m)
		self.send(addr, u"\xda\x01\x04"+chr(opt)+RDLaser.fromNumber(0))
	
	def callback(self, addr, data):
	# HANDSHAKE, MODEL, STATE?
		if data == self.HANDSHAKE:
			self.send(addr, u"\xda\x01\x05\x7e\x06\x28\x41\x4a\x10")
		#STATE
		#elif data == u"\x02\x73\xd4\x89\x8d\x89":
		#	ssend(addr, "d4098d8989c98d810b".decode("HEX"))
		elif data == u"\xda\x00\x00\x60":
			self.respond(addr, data, 65535)
		# Filelist request
		elif data == u"\xda\x00\x04\x05":
			self.sendFilelist(addr)
		elif data[:2] == u"\xe8\x00":
			self.deleteFile(RDLaser.toNumber(data[2:], 2))
		#elif data[:2] == u"\xe8\x04":
		#	self.calculateTime(RDLaser.toNumber(data[2:], 2))
		elif data[0] == u"\xe5":
			self.sendFile(RDLaser.toNumber(data[1:], 2))
		# System info request
		elif data[2:-1] == u"\xda\x00\x04":
			self.sendSystemInfo(addr, ord(data[-1]))
		# Model number query
		elif data == RDLaser.MAINBOARD_VERSION:
			self.send(addr, u"\xda\x01\x05\x7f"+RDLaser.values[RDLaser.MAINBOARD_VERSION]+u"\x00")
		# Specific codes (deprecated)
		elif data.encode("hex") in self.responses:
			self.send(addr, self.responses[data.encode("hex")])
		# Generic answer
		###
		# Query is as following:
		# 0x89 0xXX 0xDA 0x00 0xYY 0xZZ
		# Answers are in following format:
		# 0xDA 0x01 0xYY 0xZZ ...
		# so each request [4:6] must match response [2:4]
		# Rest of the answer (...) does not noticably change anything as far as tested
		###
		elif data[:2] == u"\xda\x00":
			try:
				self.respond(addr, data, RDLaser.values[data])
			except:
				self.respond(addr, data, 0)
	
	def sendFilelist(self, addr):
		if self.debug:
			print u"\x1B[31m# SEND FILELIST\x1B[0m"
		files = next(os.walk(self.filedir))[2]
		num_files = len(files)
		i = 0
		while i < num_files:
			if "." in files[i] and files[i].rsplit('.',1)[1].lower() == "rd":
				i += 1
			else:
				del files[i]
				num_files -= 1
		fname = ""
		self.send(addr, u"\xda\x01\x04\x05" + RDLaser.fromNumber(len(files)))
		for i in range(0, len(files)):
			data, sender_addr = self.recv()
			if len(data) == 6 and ord(data[-1]) is i:
				if self.debug:
					print u"\x1B[5m\x1B[31m# DUPLICATE FILE, NO LONGER SEND FILELIST\x1B[0m\x1B[25m"
				return
			#request processing time
			elif data[-2] == u"\x07":
				self.callback(addr, data)
				data, sender_addr = self.recv()
			elif ord(data[-1]) is not i+1:
				if self.debug:
					print u"\x1B[5m\x1B[31m# INVALID REQUEST, CANCELLED DOWNLOAD?\x1B[0m\x1B[25m"
				self.callback(addr, data)
				return
			fname = files[i].split('.',1)[0]
			#Send filename, \0 terminated
			self.send(sender_addr[0], u"\xe8\x01"+(RDLaser.fromNumber(i + 1, 2)+fname[:8].upper())+u"\x00")
		if self.debug:
			print(u"\x1B[31m# FILELIST SENT\x1B[0m")
	
	#Start file by file ID
	def processFile(self, fileno):
		self.init()
		self.send(u"\xe8\x03"+fromNumber(fileno, 2))
	
	def sendFile(self, fileno):
		pass
	
	def deleteFile(self, fileno):
		pass
	
	def recvFile(self):
		filetransfer = False
		file = None
		while True:
			data, sender_addr = self.recv()
			# Handle file download
			if len(data) > 4:
				if file is None:
					if data[0:4] == u"\xe8\x02\xe7\x01": # We got the filename here
						file = open(self.filedir+data[4:-1]+".rd",'w')
					else:
						file = open(self.filedir+"DIRECT.rd",'w')
						file.write(data)
				else:
					file.write(data)
			else:
				if file is not None:
					file.close()
				self.callback(sender_addr[0], data)
				return data

	def start(self):
		while True:
			self.recvFile()