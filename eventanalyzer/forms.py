"""
This file contains forms for customization Admin forms  
"""
import string
from django.forms import ModelForm, ValidationError
from eventanalyzer.models import Report

class ReportAdminForm(ModelForm):
    
    class Meta:
	model = Report
    
    def clean_db_query(self):
	db_query = self.cleaned_data['db_query']

	if string.find(db_query, "count(") != -1:
	    if db_query[len(db_query) - 1] != ")" and db_query[len(db_query) - 1] != ";":
		raise ValidationError("This query is not supported!")
	elif string.find(db_query, "group(") != -1 or string.find(db_query, "mapReduce(") != -1:
	     if db_query[len(db_query) - 1] != ")" and db_query[len(db_query) - 1] != ";":
		raise ValidationError("This query is not supported!")
	else:
	    raise ValidationError("This query is not supported!")
	
	return self.cleaned_data['db_query']

