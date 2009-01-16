from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import HttpResponseNotFound
from django.http import Http404
from django.template import loader, Context
from django.template import RequestContext 
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from tdsurface.shortcuts import get_object_or_None
#from datetime import date
import time
import datetime

from tdsurface.depth.models import *
from tdsurface.depth.forms import *

from tdsurface.toolcom import ToolCom
from tdsurface.toolapi import ToolAPI
from django.conf import settings


def mainmenu(request) :
    d = {}
    return render_to_response('mainmenu.html', d)
    
def pull_calibration(request, object_id) :    
    d = {}
    
    tool = Tool.objects.get(pk=object_id)
    d['object'] = tool
    
    tc = ToolCom(port = settings.COMPORT, baudrate=settings.BAUDRATE, bytesize=settings.DATABITS, parity=settings.PARITY, stopbits=settings.STOPBITS, timeout=settings.COMPORT_TIMEOUT)
    tapi = ToolAPI(tc)
    
    comcheck = tapi.echo('ABC123')
    if comcheck != 'ABC123' :
        return HttpResponse("Communications check of the tool failed: '%s'" % comcheck)
    
    cal_vals = tapi.get_calibration_contants()
    d['calibration'] = cal_vals
    
    ival = [int(x, 16) for x in cal_vals]
    
    d['time_stamp'] = datetime.datetime.utcnow()
    tc = ToolConfig(time_stamp = d['time_stamp'], tool=tool, calco0=ival[0], calco1=ival[1], calco2=ival[2], calco3=ival[3], calco4=ival[4], calco5=ival[5]
                    , calco6=ival[6], calco7=ival[7], calco8=ival[8], calco9=ival[9], calco10=ival[10], calco11=ival[11], calco12=ival[12], calco13=ival[13], calco14=ival[14]
                    , calco15=ival[15])
    tc.save()
    
    return render_to_response('calibration_results.html', d, context_instance = RequestContext(request))
    
def set_time(request, object_id) :
    if request.method == 'POST': # If the form has been submitted...
        form = SetTimeForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
                                
            tool = Tool.objects.get(pk=object_id)
    
            tc = ToolCom(port = settings.COMPORT, baudrate=settings.BAUDRATE, bytesize=settings.DATABITS, parity=settings.PARITY, stopbits=settings.STOPBITS, timeout=settings.COMPORT_TIMEOUT)
            tapi = ToolAPI(tc)
            
            comcheck = tapi.echo('ABC123')
            if comcheck != 'ABC123' :
                return HttpResponse("Communications check of the tool failed: '%s'" % comcheck)
                
            tapi.set_time(form.cleaned_data['set_time_to']) # Set the time
            tool_time = tapi.get_time() # Read the time back
            tc.close()
            
            return render_to_response('timeset_results.html', {'tool_time': tool_time,'object': tool,}, context_instance = RequestContext(request))
    else:
        form = SetTimeForm(initial = {'set_time_to': datetime.datetime.utcnow(),}) # An unbound form

    return render_to_response('generic_form.html', {'form': form,}, context_instance = RequestContext(request))
    
def tool_status(request, object_id) :
    
    tool = Tool.objects.get(pk=object_id)
    
    tc = ToolCom(port = settings.COMPORT, baudrate=settings.BAUDRATE, bytesize=settings.DATABITS, parity=settings.PARITY, stopbits=settings.STOPBITS, timeout=settings.COMPORT_TIMEOUT)
    tapi = ToolAPI(tc)
    
    time.sleep(1)
    
    comcheck = tapi.echo('ABC123')
    if comcheck != 'ABC123' :
        tc.close()
        return HttpResponse("Communications check of the tool failed. Expected 'ABC123' got '%s'" % comcheck)
        
    tool_time = tapi.get_time()
    calibration = tapi.get_calibration_contants()
    log_address = tapi.get_current_log_address()
    tc.close()
    
    return render_to_response('tool_status.html', {'tool_time': tool_time,'object': tool, 'calibration': calibration, 'log_address': log_address}, context_instance = RequestContext(request))
    
    
def run_activate(request, object_id) :    
    d = {}
    
    run = Run.objects.get(pk=object_id)
   
    active_run, created = Settings.objects.get_or_create(name='ACTIVE_RUN')
    
    active_run.value=run.pk
    active_run.save()
        
    return HttpResponseRedirect(reverse('run_list'))

def run_download_status(request) :
    if request.session['log_download_in_progress'] :    
        return HttpResponse("Downloading Log: %s" % (str(request.session['log_download_cnt'])))
    else :
        return HttpResponse("Download Complete")

    
def run_download_log(request, object_id) :
    run = Run.objects.get(pk=object_id)
    
    tc = ToolCom(port = settings.COMPORT, baudrate=settings.BAUDRATE, bytesize=settings.DATABITS, parity=settings.PARITY, stopbits=settings.STOPBITS, timeout=settings.COMPORT_TIMEOUT)
    tapi = ToolAPI(tc)

    comcheck = tapi.echo('ABC123')
    if comcheck != 'ABC123' :
        return HttpResponse("Communications check of the tool failed: '%s'" % comcheck)

    request.session['log_download_in_progress'] = False
    request.session['log_download_data'] = []
    request.session['log_download_cnt'] = 0
    request.session.save()
    
    def call_back(l) :
        request.session['log_download_data'].append(l)
        request.session['log_download_cnt'] += 1
        request.session.save() 

    request.session['log_download_in_progress'] = True
    request.session.save() 
    log = tapi.get_log(call_back)
    #for x in range(10) :
    #    call_back(x)
    #    time.sleep(1)
    request.session['log_download_in_progress'] = False
    request.session.save() 
    
    return HttpResponse("Log Download Complete!")
    
def run_wits0_latest(request, run_id, num_latest=100, num_skip=0, extra_context={}) :
    run = Run.objects.get(pk=run_id)

    num_latest=int(num_latest)
    neg_num_latest = -num_latest
    num_skip = int(num_skip)

    wits = WITS0.objects.filter(run=run).order_by('-time_stamp','recid','itemid')[num_skip: num_skip+num_latest]
    
    data = {'wits':wits, 'num_latest':num_latest, 'neg_num_latest':neg_num_latest, 'num_skip':num_skip, 'run':run, }
    
    for key, value in extra_context.items():
        if callable(value):
            data[key] = value()
        else:
            data[key] = value    
    
    return render_to_response('wits0_detail.html', data , context_instance = RequestContext(request)) 
    
