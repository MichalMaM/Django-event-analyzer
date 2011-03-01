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


def test_create_analysis():
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




