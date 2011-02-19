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

class OutputResult:
    """
    Class that is used for saving data from results of reports
    """
    def __init__(self, report = None, date_array=[], output_array=[]):
	self.report = report
	self.date_array = date_array
	self.output_array = output_array


class OutputMongo:
    """
    Processing string output from mongo shell to dictionary 
    """
    def __init__(self, output_shell):
	self.output_shell = output_shell
    
    def getoutput(self):
	output_records = []
	output_shell = self.output_shell

	while True:
	    if string.find(output_shell, "{") != -1:
		break
	    first_index = string.find(output_shell, "{")
	    last_index = string.find(output_shell, "}")
	    record = output_shell[first_index:last_index+1]
	    record = string.replace(record, "\n", "")
	    record = string.replace(record, "\t", "")
	    output_records.append(anyjson.deserialize(record))
	    output_shell = output_shell[last_index+1]

	return output_records
	    
	