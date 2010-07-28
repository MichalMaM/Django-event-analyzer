from pymongo.connection import Connection
from eventanalyzer.conf import settings
from datetime import datetime
from django.db import models
from django.utils.translation import ugettext_lazy as _

PERIOD_CHOICES = (
    ('d', 'day'),
    ('m', 'month'),
    ('w', 'week'),
    ('y', 'year'),
)

def get_mongo_collection():
    """
    Open a connection to MongoDB and return the collection to use.
    """
    if settings.RIGHT_MONGODB_HOST:
        connection = Connection.paired(
                left=(settings.MONGODB_HOST, settings.MONGODB_PORT),
                right=(settings.RIGHT_MONGODB_HOST, settings.RIGHT_MONGODB_PORT)
            )
    else:
        connection = Connection(host=settings.MONGODB_HOST, port=settings.MONGODB_PORT)
    return connection[settings.MONGODB_DB][settings.MONGODB_COLLECTION]

class Report(models.Model):
    """
    save individual analysis.
    """
    title = models.CharField( _( 'Title' ), max_length=100, unique=True)
    description = models.CharField(_( 'Description' ), max_length=200)
    db_query = models.TextField(_( 'Database query' ))
    interval = models.CharField( _( 'Interval' ), max_length=1, choices=PERIOD_CHOICES )
    last_report = models.DateTimeField(_( 'Last report' ), blank=True, null=True)

    def __unicode__(self):
        return self.title

class ReportResult(models.Model):
    """
    save report file for individual analysis.
    """
    report = models.ForeignKey(Report, verbose_name=_('Report'))
    output = models.TextField(_( 'Output in CSV' ))
    run_date = models.DateTimeField(_( 'Date of run' )) # , default=datetime.now, editable=False
    

    

    