class RDFileLaser(object):
	def __init__(self):
		self.enabled = False
		self.minPower = 0
		self.maxPower = 0
		self.bankMinPower = 0
		self.bankMaxPower = 0
		self.throughPower = 0
		self.pwmFrequency = 0
		#self.openDelay = 0
		#self.closeDelay = 0
		self.blowing = False
	
	def toString(self):
		return "Enabled:        %d\nBank Min Power: %0.2f%%\nBank Max Power: %0.2f%%\nMin Power:      %0.2f%%\nMax Power:      %0.2f%%\nThrough Power:  %0.2f%%\nPWM Frequency:  %dHz" % (self.enabled, self.bankMinPower, self.bankMaxPower, self.minPower, self.maxPower, self.throughPower, self.pwmFrequency)