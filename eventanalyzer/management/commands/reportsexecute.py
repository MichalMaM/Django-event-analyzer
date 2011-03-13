"""
This file execute reports that are saved in db 
"""

from django.core.management.base import BaseCommand, CommandError

from eventanalyzer.jobs import create_reports



class Command(BaseCommand):
    args = '<>'
    help = 'execute saved periodic reports'

    def handle(self, *args, **options):
	"""
	execute saved periodic reports   
	"""

	if not create_reports():
	    raise CommandError('error - in execute priodic reports')
	
	print'execute reports successfull'


