from RDWorks.RDFile import RDFile
		
f = RDFile()
f.parseFile("rdfiles/M.rd")
svg = open("rdfiles/M.svg", "w")
svg.write(f.toSVG(True, True))
svg.close()