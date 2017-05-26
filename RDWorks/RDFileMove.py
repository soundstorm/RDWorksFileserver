class RDFileMove(object):
	def __init__(self, x=0, y=0, cut=False, relative=False, cmd=0x00):
		self.x = x
		self.y = y
		self.cut = cut
		self.relative = relative
		self.cmd = cmd
	
	def toString(self):
		return "%s: (%+10d|%+10d) (%s) %02x" % (("Cut " if self.cut else "Move"), self.x, self.y, ("relative" if self.relative else "absolute"), self.cmd)