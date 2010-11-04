# -*- coding: utf-8 -*-
"""
This file contains two classes for processing output from mongo shell
"""
import types
import string
import anyjson
import csv
import codecs
import cStringIO

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)
	return data

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


class OutputCSV:
    """
    Saving data to csv file
    """
    def __init__(self, file_name):
	self.csv_file = open(file_name, "wb")
	#self.file_out = csv.writer(open(file_name, "wb"), delimiter=",", quoting=csv.QUOTE_MINIMAL)
	self.file_out = UnicodeWriter(self.csv_file, delimiter=",", quoting=csv.QUOTE_MINIMAL)
	self.csv = ""

    def addrecord(self, record):
	csv_line = []
	shorted_keys = record.keys()
	shorted_keys.sort()
	for element in shorted_keys:
	    if type(record[element]) == types.DictType:
		second_keys = record[element].keys()
		second_keys.sort()
		for atom in second_keys:
		    if type(record[element][atom]) == types.UnicodeType:
			csv_line.append(record[element][atom])
		    else:
			csv_line.append(str(record[element][atom]))
	    else:
		if type(record[element]) == types.UnicodeType:
		    csv_line.append(record[element])
		else:
		    csv_line.append(str(record[element]))
	
	#self.csv += string.join(csv_line,",")+"\n"
	encoded_data = self.file_out.writerow(csv_line)
	print encoded_data
	self.csv += encoded_data

    def closefile(self):
	self.csv_file.close()



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
		output_records.append(anyjson.deserialize(record))
	
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
	    
	