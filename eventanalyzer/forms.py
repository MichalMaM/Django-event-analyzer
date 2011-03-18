"""
This file contains forms for customization Admin forms  
"""
import string
from django import forms
from django.forms import ModelForm, ValidationError
from django.forms.util import ErrorList
from django.utils.translation import ugettext_lazy as _
from eventanalyzer.models import Report


class SpanErrorList(ErrorList):
    def __unicode__(self):
	return self.as_span()
    def as_span(self):
	if not self: return u''
	return u'<span class="errorlist">%s</span>' % ''.join([u'%s' % e for e in self])

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



class QueryForm(forms.Form):
    
    db_query = forms.CharField(label=_( 'Database query' ), widget=forms.Textarea(attrs={'cols':'80', 'rows':'20'}))
    
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

