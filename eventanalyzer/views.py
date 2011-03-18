# Create your views here.
import string
from subprocess import Popen, PIPE

from django.shortcuts import render_to_response
from django.template import RequestContext
from django import http
from django.core.urlresolvers import reverse

from eventanalyzer.conf import settings
from eventanalyzer.forms import QueryForm, SpanErrorList

def try_query(request):
    if request.method == 'POST':
	form = QueryForm(request.POST, error_class=SpanErrorList)
	if form.is_valid():
	    db_query = form.cleaned_data['db_query']
	    print "do query"
	    if string.find(db_query, "group(") != -1 or string.find(db_query, "mapReduce(") != -1:
	        if db_query[-1] == ")":
		    if string.find(db_query, "forEach(printjson)") == -1:
			db_query = db_query+".forEach(printjson)"
		elif db_query[-1] == ";":
		    if string.find(db_query, "forEach(printjson)") == -1:
			db_query = db_query[0:-1]+".forEach(printjson)"

	    mongo_error = None
	    process = Popen(["mongo","--host", string.join(settings.MONGODB_HOSTS), "--eval", db_query, settings.MONGODB_DB], stdout=PIPE)
	    output_shell = process.communicate()[0]
	    if process.returncode != 0:
		mongo_error =  "error - can not execute mongo query "
	
	    #print output_shell
	    if mongo_error != None:
		output = mongo_error
	    else:
		index = string.find(output_shell, "{")
		if index == -1:
		    analyse_list = string.split(output_shell, "\n")
		    try:
			analyse_element = int(analyse_list[-2])
			output = '{"count" : %s}' % (analyse_element)
		    except ValueError:
			output = '{"data" : "no data"}'
		else:
		    output = output_shell[index:]
	    #f = open("/home/michal/diplo/session.txt", "w")
	    #f.write(output)
	    #f.close()
	    request.session.setdefault('db_query', {}).update({'query' : output})
	    request.session.modified = True
	    return http.HttpResponseRedirect(reverse('eventanalyzer_query_result', args=()))
    else:
	form = QueryForm(error_class=SpanErrorList)
    return render_to_response('query.html', {'form': form})

def query_result(request):
    result = request.session.get('db_query', {})
    try:
	query = result['query']
    except KeyError:
	query = "Query was not inserted"
    return render_to_response('result.html', {'query': query})