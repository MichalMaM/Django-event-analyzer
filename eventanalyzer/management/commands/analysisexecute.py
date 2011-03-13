"""
This file execute analysis that are saved in db 
"""

from django.core.management.base import BaseCommand, CommandError

from eventanalyzer.jobs import create_analysis



class Command(BaseCommand):
    args = '<>'
    help = 'execute saved periodic analysis'

    def handle(self, *args, **options):
	"""
	execute saved periodic analysis   
	"""

	if not create_analysis():
	    raise CommandError('error - in execute priodic analysis')
	
	print'execute analysis successfull'



