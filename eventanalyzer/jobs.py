# -*- coding: utf-8 -*-
"""
This file is for running analysis which require run repeatedly by time intervals
"""

import sys
import string
from datetime import datetime
from subprocess import Popen, PIPE
from eventanalyzer.models import Report, ReportResult
from eventanalyzer.conf import settings
from eventanalyzer.output import OutputCSV, OutputMongo

PERIOD_CHOICES = {
    'd': 'day',
    'm': 'month',
    'w': 'week',
    'y': 'year',
}

def create_report():
    """
    create report in csv file for analyses by refer argument  
    """
    if len(sys.argv) != 2:
	print "error - correct use of this script: "+sys.argv[0]+" [time interval]"
	return False

    try:
	PERIOD_CHOICES[sys.argv[1]]
    except:
	print "error - correct use of this script: "+sys.argv[0]+" [time interval]"
	return False
    
    for report in Report.objects.filter(interval=sys.argv[1]):
	
	db_query = report.db_query
	print db_query
	if string.find(db_query, "count(") == -1:
	    db_query = db_query+".forEach(printjson)"
	    print db_query

	try:
	    process = Popen(["mongo", "--eval", db_query, settings.MONGODB_DB], stdout=PIPE)
	    output_shell = process.communicate()[0]
	    if process.returncode != 0:
		print "error - bad mongo query "
		return False
	except e:
	    print "error - mongo error: ", e[0]
	    return False
	
	print output_shell
	index = string.find(output_shell, "{")
	if index == -1:
	    analyse_list = string.split(output_shell, "\n")
	    try:
		analyse_element = int(analyse_list[3])
		full_analyse = [{"count" : analyse_element}]
	    except ValueError:
		full_analyse = [{"data" : "no data"}]
	else:
	    output_shell = output_shell[index:]
	    mongo_output = OutputMongo(output_shell)
	    full_analyse = mongo_output.getoutput()
	
	run_date = datetime.now()
	csv_file = "report"+"_"+report.title+"_"+str(run_date.year)+"_"+str(run_date.month)+"_"+str(run_date.day)+".csv"
	csv_out = OutputCSV(settings.REPORT_PATH+csv_file)
	for element in full_analyse:
	    csv_out.addrecord(element)
	csv_out.closefile()

	report.last_report = run_date
	report.save()
	
	result = ReportResult(report=report, output= csv_out.csv, run_date=run_date)
	result.save()

    return True



if __name__ == "__main__":
    create_report()