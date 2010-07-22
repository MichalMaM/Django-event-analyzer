import types


class OutputCSV:
    def __init__(self, file_name):
	self.file_out = open(file_name, "w")
	self.csv = ""

    def addrecord(self, record):
	csv_line = ""
	for element in record:
	    if type(record[element]) == types.DictType:
		for atom in record[element]:
		    csv_line = csv_line +`record[element][atom]`+", "
	    else:
		csv_line = csv_line +`record[element]`+", "
	csv_line = csv_line[0:-2]+"\n"
	self.csv += csv_line  
	self.file_out.write(csv_line)
    
    def closefile(self):
	self.file_out.close()