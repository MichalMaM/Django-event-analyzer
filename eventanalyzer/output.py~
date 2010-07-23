"""
This file contains two classes for processing output from mongo shell
"""
import types
import string
import anyjson

class OutputCSV:
    """
    Saving data to csv file
    """
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
    """
    Processing string output from mongo shell to dictionary 
    """
    def __init__(self, output_shell):
	self.output_shell = output_shell

    def __controljson(self, record):
	record = string.replace(record, "ObjectId(", "")
	record = string.replace(record, '")', '"')
	return record

    def __nextdata(self, record):
	edit_record = record[1:len(record)-1]
	left_index = string.find(edit_record, "{")
	right_index = string.find(edit_record, "}")
	sub_record = edit_record[left_index:right_index+1]
	sub_record = anyjson.deserialize(sub_record)
	edit_record = record[0:left_index+1]+'"%s"'+record[right_index+2:len(record)]
	edit_record = anyjson.deserialize(edit_record)
	edit_record["params"] = sub_record
	return edit_record
    
    def getoutput(self):
	output_records = []
	output_shell = self.output_shell
	while string.find(output_shell, "\n{") != -1:
	    index = string.find(output_shell, "\n{")
	    record = output_shell[:index]
	    record = string.replace(record, "\n", "")
	    record = string.replace(record, "\t", "")
	    if string.find(record, "ObjectId(") >=0:
		record = self.__controljson(record)
	    if string.find(record[1:len(record)-1], "{") >=0:
		new_record = self.__nextdata(record)
		output_records.append(new_record)
	    else:
		#try:
		    #print "zaznam: "+record
		output_records.append(anyjson.deserialize(record))
		#except ValueError, e:
		    #print "error in translate from json format"
	    #print "zbytek: "+output_shell[index+1:]
	    output_shell = output_shell[index+1:]

	output_shell=string.replace(output_shell, "\n", "")
	output_shell=string.replace(output_shell, "\t", "")
	
	if string.find(output_shell, "ObjectId(") >=0:
	    output_shell = self.__controljson(output_shell)
	if string.find(output_shell[1:len(output_shell)-1], "{") >=0:
	    output_shell = self.__nextdata(output_shell)
	    output_records.append(output_shell)
	else:
	    output_records.append(anyjson.deserialize(output_shell))
	
	return output_records
	    
	