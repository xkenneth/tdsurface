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


def manual_depth_to_mwdlog(request, object_id) :
    run = Run.objects.get(pk=object_id)

    mwdlogs = ToolMWDLog.objects.filter(run=run)

    for l in mwdlogs :
        time_stamp = run.start_time + timedelta(seconds=l.seconds)
        #try :
            
        lower = ManualDepth.objects.filter(run=run, time_stamp__lte = time_stamp ).order_by('-time_stamp')[0]
        higher = ManualDepth.objects.filter(run=run, time_stamp__gt = time_stamp ).order_by('time_stamp')[0]
        #except:
        #    continue

        # Linear Interpolation where x = seconds and y = depth    
        x = mktime(time_stamp.timetuple())
        xa = mktime(lower.time_stamp.timetuple())
        xb = mktime(higher.time_stamp.timetuple())

        ya = float(lower.depth)
        yb = float(higher.depth)
        
        y = ya + ((x - xa) * (yb - ya))/(xb - xa)

        #print xa, x, xb
        #print ya, y, yb
        #print
        
        l.depth=str(y)
        l.depth_units='ft'
        l.save()

    return HttpResponseRedirect(reverse('las_from_mwdlog', args=[object_id]))  


def run_manual_depth_grid(request, object_id) :

    page = int(request.GET['page'])
    rows = int(request.GET['rows'])
    
    sort_order= ''
    if request.GET['sord'] == 'desc' :
        sort_order= '-'
    
    pt = ManualDepth.objects.filter(run=object_id).order_by(sort_order+request.GET['sidx'])
    records = len(pt)
    total_pages = records/rows;
    if records % rows :
        total_pages += 1
        
    data={
        'total': total_pages,
        'page': page,
        'records': records,
        'rows' : [ ],
        }

    for r in pt[(page-1)*rows:page*rows] :
        rd = {}
        rd['id'] = r.pk        
        rd['time_stamp'] = str(r.time_stamp)                
        rd['depth'] = str(r.depth)
        rd['depth_units'] = r.depth_units
        rd['notes'] = r.notes
        data['rows'].append(rd)

    data = simplejson.dumps(data)       
    return HttpResponse(data, mimetype="application/javascript")

        
def run_manual_depth_grid_edit(request, object_id) :    
    run = Run.objects.get(pk=object_id)
    
    if request.method=='POST' :
        if request.POST['id'] == 'new' :
                           
            md = ManualDepth(run = run,
                           time_stamp = request.POST['time_stamp'],                           
                           depth = request.POST['depth'],
                           depth_units = request.POST['depth_units'],
                           notes = request.POST['notes'])
            md.save()    
            
        else :            
            md = ManualDepth.objects.get(pk = request.POST['id'])
            md.time_stamp = request.POST['time_stamp']            
            md.depth = request.POST['depth']
            md.depth_units = request.POST['depth_units']            
            md.notes = request.POST['notes']
            md.save()                
        
            
    data = simplejson.dumps(md.pk)       
    return HttpResponse(data, mimetype="application/javascript")                
    

def run_manual_depth_grid_delete(request, object_id) :    
    run = Run.objects.get(pk=object_id)
    
    if request.method=='POST' :        
        md = ManualDepth.objects.get(pk = request.POST['id'])        
        md.delete()
            
    return HttpResponse('true', mimetype="application/javascript")            

