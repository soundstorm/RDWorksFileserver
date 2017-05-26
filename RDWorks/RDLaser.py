
# encoding: utf-8
import socket
import sys
reload(sys)
sys.setdefaultencoding('utf8')

class RDLaser(object):
	BUF_SIZE = 4096
	CLIENT_PORT = 40200
	SERVER_PORT = 50200

	CMD_STOP                 = "d801".decode("HEX")
	CMD_PAUSE_CONTINUE       = "d803".decode("HEX")
	CMD_HOME_XY              = "d9100000000000000000000000".decode("HEX") #goto abs coord (0|0)
	CMD_HOME_Z               = "d82c".decode("HEX")
	CMD_HOME_U               = "de25".decode("HEX")
	CMD_FOCUS                = "dea5".decode("HEX")

	HANDSHAKE                = "da00057e".decode("HEX")
	
	STATUS                   = "da000004".decode("HEX")
	
	CFG_X_SETTINGS           = "da000020".decode("HEX") #binary
	CFG_X_STEP_LENGTH        = "da000021".decode("HEX") #picometer
	CFG_X_MAX_SPEED          = "da000023".decode("HEX") #nanometer/s
	CFG_X_JUMPOFF_SPEED      = "da000024".decode("HEX") #nanometer/s
	CFG_X_MAX_ACC            = "da000025".decode("HEX") #nanometer/s^2
	CFG_X_BREADTH            = "da000026".decode("HEX") #nanometer
	CFG_X_KEY_JUMPOFF_SPEED  = "da000027".decode("HEX") #nanometer/s
	CFG_X_KEY_ACC            = "da000028".decode("HEX") #nanometer/s^2
	CFG_X_ESTOP_ACC          = "da000029".decode("HEX") #nanometer/s^2
	CFG_X_HOME_OFFSET        = "da00002a".decode("HEX") #nanometer

	CFG_X_SETTINGS           = "da000030".decode("HEX") #binary
	CFG_Y_STEP_LENGTH        = "da000031".decode("HEX") #picometer
	CFG_Y_MAX_SPEED          = "da000033".decode("HEX") #nanometer/s
	CFG_Y_JUMPOFF_SPEED      = "da000034".decode("HEX") #nanometer/s
	CFG_Y_MAX_ACC            = "da000035".decode("HEX") #nanometer/s^2
	CFG_Y_BREADTH            = "da000036".decode("HEX") #nanometer
	CFG_Y_KEY_JUMPOFF_SPEED  = "da000037".decode("HEX") #nanometer/s
	CFG_Y_KEY_ACC            = "da000038".decode("HEX") #nanometer/s^2
	CFG_Y_ESTOP_ACC          = "da000039".decode("HEX") #nanometer/s^2
	CFG_Y_HOME_OFFSET        = "da00003a".decode("HEX") #nanometer

	CFG_Z_SETTINGS           = "da000040".decode("HEX") #binary
	CFG_Z_STEP_LENGTH        = "da000041".decode("HEX") #picometer
	CFG_Z_MAX_SPEED          = "da000043".decode("HEX") #nanometer/s
	CFG_Z_JUMPOFF_SPEED      = "da000044".decode("HEX") #nanometer/s
	CFG_Z_MAX_ACC            = "da000045".decode("HEX") #nanometer/s^2
	CFG_Z_BREADTH            = "da000046".decode("HEX") #nanometer
	CFG_Z_KEY_JUMPOFF_SPEED  = "da000047".decode("HEX") #nanometer/s
	CFG_Z_KEY_ACC            = "da000048".decode("HEX") #nanometer/s^2
	CFG_Z_ESTOP_ACC          = "da000049".decode("HEX") #nanometer/s^2
	CFG_Z_HOME_OFFSET        = "da00004a".decode("HEX") #nanometer

	CFG_U_SETTINGS           = "da000050".decode("HEX") #binary
	CFG_U_STEP_LENGTH        = "da000051".decode("HEX") #picometer
	CFG_U_MAX_SPEED          = "da000053".decode("HEX") #nanometer/s
	CFG_U_JUMPOFF_SPEED      = "da000054".decode("HEX") #nanometer/s
	CFG_U_MAX_ACC            = "da000055".decode("HEX") #nanometer/s^2
	CFG_U_BREADTH            = "da000056".decode("HEX") #nanometer
	CFG_U_KEY_JUMPOFF_SPEED  = "da000057".decode("HEX") #nanometer/s
	CFG_U_KEY_ACC            = "da000058".decode("HEX") #nanometer/s^2
	CFG_U_ESTOP_ACC          = "da000059".decode("HEX") #nanometer/s^2
	CFG_U_HOME_OFFSET        = "da00005a".decode("HEX") #nanometer

	CFG_LASER12_TYPE         = "da000010".decode("HEX") #binary
	# glass/RF/RF+preignition
	CFG_LASER34              = "da000226".decode("HEX") #binary

	CFG_LASER1_FREQUENCE     = "da000011".decode("HEX") #Hz
	CFG_LASER1_POWER_MIN     = "da000012".decode("HEX") #percent
	CFG_LASER1_POWER_MAX     = "da000013".decode("HEX") #percent
	CFG_LASER1_PREIG_FREQ    = "da00001a".decode("HEX") #Hz
	CFG_LASER1_PREIG_PULSE   = "da00001b".decode("HEX") #1/10 percent

	CFG_LASER2_FREQUENCE     = "da000017".decode("HEX") #Hz
	CFG_LASER2_POWER_MIN     = "da000018".decode("HEX") #percent
	CFG_LASER2_POWER_MAX     = "da000019".decode("HEX") #percent
	CFG_LASER2_PREIG_FREQ    = "da00001c".decode("HEX") #Hz
	CFG_LASER2_PREIG_PULSE   = "da00001d".decode("HEX") #1/10 percent

	CFG_LASER3_POWER_MIN     = "da000063".decode("HEX") #percent
	CFG_LASER3_POWER_MAX     = "da000064".decode("HEX") #percent
	CFG_LASER3_FREQUENCE     = "da000065".decode("HEX") #Hz
	CFG_LASER3_PREIG_FREQ    = "da000066".decode("HEX") #Hz
	CFG_LASER3_PREIG_PULSE   = "da000067".decode("HEX") #1/10 percent

	CFG_LASER4_POWER_MIN     = "da000068".decode("HEX") #percent
	CFG_LASER4_POWER_MAX     = "da000069".decode("HEX") #percent
	CFG_LASER4_FREQUENCE     = "da00006a".decode("HEX") #Hz
	CFG_LASER4_PREIG_FREQ    = "da00006b".decode("HEX") #Hz
	CFG_LASER4_PREIG_PULSE   = "da00006c".decode("HEX") #1/10 percent

	CFG_LASER_ATTENUATION    = "da000016".decode("HEX") #1/10 percent
	CFG_HEAD_DISTANCE        = "da00001e".decode("HEX") #nanometer
	CFG_ENABLE_AUTOLAYOUT    = "da000004".decode("HEX") #binary
	#02cfd48989e9
	CFG_FEED_TRANSMISSION    = "da000200".decode("HEX") #binary
	CFG_BROKEN_DELAY         = "da00020d".decode("HEX") #milliseconds

	LASER_STATE              = "da000400".decode("HEX")

	TOTAL_ON_TIME            = "da000401".decode("HEX") #seconds
	TOTAL_PROCESSING_TIME    = "da000402".decode("HEX") #seconds
	TOTAL_TRAVEL_X           = "da000423".decode("HEX") #meters
	TOTAL_TRAVEL_Y           = "da000433".decode("HEX") #meters
	TOTAL_PROCESSING_TIMES   = "da000403".decode("HEX") #count
	TOTAL_LASER_ON_TIME      = "da000411".decode("HEX") #seconds
	PREVIOUS_PROCESSING_TIME = "da00048f".decode("HEX") #milliseconds
	PREVIOUS_WORK_TIME       = "da000408".decode("HEX") #milliseconds
	MAINBOARD_VERSION        = "da00057f".decode("HEX") #string

	POSITION_AXIS_X          = "da000421".decode("HEX") #nanometer
	POSITION_AXIS_Y          = "da000431".decode("HEX") #nanometer
	POSITION_AXIS_Z          = "da000441".decode("HEX") #nanometer
	POSITION_AXIS_U          = "da000451".decode("HEX") #nanometer
	
	# thanks to http://stefan.schuermans.info/rdcam/scrambling.html
	MAGIC = 0x88
	
	values = {
		STATUS                   : 0,
		CFG_X_SETTINGS           : 0,
		CFG_X_STEP_LENGTH        : 0,
		CFG_X_MAX_SPEED          : 0,
		CFG_X_JUMPOFF_SPEED      : 0,
		CFG_X_MAX_ACC            : 0,
		CFG_X_BREADTH            : 0,
		CFG_X_KEY_JUMPOFF_SPEED  : 0,
		CFG_X_KEY_ACC            : 0,
		CFG_X_ESTOP_ACC          : 0,
		CFG_X_HOME_OFFSET        : 0,
		CFG_X_SETTINGS           : 0,
		CFG_Y_STEP_LENGTH        : 0,
		CFG_Y_MAX_SPEED          : 0,
		CFG_Y_JUMPOFF_SPEED      : 0,
		CFG_Y_MAX_ACC            : 0,
		CFG_Y_BREADTH            : 0,
		CFG_Y_KEY_JUMPOFF_SPEED  : 0,
		CFG_Y_KEY_ACC            : 0,
		CFG_Y_ESTOP_ACC          : 0,
		CFG_Y_HOME_OFFSET        : 0,
		CFG_Z_SETTINGS           : 0,
		CFG_Z_STEP_LENGTH        : 0,
		CFG_Z_MAX_SPEED          : 0,
		CFG_Z_JUMPOFF_SPEED      : 0,
		CFG_Z_MAX_ACC            : 0,
		CFG_Z_BREADTH            : 0,
		CFG_Z_KEY_JUMPOFF_SPEED  : 0,
		CFG_Z_KEY_ACC            : 0,
		CFG_Z_ESTOP_ACC          : 0,
		CFG_Z_HOME_OFFSET        : 0,
		CFG_U_SETTINGS           : 0,
		CFG_U_STEP_LENGTH        : 0,
		CFG_U_MAX_SPEED          : 0,
		CFG_U_JUMPOFF_SPEED      : 0,
		CFG_U_MAX_ACC            : 0,
		CFG_U_BREADTH            : 0,
		CFG_U_KEY_JUMPOFF_SPEED  : 0,
		CFG_U_KEY_ACC            : 0,
		CFG_U_ESTOP_ACC          : 0,
		CFG_U_HOME_OFFSET        : 0,
		CFG_LASER12_TYPE         : 0,
		CFG_LASER34              : 0,
		CFG_LASER1_FREQUENCE     : 0,
		CFG_LASER1_POWER_MIN     : 0,
		CFG_LASER1_POWER_MAX     : 0,
		CFG_LASER1_PREIG_FREQ    : 0,
		CFG_LASER1_PREIG_PULSE   : 0,
		CFG_LASER2_FREQUENCE     : 0,
		CFG_LASER2_POWER_MIN     : 0,
		CFG_LASER2_POWER_MAX     : 0,
		CFG_LASER2_PREIG_FREQ    : 0,
		CFG_LASER2_PREIG_PULSE   : 0,
		CFG_LASER3_POWER_MIN     : 0,
		CFG_LASER3_POWER_MAX     : 0,
		CFG_LASER3_FREQUENCE     : 0,
		CFG_LASER3_PREIG_FREQ    : 0,
		CFG_LASER3_PREIG_PULSE   : 0,
		CFG_LASER4_POWER_MIN     : 0,
		CFG_LASER4_POWER_MAX     : 0,
		CFG_LASER4_FREQUENCE     : 0,
		CFG_LASER4_PREIG_FREQ    : 0,
		CFG_LASER4_PREIG_PULSE   : 0,
		CFG_LASER_ATTENUATION    : 0,
		CFG_HEAD_DISTANCE        : 0,
		CFG_ENABLE_AUTOLAYOUT    : 0,
		CFG_FEED_TRANSMISSION    : 0,
		CFG_BROKEN_DELAY         : 0,
		LASER_STATE              : 0,
		TOTAL_ON_TIME            : 0,
		TOTAL_PROCESSING_TIME    : 0,
		TOTAL_TRAVEL_X           : 0,
		TOTAL_TRAVEL_Y           : 0,
		TOTAL_PROCESSING_TIMES   : 0,
		TOTAL_LASER_ON_TIME      : 0,
		PREVIOUS_PROCESSING_TIME : 0,
		PREVIOUS_WORK_TIME       : 0,
		MAINBOARD_VERSION        : "RDLaser.py 1.0 by sndstrm",
		POSITION_AXIS_X          : 0,
		POSITION_AXIS_Y          : 0,
		POSITION_AXIS_Z          : 0,
		POSITION_AXIS_U          : 0
	}
	__server__ = None
	__client__ = None

	'''
	Generates checksum.
	Params:
	s	Scrambled string
	'''
	@staticmethod
	def checksum(s):
		cs = 0
		for i in range(0, len(s)):
			cs += ord(s[i])
		return chr((cs >> 8) & 0xFF) + chr(cs & 0xFF) + s

	'''
	Scrambles plain char
	Params:
	p	Char to scramble
	'''
	@staticmethod
	def scramble(p):
		a = (p & 0x7E) | ((p >> 7) & 0x01) | ((p << 7) & 0x80)
		b = a ^ RDLaser.MAGIC
		s = (b + 1) & 0xFF
		return s

	'''
	Scrambles plain string
	Params:
	string	String to scramble
	'''
	@staticmethod
	def scramblestr(string):
		s = ""
		for c in string:
			s += chr(RDLaser.scramble(ord(c)))
		return s

	'''
	Descrambles scrambled char
	Params:
	s	Char to descramble
	'''
	@staticmethod
	def descramble(s):
		a = (s + 0xFF) & 0xFF
		b = a ^ RDLaser.MAGIC
		p = (b & 0x7E) | ((b >> 7) & 0x01) | ((b << 7) & 0x80)
		return p

	'''
	Descrambles scrambled string
	Params:
	string	String to descramble
	'''
	@staticmethod
	def descramblestr(string):
		p = ""
		for c in string:
			p += chr(RDLaser.descramble(ord(c)))
		return p

	# transmitted as 7-bit, 0x80 is reserved (but would be semi-valid here too)
	@staticmethod
	def fromNumber(n, bytes=5):
		s = ""
		for i in range(-bytes+1, 1):
			s += chr((n >> (-7 * i)) & 0x7F)
		return s
	
	@staticmethod
	def toNumber(s, chars=5):
		n = 0
		for i in range(-chars, 0):
			n |= ord(s[i]) << (-7 * (i+1))
		return n
	
	# Just allow one instance of server
	@staticmethod
	def getServer():
		if RDLaser.__server__ == None:
			RDLaser.__server__ = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			RDLaser.__server__.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			RDLaser.__server__.bind(('', RDLaser.SERVER_PORT))
		return RDLaser.__server__
	
	# Just allow one instance of client
	@staticmethod
	def getClient():
		if RDLaser.__client__ == None:
			RDLaser.__client__ = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			RDLaser.__client__.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			RDLaser.__client__.bind(('', RDLaser.CLIENT_PORT))
			RDLaser.__client__.settimeout(1)
		return RDLaser.__client__
	
	@staticmethod
	def disconnectServer():
		if RDLaser.__server__ == None:
			return
		RDLaser.__server__.close()
		RDLaser.__server__ = None
	
	@staticmethod
	def disconnectClient():
		if RDLaser.__client__ == None:
			return
		RDLaser.__client__.close()
		RDLaser.__client__ = None