import types
import string
import anyjson

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


class OutputMongo:
    def __init__(self, output_shell):
	self.output_shell = output_shell
	
    
    def getoutput(self):
	output_records = []
	output_shell = self.output_shell
	while string.find(output_shell, "\n{") != -1:
	    index = string.find(output_shell, "\n{")
	    record = output_shell[:index]
	    record = string.replace(record, "\n", "")
	    record = string.replace(record, "\t", "")
	    try:
		#print "zaznam: "+record
		output_records.append(anyjson.deserialize(record))
	    except ValueError, e:
		print "error in translate from json format"
	    #print "zbytek: "+output_shell[index+1:]
	    output_shell = output_shell[index+1:]

	output_shell=string.replace(output_shell, "\n", "")
	output_shell=string.replace(output_shell, "\t", "")
	output_records.append(anyjson.deserialize(output_shell))
	return output_records
	    
	