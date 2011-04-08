import os
from time import time
from datetime import datetime, timedelta
from mock import patch, Mock, sentinel
from nose import tools
from eventanalyzer.jobs import check_query, create_reports
from eventanalyzer.models import Report, ReportResult, get_mongo_collection
from settings import STATISTICS_MONGODB_COLLECTION, STATISTICS_MONGODB_DB 

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

def test_create_periodic_report_with_count():
    collection = get_mongo_collection()
    collection.remove()
    collection.insert({
        'event': "statistc",
        'timestamp': datetime(2011, 4, 7),
        'params': {"url": "www.centrum.cz"}
    })
    collection.insert({
        'event': "statistc",
        'timestamp': datetime(2011, 4, 5),
        'params': {"url": "www.centrum.cz"}
    })
    collection.insert({
        'event': "statistc",
        'timestamp': datetime(2011, 3, 7),
        'params': {"url": "www.centrum.cz"}
    })
    report = Report(title="report count", description="test", db_query='db.%s.find({event: "statistc", timestamp: {$gte: ${{d1}}, $lte: ${{d2}}}}).count()' % (STATISTICS_MONGODB_COLLECTION,), interval='w')
    report.save()
    tools.assert_equals(True, create_reports())
    tools.assert_not_equals(ReportResult.objects.all().count(), 0)
    tools.assert_not_equals(Report.objects.all()[0].last_report, None)
    collection.remove()
    
def test_create_aperiodic_report_with_count():
    collection = get_mongo_collection()
    collection.remove()
    collection.insert({
        'event': "statistc",
        'timestamp': datetime(2010, 3, 1),
        'params': {"url": "www.centrum.cz"}
    })
    collection.insert({
        'event': "statistc",
        'timestamp': datetime(2011, 2, 12),
        'params': {"url": "www.centrum.cz"}
    })
    collection.insert({
        'event': "content_link",
        'timestamp': datetime(2011, 2, 12),
        'params': {"url": "www.atlas.cz"}
    })
    report = Report(title="report count", description="test", db_query='db.%s.find({event: "statistc"}).count()' % (STATISTICS_MONGODB_COLLECTION,), interval='n')
    report.save()
    report = Report(title="report now", description="test", db_query='db.%s.count()' % (STATISTICS_MONGODB_COLLECTION,), interval='n')
    report.save()
    tools.assert_equals(True, create_reports())
    tools.assert_equals(ReportResult.objects.all().count(), 2)
    tools.assert_not_equals(Report.objects.all()[0].last_report, None)
    tools.assert_equals(ReportResult.objects.all()[0].output, '{"count" : 2}')
    tools.assert_equals(ReportResult.objects.all()[1].output, '{"count" : 3}')
    collection.remove()
    
def test_create_periodic_report_with_group():
    collection = get_mongo_collection()
    collection.remove()
    collection.insert({
        'event': "statistc",
        'timestamp': datetime(2011, 4, 7),
        'params': {"url": "www.centrum.cz"}
    })
    collection.insert({
        'event': "statistc",
        'timestamp': datetime(2011, 4, 1),
        'params': {"url": "www.centrum.cz"}
    })
    collection.insert({
        'event': "statistc",
        'timestamp': datetime(2011, 3, 7),
        'params': {"url": "www.centrum.cz"}
    })
    collection.insert({
        'event': "statistc",
        'timestamp': datetime(2011, 3, 21),
        'params': {"url": "www.centrum.cz"}
    })
    report = Report(title="report group", description="test", db_query='db.%s.group({ key : { "params.url" : true }, condition : { event : "statistic", timestamp : {$gt : ${{d1}}, $lt: ${{d2}}} }, reduce : function( obj, prev ) { prev.total++; }, initial : { total : 0 } })' % (STATISTICS_MONGODB_COLLECTION,), interval='m')
    report.save()
    tools.assert_equals(True, create_reports())
    tools.assert_not_equals(ReportResult.objects.all().count(), 0)
    tools.assert_not_equals(Report.objects.all()[0].last_report, None)
    collection.remove()

def test_create_periodic_report_with_group():
    collection = get_mongo_collection()
    collection.remove()
    collection.insert({
        'event': "statistic",
        'timestamp': datetime(2011, 4, 1),
        'params': {"url": "www.atlas.cz"}
    })
    collection.insert({
        'event': "statistic",
        'timestamp': datetime(2011, 3, 7),
        'params': {"url": "www.centrum.cz"}
    })
    collection.insert({
        'event': "statistic",
        'timestamp': datetime(2011, 3, 21),
        'params': {"url": "www.centrum.cz"}
    })
    report = Report(title="report group", description="test", db_query='db.%s.group({ key : { "params.url" : true }, condition : { event : "statistic" }, reduce : function( obj, prev ) { prev.total++; }, initial : { total : 0 } })' % (STATISTICS_MONGODB_COLLECTION,), interval='n')
    report.save()
    tools.assert_equals(True, create_reports())
    tools.assert_equals(ReportResult.objects.all().count(), 1)
    tools.assert_not_equals(Report.objects.all()[0].last_report, None)
    tools.assert_equals(ReportResult.objects.all()[0].output, '{ "params.url" : "www.atlas.cz", "total" : 1 }\n{ "params.url" : "www.centrum.cz", "total" : 2 }\n')
    collection.remove()