# -*- coding: utf-8 -*-
"""
This file is for running analysis which require run repeatedly by time intervals
"""

import sys
import string
from datetime import datetime, timedelta
from subprocess import Popen, PIPE
from eventanalyzer.models import Report, ReportResult
from eventanalyzer.conf import settings
from eventanalyzer.output import OutputCSV, OutputMongo


DELTA_TIME_YEAR = 365*24*60*60
DELTA_TIME_MONTH = 30*24*60*60
DELTA_TIME_WEEK = 7*24*60*60
DELTA_TIME_DAY = 24*60*60

PERIOD_CHOICES = {
    'd': DELTA_TIME_DAY,
    'm': DELTA_TIME_MONTH,
    'w': DELTA_TIME_WEEK,
    'y': DELTA_TIME_YEAR,
}

def create_report():
    """
    create report in csv file for analyses by refer argument  
    """
    
    date_now = datetime.now()
    for report in Report.objects.all():
	
	if report.last_report == None or report.last_report <= date_now - timedelta( seconds=PERIOD_CHOICES[report.interval]):
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