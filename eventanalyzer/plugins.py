"""
This file is test module for using plug-ins
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

    def set_data(self, title, file_path, data):
	self.file_name = file_path+".csv"
	self.csv_file = open(self.file_name, "wb")
	#self.file_out = csv.writer(open(file_name, "wb"), delimiter=",", quoting=csv.QUOTE_MINIMAL)
	self.file_out = UnicodeWriter(self.csv_file, delimiter=",", quoting=csv.QUOTE_MINIMAL)
	#self.csv = ""
	for record in data:
	    self.__addrecord(record)
	self.__closefile()

    def __addrecord(self, record):
	for index in range(len(record.date_array)):
	    for data_json in record.output_array[index]:
		csv_record = []
		csv_record.append(record.report)
		csv_record.append(record.date_array[index].strftime("%Y-%m-%d:%H:%M:%S"))
		shorted_keys = data_json.keys()
		shorted_keys.sort()
		for element in shorted_keys:
		    if type(data_json[element]) == types.UnicodeType:
			csv_record.append(data_json[element])
		    else:
			csv_record.append(str(data_json[element]))
		self.file_out.writerow(csv_record)
	

    def __closefile(self):
	self.csv_file.close()

    def get_output_file(self):
	return self.file_name