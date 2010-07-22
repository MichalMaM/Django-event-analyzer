"""
This file is for running analysis which require run repeatedly by time intervals
"""
import sys
from datetime import datetime
from subprocess import Popen, PIPE
#from django.db import transaction
from eventanalyzer.models import Report, ReportArchive, ReportResult
from eventanalyzer.conf import settings
from eventanalyzer.output import OutputCSV

PERIOD_CHOICES = {
    'd': 'day',
    'm': 'month',
    'w': 'week',
    'y': 'year',
}

#@transaction.commit_on_success
def create_report():
    """
    create report in csv file for analyses by refer argument  
    """
    if len(sys.argv) != 2:
	print "error - correct use of this script: "+sys.argv[0]+" [time interval]"
	return False
    #test argumentu
    print sys.argv[0], " : ", sys.argv[1]
    try:
	PERIOD_CHOICES[sys.argv[1]]
    except:
	print "error - correct use of this script: "+sys.argv[0]+" [time interval]"
	return False
    
    #
    print Report.objects.filter(interval=sys.argv[1])
    for report in Report.objects.filter(interval=sys.argv[1]):
	#proved analyzu na mongu => report.db_query

	#
	print report.db_query
	try:
	    output_shell = Popen(["mongo", "--eval", report.db_query+".forEach(printjson)", settings.MONGODB_DB], stdout=PIPE).communicate()[0]
	except:
	    print "error - bad mongo query"
	    return False
	#
	#print full_analyse
	#for x in full_analyse:
	#    print x
	
	run_date = datetime.now()
	csv_file = "report"+"_"+report.title+"_"+`run_date.year`+"_"+`run_date.month`+"_"+`run_date.day`+".csv"
	csv_out = OutputCSV(settings.REPORT_PATH+csv_file)
	for element in full_analyse:
	    csv_out.addrecord(element)
	csv_out.closefile()
	

	try:
	    result_report = ReportResult.objects.get(report=report)
	    result_report.last_report = run_date
	    result_report.save()
	except:
	    result_report = ReportResult(report=report, last_report= run_date)
	    result_report.save()
	
	archive = ReportArchive(report=report, output= csv_out.csv, run_date=run_date)
	archive.save()
	
    #
    print "OK"
    return True



if __name__ == "__main__":
    create_report()