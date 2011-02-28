from time import time
from datetime import datetime, timedelta
from mock import patch, Mock, sentinel
from nose import tools
from eventanalyzer.jobs import check_query, create_analysis
from eventanalyzer.models import Report, ReportResult, Analysis, AnalysisResult


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


def test_create_analysis():
    report = Report(title="report1", description="test", db_query="db.events.count()", interval='m')
    report_result1 = ReportResult(report=report, output ='{"count" : 5}', run_date = datetime(2010, 5, 6))
    report_result2 = ReportResult(report=report, output ='{"count" : 7}', run_date = datetime(2010, 4, 6))
    #analysis = Analysis(title="analysis1", description="test analysis", plug_in='output_csv_file', interval='m')
    #tools.assert_equals(True, create_analysis())






