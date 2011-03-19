import os
from time import time
from datetime import datetime, timedelta
from mock import patch, Mock, sentinel
from nose import tools
from eventanalyzer.jobs import check_query, create_analysis
from eventanalyzer.models import Report, ReportResult, Analysis, AnalysisResult
from settings import STATISTICS_REPORT_PATH


def test_getting_correct_query():
    query = "db.events.count()"
    report = Report(title="report1", description="test", db_query=query, interval='m')
    tools.assert_equals((True, query), check_query(report))
    query = "db.events.group()"
    report.db_query=query
    tools.assert_equals((True, 'db.events.group().forEach(printjson)'), check_query(report))
    query = "db.events.group().forEach(printjson)"
    report.db_query=query
    tools.assert_equals((True, query), check_query(report))
    query = "db.events.group"
    report.db_query=query
    tools.assert_equals((False, ''), check_query(report))
    query = "db.events.find()"
    report = Report(title="report2", description="test2", db_query=query, interval='w')
    tools.assert_equals((False, ''), check_query(report))


def test_create_periodic_csv_analysis_for_count():
    report = Report(title="report1", description="test", db_query="db.events.count()", interval='m')
    report.save()
    report_result1 = ReportResult(report=report, output ='{"count" : 5}', run_date = datetime(2010, 5, 6))
    report_result1.save()
    report_result2 = ReportResult(report=report, output ='{"count" : 7}', run_date = datetime(2010, 4, 6))
    report_result2.save()
    analysis = Analysis(id=1, title="analysis1", description="test analysis", plug_in='output_csv_file', interval='m')
    analysis.queries.add(report)
    analysis.save()
    tools.assert_equals(True, create_analysis())
    tools.assert_equals(AnalysisResult.objects.all().count(), 1)
    tools.assert_not_equals(Analysis.objects.all()[0].last_report, None)
    analysis_result1 = AnalysisResult.objects.all()[0]
    os.remove('%s/%s' % (STATISTICS_REPORT_PATH, analysis_result1.output))


def test_create_aperiodic_graph_analysis_for_count():
    report = Report(title="report2", description="test", db_query='db.events.find({event: "statistc"}).count()', interval='w')
    report.save()
    report_result1 = ReportResult(report=report, output ='{"count" : 15}', run_date = datetime(2010, 5, 13))
    report_result1.save()
    report_result2 = ReportResult(report=report, output ='{"count" : 97}', run_date = datetime(2010, 5, 6))
    report_result2.save()
    analysis = Analysis(id=2, title="analysis2", description="test analysis", plug_in='output_bar_graph_file', interval='n')
    analysis.queries.add(report)
    analysis.save()
    tools.assert_equals(True, create_analysis())
    tools.assert_equals(AnalysisResult.objects.all().count(), 1)
    tools.assert_not_equals(Analysis.objects.all()[0].last_report, None)


def test_create_periodic_graph_analysis_for_group():
    report = Report(title="report3", description="test", db_query='db.events.group({ key : { event : true }, condition : { timestamp : {$gt : ${{d1}}, $lt: ${{d2}}} }, reduce : function( obj, prev ) { prev.total++; }, initial : { total : 0 } })', interval='y')
    report.save()
    report_result1 = ReportResult(report=report, output ='{ "event" : "main_event7_1", "total" : 4 }\n{ "event" : "main_event6_1", "total" : 4 }\n', run_date = datetime(2011, 5, 13))
    report_result1.save()
    report_result2 = ReportResult(report=report, output ='{ "event" : "main_event7_1", "total" : 6 }\n{ "event" : "main_event5_1", "total" : 12 }\n', run_date = datetime(2010, 5, 13))
    report_result2.save()
    analysis = Analysis(id=3, title="analysis3", description="test analysis", plug_in='output_bar_graph_file', interval='y')
    analysis.queries.add(report)
    analysis.save()
    tools.assert_equals(True, create_analysis())
    tools.assert_equals(AnalysisResult.objects.all().count(), 1)
    tools.assert_not_equals(Analysis.objects.all()[0].last_report, None)


def test_create_periodic_csv_analysis_for_group():
    report = Report(title="report4", description="test", db_query='db.events.group({ key : { event : true }, condition : { timestamp : {$gt : ${{d1}}, $lt: ${{d2}}} }, reduce : function( obj, prev ) { prev.total++; }, initial : { total : 0 } })', interval='m')
    report.save()
    report_result1 = ReportResult(report=report, output ='{ "event" : "services_list", "total" : 13 }\n{ "event" : "main_event6_1", "total" : 4 }\n', run_date = datetime(2011, 6, 13))
    report_result1.save()
    report_result2 = ReportResult(report=report, output ='{ "event" : "main_event7_1", "total" : 60 }\n{ "event" : "content_link", "total" : 20 }\n', run_date = datetime(2010, 5, 13))
    report_result2.save()
    analysis = Analysis(id=4, title="analysis4", description="test analysis", plug_in='output_csv_file', interval='y')
    analysis.queries.add(report)
    analysis.save()
    tools.assert_equals(True, create_analysis())
    tools.assert_equals(AnalysisResult.objects.all().count(), 1)
    tools.assert_not_equals(Analysis.objects.all()[0].last_report, None)




