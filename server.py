from RDWorks.RDLaser import RDLaser
from RDWorks.RDServer import RDServer

RDServer.debug=True
RDLaser.values[RDLaser.CFG_X_BREADTH] = 700000
RDLaser.values[RDLaser.CFG_Y_BREADTH] = 500000
server = RDServer()
server.start()
