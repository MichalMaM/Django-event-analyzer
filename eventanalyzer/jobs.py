"""
This file is for running analysis and data reports that require run repeatedly by cron 
"""
import pkg_resources
import sys
import string
import pymongo
from datetime import datetime, timedelta
from subprocess import Popen, PIPE
from eventanalyzer.models import Report, ReportResult, Analysis, AnalysisResult, get_mongo_collection
from eventanalyzer.conf import settings
from eventanalyzer.output import OutputMongo, OutputResult 
from eventanalyzer.plugins import OutputCSV

DELTA_TIME_YEAR = 365*24*60*60
DELTA_TIME_MONTH = 30*24*60*60
DELTA_TIME_WEEK = 7*24*60*60
DELTA_TIME_DAY = 24*60*60
DELTA_TIME_NOW = 1

PERIOD_CHOICES = {
    'n': DELTA_TIME_NOW,
    'd': DELTA_TIME_DAY,
    'm': DELTA_TIME_MONTH,
    'w': DELTA_TIME_WEEK,
    'y': DELTA_TIME_YEAR,
}

PLUG_INS = {}
for dist in pkg_resources.working_set.iter_entry_points("output.plugins.0.01"):
    try:
	PLUG_INS[dist.name] = dist.load()
	#print PLUG_INS[dist.name]
    except ImportError, err:
        print "Error while loading command %s: %s" % (dist.name, str(err))


def execute_query(db_query, report, run_date):
    """
    execute query from report in mongo db and save result  
    """
    print db_query+"\n"
    try:
	process = Popen(["mongo","--host", string.join(settings.MONGODB_HOSTS), "--eval", db_query, settings.MONGODB_DB], stdout=PIPE)
	output_shell = process.communicate()[0]
	if process.returncode != 0:
	    print "error - can not execute mongo query "
	    return False
    except e:
	print "error - mongo error: ", e[0]
	return False
	
    print output_shell
    index = string.find(output_shell, "{")
    if index == -1:
	analyse_list = string.split(output_shell, "\n")
	try:
	    analyse_element = int(analyse_list[-2])
	    output = '{"count" : %s}' % (analyse_element)
	except ValueError:
	    output = '{"data" : "no data"}'
    else:
	output = output_shell[index:]
	#mongo_output = OutputMongo(output_shell)
	#full_analyse = mongo_output.getoutput()
	
    report.last_report = run_date
    report.save()
	
    result = ReportResult(report=report, output=output, run_date=run_date)
    result.save()
    return True

def check_query(report):
    """
    check if query is good   
    """

    if string.find(report.db_query, "count(") != -1:
	if report.db_query[len(report.db_query) - 1] == ")" or report.db_query[len(report.db_query) - 1] == ";":
	    db_query = report.db_query
	else:
	    print "error - unsupported query: report title: %s, id: %s" % (report.title, report.id)
	    return (False, '')
    elif string.find(report.db_query, "group(") != -1 or string.find(report.db_query, "mapReduce(") != -1:
	if report.db_query[len(report.db_query) - 1] == ")":
	    if string.find(report.db_query, "forEach(printjson)") == -1:
		db_query = report.db_query+".forEach(printjson)"
	    else:
		db_query = report.db_query
	elif report.db_query[len(report.db_query) - 1] == ";":
	    if string.find(report.db_query, "forEach(printjson)") == -1:
		db_query = report.db_query[0:len(report.db_query) - 1]+".forEach(printjson)"
	    else:
		db_query = report.db_query
	else:
	    print "error - unsupported query: report title: %s, id: %s" % (report.title, report.id)
	    return (False, '')
    else:
	print "error - unsupported query: report title: %s, id: %s" % (report.title, report.id)
	return (False, '')

    return (True, db_query)

def execute_past_reports(report, db_query, date_from, date_to, date_now):
    """
    excuted reports results for past periods for given report
    """
    if report.last_report == None and report.interval != 'n' and date_from != None:
	date_from_var = date_from
	date_to_var = date_to
	run_date = date_now
	#report.date_from must be found in db if date_form is not set
	if report.date_from == None:
	    collection = get_mongo_collection()
	    for record in collection.find().sort("timestamp", pymongo.ASCENDING).limit(1):
		report_date_from = record["timestamp"]
	else:
	    report_date_from = report.date_from
	while True:
	    if date_from_var <= report_date_from:
		break
	    # replace date patterns
	    db_query_var = db_query
	    if date_from_var != None:
		date_from_var = date_from_var - timedelta( seconds=PERIOD_CHOICES[report.interval])
		db_query_var = string.replace(db_query_var, "${{d1}}", "new Date(%s,%s,%s)" % (date_from_var.year, date_from_var.month - 1, date_from_var.day))
	    if date_to_var != None:
		date_to_var = date_to_var - timedelta( seconds=PERIOD_CHOICES[report.interval])
		db_query_var = string.replace(db_query_var, "${{d2}}", "new Date(%s,%s,%s)" % (date_to_var.year, date_to_var.month - 1, date_to_var.day))
		    
	    run_date = run_date - timedelta( seconds=PERIOD_CHOICES[report.interval])
	    if not execute_query(db_query_var, report, run_date):
		print "error in past generate - unsupported query: report title: %s, id: " % (report.title, report.id)
		break

    return True
    

def process_output_reports(results, analysis, date_now):
    """
    process result data depending on selected plug-in   
    """
    #PLUG_INS[analysis.plug_in].set_data(analysis.title, file_path, results)
    output = PLUG_INS[analysis.plug_in]()
    file_path = settings.REPORT_PATH+"/analysis%s_%s_%s_%s_%s_%s_%s" % (analysis.id, date_now.year, date_now.month, date_now.day, date_now.hour, date_now.minute, date_now.second)
    output.set_data(analysis.title, file_path, results)

    result = AnalysisResult(analysis=analysis, output=string.split(output.get_output_file(), "/")[-1], run_date=date_now)
    result.save() 
    analysis.last_report = date_now
    analysis.save()
    return True

def create_analysis():
    """
    create results of analysis by analysis properties  
    """
    
    date_now = datetime.now()
    for analysis in Analysis.objects.filter(activated=True):
	
	if analysis.last_report == None or analysis.last_report <= date_now - timedelta( seconds=PERIOD_CHOICES[analysis.interval]):
	    
	    if analysis.last_report != None and analysis.interval == 'n':
		continue
	      
	    results = []
	    for report in analysis.queries.filter(activated=True):
		
		if analysis.date_from != None and analysis.date_to != None:
		    report_results = ReportResult.objects.filter(report=report, run_date__lte=analysis.date_to, run_date__gte=analyses.date_from).order_by('-run_date')  
		elif analysis.date_from == None and analysis.date_to != None:
		    report_results = ReportResult.objects.filter(report=report, run_date__lte=analysis.date_to).order_by('-run_date')
		elif analysis.date_from != None and analysis.date_to == None:
		    report_results = ReportResult.objects.filter(report=report, run_date__gte=analyses.date_from).order_by('-run_date')
		else:
		    report_results = ReportResult.objects.filter(report=report).order_by('-run_date')
		
		# create output from mongo output
		output_result = OutputResult(report=report.title)
		output_result.date_array = []
		output_result.output_array = []
		print "\n KOLIK: "+ str(output_result.output_array)
		for result in report_results:
		    output_result.date_array.append(result.run_date)
		    #print result.output
		    #print "\nouttest: "+str(output_result.output_array)
		    mongo_output = OutputMongo(result.output)
		    output_result.output_array.append(mongo_output.getoutput())

		print "out: ",output_result.output_array
		results.append(output_result)    


	    #print results[0].output_array
	    #print "\n\n"
	    #print results[1].output_array
	    # process outputs
	    if not process_output_reports(results, analysis, date_now):
		print "Error in execute analysis: %s" % (analysis.title)
		continue
	    
	    if analysis.interval != 'n':
		if analysis.date_to != None:
		    analysis.date_to = analysis.date_to + timedelta( seconds=PERIOD_CHOICES[analysis.interval])
		if analysis.date_from != None:
		    analysis.date_from = analysis.date_from + timedelta( seconds=PERIOD_CHOICES[analysis.interval])
		    
    return True

def create_reports():
    """
    create results of reports by reports properties  
    """
    
    date_now = datetime.now()
    for report in Report.objects.filter(activated=True):
	
	if report.last_report == None or report.last_report <= date_now - timedelta( seconds=PERIOD_CHOICES[report.interval]):
	    #if report is now so do not execute it times 
	    if report.last_report != None and report.interval == 'n':
		continue
	    if report.date_to != None and report.date_to < date_now:
		continue
	    
	    # check if query is good
	    check_ok, db_query = check_query(report)
	    if not check_ok:
		continue
	    
	    # check if date patterns are in query
	    date_pattern_from = string.find(db_query, "${{d1}}")
	    date_pattern_to = string.find(db_query, "${{d2}}")
	    if date_pattern_from != -1:
		date_from = date_now - timedelta( seconds=PERIOD_CHOICES[report.interval])
	    else:
		date_from = None
	    if date_pattern_to != -1:
		date_to = date_now
	    else:
		date_to = None

	    # excute reports for past periods
	    if not execute_past_reports(report, db_query, date_from, date_to, date_now):
		continue

	    # execute query for this time
	    if date_from != None:
		db_query = string.replace(db_query, "${{d1}}", "new Date(%s,%s,%s)" % (date_from.year, date_from.month - 1, date_from.day))
	    if date_to != None:
		db_query = string.replace(db_query, "${{d2}}", "new Date(%s,%s,%s)" % (date_to.year, date_to.month - 1, date_to.day))

	    if not execute_query(db_query, report, date_now):
		print "error - unsupported query: report title: %s, id: " % (report.title, report.id)
		continue

    return True


if __name__ == "__main__":
    create_reports()
    create_analysis()