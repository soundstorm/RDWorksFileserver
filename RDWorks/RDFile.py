from RDWorks.RDFileLayer import RDFileLayer
from RDWorks.RDFileMove import RDFileMove

class RDFile(object):
	ORIGIN_MACHINE_ZERO = 0x10 #Absolute
	ORIGIN_ANCHOR_POS   = 0x11
	ORIGIN_CURRENT_POS  = 0x12
	debug = False
	
	def __init__(self):
		self.layers = []
		self.origin = RDFile.ORIGIN_CURRENT_POS
		self.bounds = [0, 0, 0, 0]
	
	def toNumber(self, s, chars=5):
		n = 0
		for i in range(-chars, 0):
			n |= ord(s[i]) << (-7 * (i+1))
		return n
	
	def getByte(self):
		return ord(self.file.read(1))
	
	def getShort(self):
		val = self.toNumber(self.file.read(2), 2)
		if val & 0x2000:
			val -= (1 << 14)
		return val
	
	def getUShort(self):
		return self.toNumber(self.file.read(2), 2)
	
	def getPercent(self):
		return self.getUShort() / 163.83
	
	def getLong(self):
		val = self.toNumber(self.file.read(5), 5)
		if val & 0x400000000:
			val -= (1 << 35)
		return val
	
	def getText(self):
		return ("%08x%08x" % (self.getLong(), self.getLong())).decode("HEX")
	
	def setCurrentLayer(self, layer):
		if self.debug and self.curlayer is not layer:
			print("Changing Layer to %d." % (layer, ))
		self.curlayer = layer
		while len(self.layers) <= layer:
			self.layers.append(RDFileLayer())
	
	def parseFile(self, filename):
		self.filename = filename
		self.file = open(filename, "r")
		self.sx = 0
		self.sy = 0
		self.lx = 0
		self.ly = 0
		self.origin = RDFile.ORIGIN_CURRENT_POS
		self.layers = [RDFileLayer(), ]
		self.curlayer = 0
		while True:
			cmd1 = self.getByte()
				
			if cmd1 & 0x80 == 0:
				if self.debug:
					print("\x1B[30;48;5;1mDid not finish reading previous cmd:\x1B[0m")
					self.file.seek(-2, 1)
					while self.getByte() & 0x80 == 0:
						self.file.seek(-2, 1)
					self.file.seek(-1, 1)
				cmdstr = "0x%02x" % self.getByte()
				b = self.getByte()
				while b & 0x80 == 0:
					cmdstr += " 0x%02x" % b
					b = self.getByte()
				if self.debug:
					print(cmdstr)
				self.file.seek(-1, 1)
			
			elif cmd1 == 0x80:
				cmd2 = readByte()
				if cmd2 == 0x00:
					self.layers[self.curlayer].penDown = readLong()
					if self.debug:
						print("Layer %d Pen Down %d nm" % (self.curlayer, self.layers[self.curlayer].penDown))
				if cmd2 == 0x0C:
					self.layers[self.curlayer].penUp = readLong()
					if self.debug:
						print("Layer %d Pen Up %d nm" % (self.curlayer, self.layers[self.curlayer].penUp))
			
			elif cmd1 == 0x88: #Absolute Move
				self.layers[self.curlayer].moves.append(RDFileMove(self.getLong(), self.getLong(), False, False, 0x88))
				if self.debug == 2:
					print(self.layers[self.curlayer].moves[-1].toString())
			
			elif cmd1 == 0x89: #Relative Move
				self.layers[self.curlayer].moves.append(RDFileMove(self.getShort(), self.getShort(), False, True, 0x89))
				if self.debug == 2:
					print(self.layers[self.curlayer].moves[-1].toString())
			
			elif cmd1 == 0x8A: #Relative X Move
				self.layers[self.curlayer].moves.append(RDFileMove(self.getShort(), 0, False, True, 0x8A))
				if self.debug == 2:
					print(self.layers[self.curlayer].moves[-1].toString())
			
			elif cmd1 == 0x8B: #Relative Y Move
				self.layers[self.curlayer].moves.append(RDFileMove(0, self.getShort(), False, True, 0x8B))
				if self.debug == 2:
					print(self.layers[self.curlayer].moves[-1].toString())
			
			elif cmd1 == 0xA8: #Absolute Cut
				self.layers[self.curlayer].moves.append(RDFileMove(self.getLong(), self.getLong(), True, False, 0xA8))
				if self.debug == 2:
					print(self.layers[self.curlayer].moves[-1].toString())
			
			elif cmd1 == 0xA9: #Relative Cut
				self.layers[self.curlayer].moves.append(RDFileMove(self.getShort(), self.getShort(), True, True, 0xA9))
				if self.debug == 2:
					print(self.layers[self.curlayer].moves[-1].toString())
			
			elif cmd1 == 0xAA: #Relative X Cut
				self.layers[self.curlayer].moves.append(RDFileMove(self.getShort(), 0, True, True, 0xAA))
				if self.debug == 2:
					print(self.layers[self.curlayer].moves[-1].toString())
			
			elif cmd1 == 0xAB: #Relative Y Cut
				self.layers[self.curlayer].moves.append(RDFileMove(0, self.getShort(), True, True, 0xAB))
				if self.debug == 2:
					print(self.layers[self.curlayer].moves[-1].toString())
			
			elif cmd1 == 0xC0:
				a = self.getByte()
				p = self.getPercent()
				if self.debug:
					print("0x%02x Layer %d %0.2f%%", (cmd1, a, p))
			
			elif cmd1 == 0xC1:
				a = self.getByte()
				p = self.getPercent()
				if self.debug:
					print("0x%02x Layer %d %0.2f%%", (cmd1, a, p))
			
			elif cmd1 == 0xC2:
				a = self.getByte()
				p = self.getPercent()
				if self.debug:
					print("0x%02x Layer %d %0.2f%%", (cmd1, a, p))
			
			elif cmd1 == 0xC3:
				a = self.getByte()
				p = self.getPercent()
				if self.debug:
					print("0x%02x Layer %d %0.2f%%", (cmd1, a, p))
			
			elif cmd1 == 0xC4:
				a = self.getByte()
				p = self.getPercent()
				if self.debug:
					print("0x%02x Layer %d %0.2f%%", (cmd1, a, p))
			
			elif cmd1 == 0xC5:
				a = self.getByte()
				p = self.getPercent()
				if self.debug:
					print("0x%02x Layer %d %0.2f%%", (cmd1, a, p))
			
			elif cmd1 == 0xC6: #Laser/Layer settings
				cmd2 = self.getByte()
				if cmd2 == 0x01:
					self.layers[self.curlayer].lasers[0].minPower = self.getPercent()
					if self.debug:
						print("Layer %d Laser 1 MinPower %0.2f" % (self.curlayer, self.layers[self.curlayer].lasers[0].minPower))
				elif cmd2 == 0x02:
					self.layers[self.curlayer].lasers[0].maxPower = self.getPercent()
					if self.debug:
						print("Layer %d Laser 1 MaxPower %0.2f" % (self.curlayer, self.layers[self.curlayer].lasers[0].maxPower))
				elif cmd2 == 0x05:
					self.layers[self.curlayer].lasers[2].minPower = self.getPercent()
					if self.debug:
						print("Layer %d Laser 3 MinPower %0.2f" % (self.curlayer, self.layers[self.curlayer].lasers[2].minPower))
				elif cmd2 == 0x06:
					self.layers[self.curlayer].lasers[2].maxPower = self.getPercent()
					if self.debug:
						print("Layer %d Laser 3 MaxPower %0.2f" % (self.curlayer, self.layers[self.curlayer].lasers[2].maxPower))
				elif cmd2 == 0x07:
					self.layers[self.curlayer].lasers[3].minPower = self.getPercent()
					if self.debug:
						print("Layer %d Laser 4 MinPower %0.2f" % (self.curlayer, self.layers[self.curlayer].lasers[4].minPower))
				elif cmd2 == 0x08:
					self.layers[self.curlayer].lasers[3].maxPower = self.getPercent()
					if self.debug:
						print("Layer %d Laser 4 MinPower %0.2f" % (self.curlayer, self.layers[self.curlayer].lasers[4].maxPower))
				elif cmd2 == 0x21:
					self.layers[self.curlayer].lasers[1].minPower = self.getPercent()
					if self.debug:
						print("Layer %d Laser 2 MinPower %0.2f" % (self.curlayer, self.layers[self.curlayer].lasers[1].minPower))
				elif cmd2 == 0x22:
					self.layers[self.curlayer].lasers[1].maxPower = self.getPercent()
					if self.debug:
						print("Layer %d Laser 2 MinPower %0.2f" % (self.curlayer, self.layers[self.curlayer].lasers[1].maxPower))
			
				elif cmd2 == 0x12:
					self.layers[self.curlayer].scanOpenDelay = self.getLong()
					if self.debug:
						print("Layer %d Scan Open Delay %d" % (self.curlayer, self.layers[self.curlayer].scanOpenDelay))
				elif cmd2 == 0x13:
					self.layers[self.curlayer].scanCloseDelay = self.getLong()
					if self.debug:
						print("Layer %d Scan Close Delay %d" % (self.curlayer, self.layers[self.curlayer].scanOpenDelay))
				elif cmd2 == 0x15:
					self.layers[self.curlayer].openDelay = self.getLong()
					if self.debug:
						print("Layer %d Open Delay %d" % (self.curlayer, self.layers[self.curlayer].closeDelay))
				elif cmd2 == 0x16:
					self.layers[self.curlayer].closeDelay = self.getLong()
					if self.debug:
						print("Layer %d Close Delay %d" % (self.curlayer, self.layers[self.curlayer].openDelay))
				
				elif cmd2 == 0x31:
					self.setCurrentLayer(self.getByte())
					self.layers[self.curlayer].lasers[0].bankMinPower = self.getPercent()
					if self.debug:
						print("Layer %d Laser 1 BankMinPower %0.2f" % (self.curlayer, self.layers[self.curlayer].lasers[0].bankMinPower))
				elif cmd2 == 0x32:
					self.setCurrentLayer(self.getByte())
					self.layers[self.curlayer].lasers[0].bankMaxPower = self.getPercent()
					if self.debug:
						print("Layer %d Laser 1 BankMaxPower %0.2f" % (self.curlayer, self.layers[self.curlayer].lasers[0].bankMaxPower))
				elif cmd2 == 0x35:
					self.setCurrentLayer(self.getByte())
					self.layers[self.curlayer].lasers[2].bankMinPower = self.getPercent()
					if self.debug:
						print("Layer %d Laser 3 BankMinPower %0.2f" % (self.curlayer, self.layers[self.curlayer].lasers[2].bankMinPower))
				elif cmd2 == 0x36:
					self.setCurrentLayer(self.getByte())
					self.layers[self.curlayer].lasers[2].bankMaxPower = self.getPercent()
					if self.debug:
						print("Layer %d Laser 3 BankMaxPower %0.2f" % (self.curlayer, self.layers[self.curlayer].lasers[2].bankMaxPower))
				elif cmd2 == 0x37:
					self.setCurrentLayer(self.getByte())
					self.layers[self.curlayer].lasers[3].bankMinPower = self.getPercent()
					if self.debug:
						print("Layer %d Laser 4 BankMinPower %0.2f" % (self.curlayer, self.layers[self.curlayer].lasers[3].bankMinPower))
				elif cmd2 == 0x38:
					self.setCurrentLayer(self.getByte())
					self.layers[self.curlayer].lasers[3].bankMaxPower = self.getPercent()
					if self.debug:
						print("Layer %d Laser 4 BankMaxPower %0.2f" % (self.curlayer, self.layers[self.curlayer].lasers[3].bankMaxPower))
				elif cmd2 == 0x41:
					self.setCurrentLayer(self.getByte())
					self.layers[self.curlayer].lasers[1].bankMinPower = self.getPercent()
					if self.debug:
						print("Layer %d Laser 2 BankMinPower %0.2f" % (self.curlayer, self.layers[self.curlayer].lasers[1].bankMinPower))
				elif cmd2 == 0x42:
					self.setCurrentLayer(self.getByte())
					self.layers[self.curlayer].lasers[1].bankMaxPower = self.getPercent()
					if self.debug:
						print("Layer %d Laser 2 BankMaxPower %0.2f" % (self.curlayer, self.layers[self.curlayer].lasers[1].bankMaxPower))
				
				elif cmd2 == 0x50:
					self.layers[self.curlayer].lasers[0].throughPower = self.getPercent()
					if self.debug:
						print("Layer %d Laser 1 ThroughPower %0.2f" % (self.curlayer, self.layers[self.curlayer].lasers[0].throughPower))
				elif cmd2 == 0x51:
					self.layers[self.curlayer].lasers[1].throughPower = self.getPercent()
					if self.debug:
						print("Layer %d Laser 2 ThroughPower %0.2f" % (self.curlayer, self.layers[self.curlayer].lasers[1].throughPower))
				elif cmd2 == 0x55:
					self.layers[self.curlayer].lasers[2].throughPower = self.getPercent()
					if self.debug:
						print("Layer %d Laser 3 ThroughPower %0.2f" % (self.curlayer, self.layers[self.curlayer].lasers[2].throughPower))
				elif cmd2 == 0x56:
					self.layers[self.curlayer].lasers[3].throughPower = self.getPercent()
					if self.debug:
						print("Layer %d Laser 4 ThroughPower %0.2f" % (self.curlayer, self.layers[self.curlayer].lasers[3].throughPower))
			
				elif cmd2 == 0x60:
					self.setCurrentLayer(self.getByte())
					laser = self.getByte()
					self.layers[self.curlayer].lasers[laser].pwmFrequency = self.getLong()
					if self.debug:
						print("Layer %d Laser %d PWM Frequency %d Hz" % (self.curlayer, laser, self.layers[self.curlayer].lasers[laser].pwmFrequency))
				
				else:
					if debug:
						print(" ! Unkown 0x%02x message: 0x%02x" % (cmd1, cmd2))
			
			elif cmd1 == 0xC7:
				a = self.getByte()
				p = self.getPercent()
				if self.debug:
					print("0x%02x Layer %d %0.2f%%", (cmd1, a, p))
			
			elif cmd1 == 0xC8:
				a = self.getByte()
				p = self.getPercent()
				if self.debug:
					print("0x%02x Layer %d %0.2f%%", (cmd1, a, p))
			
			elif cmd1 == 0xC9: #Speed
				cmd2 = self.getByte()
				if cmd2 == 0x02: #cut speed
					self.layers[self.curlayer].speed = self.getLong()
					if self.debug:
						print("Layer %d Speed: %d nm/s" % (self.curlayer, self.layers[self.curlayer].speed))
				elif cmd2 == 0x03: #pen speed
					self.layers[self.curlayer].penspeed = self.getLong()
					if self.debug:
						print("Layer %d Pen Up/Down Speed: %d nm/s" % (self.curlayer, self.layers[self.penlayer].speed))
				elif cmd2 == 0x04: #speed
					self.setCurrentLayer(self.getByte())
					self.layers[self.curlayer].speed = self.getLong()
					if self.debug:
						print("Layer %d Speed: %d nm/s" % (self.curlayer, self.layers[self.curlayer].speed))
			
			elif cmd1 == 0xCA: #Layer settings
				cmd2 = self.getByte()
				if cmd2 == 0x01: #Function
					flag = self.getByte()
					print("Layer %d Function: 0x%02x" % (self.curlayer, flag))
					if flag == 0x00: #CUT
						self.layers[self.curlayer].function |= RDFileLayer.CUT
					elif flag == 0x01:
						self.layers[self.curlayer].function |= RDFileLayer.BI_DIR_X
					elif flag == 0x02:
						self.layers[self.curlayer].function |= RDFileLayer.UNI_DIR_X
					elif flag == 0x03:
						self.layers[self.curlayer].function |= RDFileLayer.BI_DIR_Y
					elif flag == 0x04:
						self.layers[self.curlayer].function |= RDFileLayer.UNI_DIR_Y
					elif flag == 0x12:
						self.layers[self.curlayer].blowing = False
					elif flag == 0x13:
						self.layers[self.curlayer].blowing = True
				elif cmd2 == 0x02:
					self.setCurrentLayer(self.getByte())
				elif cmd2 == 0x03: #Enabled
					flag = self.getByte()
					if self.debug:
						print("Setting lasers on Layer %d to %s" % (self.curlayer, bin(flag)))
					self.layers[self.curlayer].lasers[0].enabled = flag & 0x01 > 0
					self.layers[self.curlayer].lasers[1].enabled = flag & 0x02 > 0
					self.layers[self.curlayer].lasers[2].enabled = flag & 0x04 > 0
					self.layers[self.curlayer].lasers[3].enabled = flag & 0x08 > 0
				elif cmd2 == 0x06: #Color
					self.setCurrentLayer(self.getByte())
					b = self.file.read(5)
					c = self.toNumber(b, 5)
					self.layers[self.curlayer].color = ((c & 0xFF0000) >> 16) | (c & 0xFF00) | ((c & 0xFF) << 16) #BGR
					if self.debug:
						print("Layer %d Color: #%06x" % (self.curlayer, self.layers[self.curlayer].color))
				elif cmd2 == 0x10: #IO Outputs
					self.layers[self.curlayer].IOs = self.getByte()
					if self.debug:
						print("Layer %d active IOs: %s" % (self.curlayer, bin(self.layers[self.curlayer].IOs)))
				elif cmd2 == 0x22:
					self.setCurrentLayer(self.getByte())
				elif cmd2 == 0x41:
					if self.debug:
						print("0xCA 0x41 0x%02x 0x%02x" % (self.getByte(), self.getByte()))
				else:
					if self.debug:
						print(" ! Unkown 0x%02x message: 0x%02x" % (cmd1, cmd2))
			
			elif cmd1 == 0xD7:
				self.file.close()
				break
			
			elif cmd1 == 0xD8: #File origin (relative/absolute/anchor)
				self.origin = self.getByte()
				if self.debug:
					print("Origin set to 0x%02x" % (self.origin, ))
			
			elif cmd1 == 0xDA: #Uhm?
				cmd2 = self.getByte()
				self.sx = self.getShort()
				self.lx = self.getLong()
				self.ly = self.getLong()
				print("SX %d LX %d LY %d" % (self.sx, self.lx, self.ly))
			
			elif cmd1 == 0xEA:
				self.getByte()
			
			elif cmd1 == 0xEB:
				pass
			
			elif cmd1 == 0xE6: #Absolute machine coords
				print("Absolute coords: 0x%02x" % (self.getByte(),))
			
			elif cmd1 == 0xE7: #Workspace
				cmd2 = self.getByte()
				if cmd2 == 0x00:
					pass
				elif cmd2 == 0x03: #Document lower bounds
					self.bounds[0] = self.getLong()
					self.bounds[1] = self.getLong()
					if self.debug:
						print("Document lower bounds 0xE7 0x03: (%d|%d)" % (self.bounds[0], self.bounds[1]))
				elif cmd2 == 0x04:
					print("Document 0xE7 0x04: (%d|%d) (%d|%d)" % (self.getShort(), self.getShort(), self.getLong(), self.getLong()))
				elif cmd2 == 0x05:
					print("0xE7 0x05: %d" % (self.getByte(),))
				elif cmd2 == 0x06:
					print("0xE7 0x06: (%d|%d)" % (self.getLong(), self.getLong()))
				elif cmd2 == 0x07:
					self.bounds[2] = self.getLong()
					self.bounds[3] = self.getLong()
					if self.debug:
						print("Document upper bounds 0xE7 0x07: (%d|%d)" % (self.bounds[2], self.bounds[3]))
				elif cmd2 == 0x08:
					print("Layer size 0xE7 0x08: (%d|%d) (%d|%d)" % (self.getShort(), self.getShort(), self.getLong(), self.getLong()))
				elif cmd2 == 0x13: #Layer origin
					self.layers[self.curlayer].bounds[0] = self.getLong()
					self.layers[self.curlayer].bounds[1] = self.getLong()
					if self.debug:
						print("Layer %d lower bounds 0x13: (%d|%d)" % (self.curlayer, self.layers[self.curlayer].bounds[0], self.layers[self.curlayer].bounds[1]))
				elif cmd2 == 0x17: #Layer size
					print("Current size 0x17: (%d|%d)" % (self.getLong(), self.getLong()))
				elif cmd2 == 0x23: #Initial offset from origin (?)
					print("0xE7 0x23: (%d|%d)" % (self.getLong(), self.getLong()))
				elif cmd2 == 0x24: #Flip settings (?)
					flag = self.getByte()
					if (flag & 0x01):
						if self.debug:
							print("HFlip-X")
					if (flag & 0x02):
						if self.debug:
							print("VFlip-X")
					if (flag & 0x04):
						if self.debug:
							print("HFlip-Y")
					if (flag & 0x08):
						if self.debug:
							print("VFlip-Y")
				elif cmd2 == 0x50:
					self.bounds[0] = self.getLong()
					self.bounds[1] = self.getLong()
					if self.debug:
						print("Document lower bounds 0xE7 0x50: (%d|%d)" % (self.bounds[0], self.bounds[1]))
				elif cmd2 == 0x51:
					self.bounds[2] = self.getLong()
					self.bounds[3] = self.getLong()
					if self.debug:
						print("Document upper bounds 0xE7 0x51: (%d|%d)" % (self.bounds[2], self.bounds[3]))
				elif cmd2 == 0x52: #Layer lower bounds
					self.setCurrentLayer(self.getByte())
					self.layers[self.curlayer].bounds[0] = self.getLong()
					self.layers[self.curlayer].bounds[1] = self.getLong()
					if self.debug:
						print("Layer %d lower bounds 0xE7 0x52: (%d|%d)" % (self.curlayer, self.layers[self.curlayer].bounds[0], self.layers[self.curlayer].bounds[1]))
				elif cmd2 == 0x53: #Layer upper bounds
					self.setCurrentLayer(self.getByte())
					self.layers[self.curlayer].bounds[2] = self.getLong()
					self.layers[self.curlayer].bounds[3] = self.getLong()
					if self.debug:
						print("Layer %d upper bounds 0xE7 0x53: (%d|%d)" % (self.curlayer, self.layers[self.curlayer].bounds[2], self.layers[self.curlayer].bounds[3]))
				elif cmd2 == 0x54:
					print("Layer %d 0xE7 0x54: %d" % (self.getByte(), self.getLong()))
				elif cmd2 == 0x55:
					print("Layer %d 0xE7 0x55: %d" % (self.getByte(), self.getLong()))
				elif cmd2 == 0x60:
					print("Layer 0xE7 0x60: %d" % (self.getByte(),))
				elif cmd2 == 0x61: #Layer lower bounds again?
					self.setCurrentLayer(self.getByte())
					self.layers[self.curlayer].bounds[0] = self.getLong()
					self.layers[self.curlayer].bounds[1] = self.getLong()
					if self.debug:
						print("Layer %d lower bounds 0xE7 0x61: (%d|%d)" % (self.curlayer, self.layers[self.curlayer].bounds[0], self.layers[self.curlayer].bounds[1]))
				elif cmd2 == 0x62: #Layer upper bounds again?
					self.setCurrentLayer(self.getByte())
					self.layers[self.curlayer].bounds[2] = self.getLong()
					self.layers[self.curlayer].bounds[3] = self.getLong()
					if self.debug:
						print("Layer %d upper bounds 0xE7 0x62: (%d|%d)" % (self.curlayer, self.layers[self.curlayer].bounds[2], self.layers[self.curlayer].bounds[3]))
				else:
					if self.debug:
						print(" ! Unkown 0x%02x message: 0x%02x" % (cmd1, cmd2))
				
			elif cmd1 == 0xF0: #File start
				pass
			
			elif cmd1 == 0xF1:
				cmd2 = self.getByte()
				if cmd2 == 0x00:
					if self.debug:
						print("0xF1 0x00 0x%02x" % (self.getByte(), ))
				elif cmd2 == 0x01:
					if self.debug:
						print("0xF1 0x01 0x%02x" % (self.getByte(), ))
				elif cmd2 == 0x02:
					if self.debug:
						print("0xF1 0x02 0x%02x" % (self.getByte(), ))
				elif cmd2 == 0x03:
					if self.debug:
						print("0xF1 0x03 (%d|%d)" % (self.getLong(), self.getLong()))
			
			elif cmd1 == 0xF2: #Document info
				cmd2 = self.getByte()
				if cmd2 == 0x00:
					b = self.getByte()
					if self.debug:
						print("Document ?? 0xF2 0x00 %02x" % (b,))
				elif cmd2 == 0x01:
					b = self.getByte()
					if self.debug:
						print("Document ?? 0xF2 0x01 %02x" % (b,))
				elif cmd2 == 0x02:
					self.name = self.getText()
					if self.debug:
						print("Document Name 0xF2 0x02: %s" % (self.name,))
				elif cmd2 == 0x03:
					print("Document lower bounds 0xF2 0x03: (%d|%d)" % (self.getLong(), self.getLong()))
				elif cmd2 == 0x04:
					print("Document upper bounds 0xF2 0x04: (%d|%d)" % (self.getLong(), self.getLong()))
				elif cmd2 == 0x05:
					print("Document size 0xF2 0x05: (%d|%d) (%d|%d)" % (self.getShort(), self.getShort(), self.getLong(), self.getLong()))
				elif cmd2 == 0x06:
					print("Document ?? 0xF2 0x06: (%d|%d)" % (self.getLong(), self.getLong()))
				elif cmd2 == 0x07:
					print("Document ?? 0xF2 0x07 %02x" % (self.getByte(),))
				else:
					if self.debug:
						print(" ! Unkown 0x%02x message: 0x%02x" % (cmd1, cmd2))
				
			else:
				print("\x1B[30;48;5;1mUnknown CMD: %02x\x1B[0m" % cmd1)
				b = self.getByte()
				while b & 0x80 == 0: #CMDs have highest bit set
					b = self.getByte()
				self.file.seek(-1, 1)
	
	def toSVG(self, mirrorx=False, mirrory=False, displayonly=True):
		print("SVG")
		bounds = self.bounds
		if self.origin == RDFile.ORIGIN_MACHINE_ZERO:
			bounds[0] = 0
			bounds[1] = 0
		width = bounds[2] - bounds[0]
		height = bounds[3] - bounds[1]
		print("BOUNDS")
		tags = ""
		if not displayonly:
			tags += " width='%0.3fmm' height='%0.3fmm'" % (width / 1000.0 + 8, height / 1000.0 + 8)
		else:
			tags += " width='100%'"
		svg = "<svg preserveAspectRatio='xMidYMid meet'%s viewBox='%0.3f %0.3f %0.3f %0.3f'>" % (tags, -4, -4, width / 1000.0 + 8, height / 1000.0 + 8)
		svg += "\n<g transform='scale(%d, %d) translate(%0.3f, %0.3f)'>" % (1 - mirrorx * 2, 1 - mirrory*2, - width / 1000.0 * mirrorx, - height / 1000.0 * mirrory)
		if displayonly:
			for x in range(0, width/10000+2):
				svg += "<path d='M %d %d L %d %d' stroke='#DDD' fill='none' stroke-width='0.1mm' />" % (x * 10 + bounds[0] / 1000.0, bounds[1] / 1000.0 - 5, x * 10 + bounds[0] / 1000.0, bounds[3]/1000.0 + 5)
			for y in range(0, height/10000+2):
				svg += "<path d='M %d %d L %d %d' stroke='#DDD' fill='none' stroke-width='0.1mm' />" % (bounds[0] /1000.0 - 5, bounds[3] / 1000.0 - y * 10, bounds[2] / 1000.0 + 5, bounds[3] / 1000.0 - y * 10)
		for layer in range(len(self.layers)):
			svg += "\n\t"+self.layers[layer].toSVG(bounds[0], bounds[3])
		svg += "\n\t<rect x='-2.5' y='%0.3f' width='5' height='5' fill='#00FF00' stroke='black' stroke-width='0.5' />" % (bounds[3] / 1000.0 - 2.5, )
		svg += "\n</g>"
		svg += "\n</svg>"
		return svg