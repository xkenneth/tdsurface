import pytz
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import HttpResponseNotFound
from django.http import Http404
from django.template import loader, Context
from django.template import RequestContext 
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required


from django.core import serializers
from django.utils import simplejson

from time import mktime
from datetime import datetime
from datetime import timedelta

from tdsurface.depth.models import *

def run_toollog_grid(request, object_id) :

    run = Run.objects.get(pk=object_id)    
    wltz = pytz.timezone(run.well_bore.well.timezone)
    
    page = int(request.GET['page'])
    rows = int(request.GET['rows'])
    
    sort_order= ''
    if request.GET['sord'] == 'desc' :
        sort_order= '-'
    
    logs = ToolMWDLog.objects.filter(run=run).order_by(sort_order+request.GET['sidx'])
    
    records = len(logs)
    total_pages = records/rows;
    if records % rows :
        total_pages += 1
        
    data={
        'total': total_pages,
        'page': page,
        'records': records,
        'rows' : [ ],
        }

    for log in logs[(page-1)*rows:page*rows] :        
        wlt = pytz.utc.localize(run.start_time + timedelta(seconds=log.seconds)).astimezone(wltz).replace(tzinfo=None)
        rd = {}
        rd['id'] = log.pk        
        rd['seconds'] = str(wlt)
        rd['azimuth'] = str(log.azimuth())
        rd['inclination'] = str(log.inclination())
        rd['toolface_magnetic'] = str(log.tool_face_magnetic())
        rd['toolface_gravity'] = str(log.tool_face_gravity())
        rd['depth'] = str(log.depth)
        rd['depth_units'] = log.depth_units

        gamma = ToolMWDLogGamma.objects.filter(run=run, seconds=log.seconds)[0]
        rd['gamma'] = str(gamma.gamma_cps())
        
        data['rows'].append(rd)

    data = simplejson.dumps(data)       
    return HttpResponse(data, mimetype="application/javascript")

        


