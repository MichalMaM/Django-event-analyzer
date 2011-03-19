"""
This file is test module for using plug-ins
"""
import types
import string
import anyjson
import csv
import codecs
import cStringIO
from pychart import *

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


class OutputBarGraph:
    """
    Drowing data to PNG file
    """

    def set_data(self, title, file_path, data):
	self.title = title
	self.data = data
	self.number_reports = len(data)
	if self.number_reports == 0:
	    self.file_name = file_path+"_NO_DATA.txt"
	else:
	    self.file_name = file_path+".png"
	    self.canvas = canvas.init(self.file_name)

	    output_count = 1
	    for one_out in self.data[0].output_array:
		if output_count == 2:
		    break
		for output in one_out:
		    if len(output) > 1:
			output_count = 2
			break

	    if output_count == 1:
		print "1"
		if self.number_reports == 1: 
		    self.__drow_one_one_report()
		else:
		    self.__drow_one_more_report()
	    else:
		 print "2"
		 self.__drow_more_one_report()
	
    def __drow_one_one_report(self):
	
	report = self.data[0]
	drow_data = []
	max_value = 0
	for index in range(len(report.date_array)):
	    date_elem = report.date_array[index]
	    key, value = report.output_array[index][0].items()[0]
	    if value == "no data":
		continue
	    try:
		value = int(value)
		if value > max_value:
		    max_value = value
	    except ValueError:
		continue
	    drow_data.append((date_elem, value))

	max_value = max_value/10
	if max_value == 0:
	    max_value = 1

	width = len(drow_data)*30
	if width > 5000:
	    width = 5000
	elif width < 600:
	    width = 600

	self.area = area.T(size = (width,740),
	    x_coord = category_coord.T(drow_data, 0),
            y_grid_interval=max_value,
	    x_axis=axis.X(format="/a-60/hL%s", label="Date [s]"),
            y_axis=axis.Y(label="Value [-]"),
            legend = legend.T(), 
	    y_range = (0, None)
	)

	self.area.add_plot(bar_plot.T(label=report.report, data=drow_data))
	self.area.draw(self.canvas)
    

    def __drow_one_more_report(self):

	drow_data = []
	all_data = []
	max_value = 0
	for report in self.data:
	    partition_data = []
	    for index in range(len(report.date_array)):
		date_elem = report.date_array[index]
		key, value = report.output_array[index][0].items()[0]
		if value == "no data":
		    continue
		try:
		    value = int(value)
		    if value > max_value:
			max_value = value
		except ValueError:
		    continue
		partition_data.append((date_elem, value))
	    if len(partition_data) == 0:
		continue
	    all_data.append([report.report, partition_data])
	    drow_data = drow_data + partition_data
	drow_data.sort()

	max_value = max_value/10
	if max_value == 0:
	    max_value = 1

	width = len(drow_data)*30
	if width > 5000:
	    width = 5000
	elif width < 600:
	    width = 600

	self.area = area.T(size = (width,740),
	    x_coord = category_coord.T(drow_data, 0),
            y_grid_interval=max_value,
	    x_axis=axis.X(format="/a-60/hL%s", label="Date [s]"),
            y_axis=axis.Y(label="Value [-]"),
            legend = legend.T(), 
	    y_range = (0, None)
	)
	for plot in all_data:
	    self.area.add_plot(bar_plot.T(label=plot[0], data=plot[1]))
	self.area.draw(self.canvas)

    def __drow_more_one_report(self):
	
	report = self.data[0]
	legend_position = {}
	drow_data = []
	max_value = 0
	used_key = None
	# collect all possible bars for side by side 
	for element in report.output_array:
	    for json_out in element:
		if len(json_out) == 1:
		    break
		else:
		    if used_key == None:
			for key, value in json_out.items():
			    if key != "total" and key != "value":
				used_key = key
				if not legend_position.has_key(str(value)):
				    legend_position[str(value)] = len(legend_position.values()) + 1
				break
		    else:
			value = str(json_out[used_key])
			if not legend_position.has_key(value):
			    legend_position[value] = len(legend_position.values()) + 1
			    
	# construct data for draw	
	for index in range(len(report.output_array)):
	    partition_list = []
	    partition_list.append(report.date_array[index])
	    for i in range(len(legend_position)):
		partition_list.append(0)
	    for json_out in report.output_array[index]:
		if len(json_out) == 1:
		    partition_list = []
		    break
		else:
		    position = legend_position[str(json_out[used_key])]
		    if json_out.has_key("total"):
			value = json_out["total"]
			partition_list[position] = value
			if value > max_value:
			    max_value = value
		    elif json_out.has_key("value"):
			value = json_out["value"]
			partition_list[position] = value
			if value > max_value:
			    max_value = value
			
	    if len(partition_list) > 1:
		drow_data.append(partition_list)

	max_value = max_value/10
	if max_value == 0:
	    max_value = 1

	same_mark = len(drow_data[0])-1
	width = len(drow_data)*same_mark*30
	if width > 5000:
	    width = 5000
	elif width < 600:
	    width = 600

	self.area = area.T(size = (width,740),
	    x_coord = category_coord.T(drow_data, 0),
            y_grid_interval=max_value,
	    x_axis=axis.X(format="/a-60/hL%s", label="Date [s]"),
            y_axis=axis.Y(label="Value [-]"),
            legend = legend.T(), 
	    y_range = (0, None)
	)

	chart_object.set_defaults(bar_plot.T, direction="vertical", data=drow_data)
	
	data_labels = legend_position.items()[:]
	data_labels.sort(key=lambda number: number[1])
	
	for i in range(len(drow_data[0])-1) :
	    self.area.add_plot(bar_plot.T(label=font.quotemeta(data_labels[i][0]), hcol=i+1, cluster=(i,len(drow_data[0])-1)))

	self.area.draw(self.canvas)
	

    def get_output_file(self):
	return self.file_name
