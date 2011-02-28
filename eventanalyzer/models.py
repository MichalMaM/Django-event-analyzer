import pkg_resources
import string

from pymongo.connection import Connection
from eventanalyzer.conf import settings
from datetime import datetime
from django.db import models
from django.utils.translation import ugettext_lazy as _

PERIOD_CHOICES = (
    ('n', 'now'), 
    ('d', 'day'),
    ('m', 'month'),
    ('w', 'week'),
    ('y', 'year'),
)


PLUG_INS = []
for dist in pkg_resources.working_set.iter_entry_points("output.plugins.0.01"):
    try:
	PLUG_INS.append((dist.name, string.replace(dist.name, "_", " ")))
    except ImportError, err:
        print "Error while loading command %s: %s" % (dist.name, str(err))

#PLUG_INS = [
#    ('bar_graph', 'bar graph'), 
#    ('output_csv_file', 'output csv file'),
#]


def get_mongo_collection():
    "Open a connection to MongoDB and return the collection to use."
    if not getattr(settings, "MONGODB_HOSTS", []):
        hosts = [
            "%s:%s" % (getattr(settings, "MONGODB_HOST", "localhost"), getattr(settings, "MONGODB_PORT", 27017))
        ]

        if getattr(settings, "RIGHT_MONGODB_HOST", None):
            hosts.append("%s:%s" % (settings.RIGHT_MONGODB_HOST, getattr(settings, "RIGHT_MONGODB_PORT", 27017)))
    else:
        hosts = settings.MONGODB_HOSTS
    
    connection = Connection(hosts)
    return connection[settings.MONGODB_DB][settings.MONGODB_COLLECTION]

class Report(models.Model):
    """
    save report for execute individual query.
    """
    title = models.CharField( _( 'Title' ), max_length=100, unique=True)
    description = models.CharField(_( 'Description' ), max_length=200)
    db_query = models.TextField(_( 'Database query' ), help_text=_( 'If you want use date bounds for your query, so use pattern ${{d1}} for date from and ${{d2}} for date to' ))
    interval = models.CharField( _( 'Interval' ), max_length=1, choices=PERIOD_CHOICES )
    date_from = models.DateTimeField(_( 'Date from' ), blank=True, null=True)
    date_to = models.DateTimeField(_( 'Date to' ), blank=True, null=True)
    activated = models.BooleanField(_( 'Activated' ), default=True) 
    last_report = models.DateTimeField(_( 'Last report' ), blank=True, null=True)

    def __unicode__(self):
        return self.title

class ReportResult(models.Model):
    """
    save report result for individual query report.
    """
    report = models.ForeignKey(Report, verbose_name=_('Report'))
    output = models.TextField(_( 'Output in JSON' ))
    run_date = models.DateTimeField(_( 'Date of run' ))

class Analysis(models.Model):
    """
    save individual analysis.
    """
    title = models.CharField( _( 'Title' ), max_length=100, unique=True)
    description = models.CharField(_( 'Description' ), max_length=200)
    plug_in = models.CharField( _( 'Plug-in' ), max_length=30, choices=PLUG_INS )
    queries = models.ManyToManyField(Report, verbose_name=_('Queries'))
    date_from = models.DateTimeField(_( 'Date from' ), blank=True, null=True)
    date_to = models.DateTimeField(_( 'Date to' ), blank=True, null=True)
    interval = models.CharField( _( 'Interval' ), max_length=1, choices=PERIOD_CHOICES )
    activated = models.BooleanField(_( 'Activated' ), default=True)
    last_report = models.DateTimeField(_( 'Last analysis' ), blank=True, null=True)

    def __unicode__(self):
        return self.title


class AnalysisResult(models.Model):
    """
    save analysis result for individual analysis.
    """
    analysis = models.ForeignKey(Analysis, verbose_name=_('Analysis'))
    output = models.FilePathField(_( 'Output file' ), path=settings.REPORT_PATH)
    run_date = models.DateTimeField(_( 'Date of run' ))

    

    

    