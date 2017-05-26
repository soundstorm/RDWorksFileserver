from RDWorks.RDFileLaser import RDFileLaser
from RDWorks.RDFileMove import RDFileMove

class RDFileLayer(object):
	CUT        = 0x01
	BI_DIR_X   = 0x02
	UNI_DIR_X  = 0x04
	BI_DIR_Y   = 0x08
	UNI_DIR_Y  = 0x10
	AIR_ENABLE = 0x80
	
	def __init__(self):
		self.laser1 = RDFileLaser()
		self.laser2 = RDFileLaser()
		self.laser3 = RDFileLaser()
		self.laser4 = RDFileLaser()
		self.lasers = [self.laser1, self.laser2, self.laser3, self.laser4]
		self.scanOpenDelay = 0
		self.scanCloseDelay = 0
		self.openDelay = 0
		self.closeDelay = 0
		self.IOs = 0
		self.speed = 0
		self.penspeed = 0
		self.color = 0
		self.sx = 0
		self.sy = 0
		self.lx = 0
		self.ly = 0
		self.function = 0
		self.bounds = [0, 0, 0, 0]
		self.moves = []
	
	def toString(self):
		movestr = ""
		#for move in self.moves:
		#	movestr += move.toString()+"\n"
		return "Laser 1:\n%s\nLaser 2:\n%s\nLaser 3:\n%s\nLaser 4:\n%s\nIOs: %s\nSpeed: %d\nPen Speed: %d\nColor: #%06x\n(%d|%d) (%d|%d)\nFunction: %s\nMoves:\n%s" % (self.laser1.toString(), self.laser2.toString(), self.laser3.toString(), self.laser4.toString(), bin(self.IOs),  self.speed, self.penspeed, self.color, self.sx, self.sy, self.lx, self.ly, bin(self.function), movestr)
	
	def toAbsolute(self):
		x = 0
		y = 0
		for move in self.moves:
			if move.relative:
				x += move.x
				y += move.y
				move.x = x
				move.y = y
				move.relative = False
			else:
				x = move.x
				y = move.y
	
	def toRelative(self):
		x = 0
		y = 0
		for move in self.moves:
			if move.relative:
				x += move.x
				y += move.y
				move.x = x
				move.y = y
			else:
				_x = move.x - x
				_y = move.y - y
				x = move.x
				y = move.y
				move.x = _x
				move.y = _y
				move.relative = True
	
	def toSVG(self, xneg, ypos):
		if len(self.moves) == 0:
			return ""
		self.toAbsolute()
		path = "M %0.3f %0.3f" % ((self.moves[0].x - xneg) / 1000.0, (ypos - self.moves[0].y)/1000.0)
		for move in self.moves[1:]:
			if move.cut:
				path += " L %0.3f %0.3f" % ((move.x - xneg) / 1000.0, (ypos - move.y)/1000.0)
			else:
				path += " M %0.3f %0.3f" % ((move.x - xneg) / 1000.0, (ypos - move.y)/1000.0)
		return "<path d='%s' stroke='#%06x' fill='none' stroke-width='0.1mm' />" % (path, self.color)
		