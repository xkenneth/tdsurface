from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import HttpResponseNotFound
from django.http import Http404
from django.template import loader, Context
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from tdsurface.shortcuts import get_object_or_None
from datetime import date
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
    
    return render_to_response('calibration_results.html', d)
    
def set_time(request, object_id) :
    if request.method == 'POST': # If the form has been submitted...
        form = SetTimeForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
                                
            tool = Tool.objects.get(pk=object_id)
    
            tc = ToolCom(port = '/dev/tty.BluePortXP-C6DC-SPP-1', baudrate=2400, bytesize=8, parity='N', stopbits=1, timeout=10)
            tapi = ToolAPI(tc)
            
            comcheck = tapi.echo('ABC123')
            if comcheck != 'ABC123' :
                return HttpResponse("Communications check of the tool failed: '%s'" % comcheck)
                
            tapi.set_time(form.cleaned_data['set_time_to']) # Set the time
            tool_time = tapi.get_time() # Read the time back
            tc.close()
            
            return render_to_response('timeset_results.html', {'tool_time': tool_time,'object': tool,})
    else:
        form = SetTimeForm(initial = {'set_time_to': datetime.datetime.utcnow(),}) # An unbound form

    return render_to_response('generic_form.html', {'form': form,})
    
def tool_status(request, object_id) :
    
    tool = Tool.objects.get(pk=object_id)
    
    tc = ToolCom(port = '/dev/tty.BluePortXP-C6DC-SPP-1', baudrate=2400, bytesize=8, parity='N', stopbits=1, timeout=10)
    tapi = ToolAPI(tc)
    
    comcheck = tapi.echo('ABC123')
    if comcheck != 'ABC123' :
        return HttpResponse("Communications check of the tool failed: '%s'" % comcheck)
        
    tool_time = tapi.get_time()
    calibration = tapi.get_calibration_contants()
    log_address = tapi.get_current_log_address()
    tc.close()
    
    return render_to_response('tool_status.html', {'tool_time': tool_time,'object': tool, 'calibration': calibration, 'log_address': log_address})
    
    
def run_activate(request, object_id) :    
    d = {}
    
    run = Run.objects.get(pk=object_id)
   
    active_run, created = Settings.objects.get_or_create(name='ACTIVE_RUN')
    
    active_run.value=run.pk
    active_run.save()
        
    return HttpResponseRedirect(reverse('run_list')) 
