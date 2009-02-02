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

from django.core import serializers
from django.utils import simplejson

import time
import datetime

from tdsurface.depth.models import *
from tdsurface.depth.forms import *

from tdsurface.toolcom import ToolCom
from tdsurface.toolapi import ToolAPI
from django.conf import settings

import threading
import logging


def test(request) :
    data = simplejson.dumps({'test': 'foo', 'test2':'bar', })   
    
    return HttpResponse(data, mimetype="application/javascript")

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

def reset_timer(request, object_id) :
    
    tool = Tool.objects.get(pk=object_id)
    
    tc = ToolCom(port = settings.COMPORT, baudrate=settings.BAUDRATE, bytesize=settings.DATABITS, parity=settings.PARITY, stopbits=settings.STOPBITS, timeout=settings.COMPORT_TIMEOUT)
    tapi = ToolAPI(tc)    
    
    comcheck = tapi.echo('ABC123')
    if comcheck != 'ABC123' :
        tc.close()
        return HttpResponse("Communications check of the tool failed. Expected 'ABC123' got '%s'" % comcheck)
        
    tapi.set_time(datetime.datetime(2001,1,1,0,0,0)) # Set the timer to 0 using tool base time (2001-01-01 00:00:00) (year & month are ignored on the timer)
    
    tc.close()
    
    return render_to_response('message.html', {'message': 'Tool timer reset to 0', 'navigation_template': 'tool_menu.html' , 'object':tool }, context_instance = RequestContext(request))
        
def tool_status(request, object_id) :
    
    tool = Tool.objects.get(pk=object_id)
    
    tc = ToolCom(port = settings.COMPORT, baudrate=settings.BAUDRATE, bytesize=settings.DATABITS, parity=settings.PARITY, stopbits=settings.STOPBITS, timeout=settings.COMPORT_TIMEOUT)
    tapi = ToolAPI(tc)
    
    comcheck = tapi.echo('ABC123')
    if comcheck != 'ABC123' :
        tc.close()
        return HttpResponse("Communications check of the tool failed. Expected 'ABC123' got '%s'" % comcheck)
            
    calibration = tapi.get_calibration_contants()
    sensor = tapi.get_sensor_readings()
    log_address = tapi.get_current_log_address()
    bytes_in_log = int(log_address, 16) - int('D600', 16)
    scp = tapi.get_status_constant_profile()
    tool_timer = tapi.get_timer()    
    tc.close()
    
    return render_to_response('tool_status.html', {'scp': scp, 'sensor': sensor, 'tool_timer': tool_timer, 'object': tool, 'calibration': calibration, 'log_address': log_address, 'bytes_in_log': bytes_in_log}, context_instance = RequestContext(request))


def tool_pulse_pattern_profile(request, object_id) :
    
    tool = Tool.objects.get(pk=object_id)

    tc = ToolCom(port = settings.COMPORT, baudrate=settings.BAUDRATE, bytesize=settings.DATABITS, parity=settings.PARITY, stopbits=settings.STOPBITS, timeout=settings.COMPORT_TIMEOUT)
    tapi = ToolAPI(tc)

    comcheck = tapi.echo('ABC123')
    if comcheck != 'ABC123' :
        tc.close()
        return HttpResponse("Communications check of the tool failed. Expected 'ABC123' got '%s'" % comcheck)

    if request.method == 'POST':
        for seq in range(3) :
            for num in range(20) :
                pat_val = int(request.POST['ppp_seq'+str(seq)+'_pat'+str(num)])
                pat_val_cur = int(request.POST['ppp_seq'+str(seq)+'_pat'+str(num)+'_cur'])
                cnt_val = int(request.POST['ppp_seq'+str(seq)+'_cnt'+str(num)])
                cnt_val_cur = int(request.POST['ppp_seq'+str(seq)+'_cnt'+str(num)+'_cur'])
                if (pat_val != pat_val_cur) or (cnt_val != cnt_val_cur):
                    tapi.set_pulse_pattern_profile(seq, num, pat_val, cnt_val)                    

        for cnt in range(10) :
            seq = int(request.POST['ppsp_seq'+str(cnt)])
            seq_cur = int(request.POST['ppsp_seq'+str(cnt)+'_cur'])
            time_min = int(request.POST['ppsp_min'+str(cnt)])
            time_sec = int(request.POST['ppsp_sec'+str(cnt)])
            time = ((time_min * 60) + time_sec) * 1000
            time_cur = int(request.POST['ppsp_time'+str(cnt)+'_cur'])
            if (seq != seq_cur) or (time != time_cur) :
                print 'ppsp',cnt,seq,time,time_min,time_sec
                tapi.set_pulse_pattern_sequence_profile(cnt, seq, time)                
        
        adv_seq = 0
        adv_seq_cur = int(request.POST['scp_adv_seq_cur'])
        if request.POST.has_key('scp_adv_seq') :
            adv_seq=1
        if adv_seq != adv_seq_cur :
            tapi.toggle_advanced_sequence_pattern_mode()
                
    ppp = tapi.get_pulse_pattern_profile()
    ppsp = tapi.get_pulse_pattern_sequence_profile()
    scp = tapi.get_status_constant_profile()
    tc.close()
    
    #ppp = [[(1, 1), (14, 1), (2, 1), (14, 1), (1, 1), (14, 1), (2, 1), (14, 1), (14, 3), (65535, 1), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)], [(33, 1), (65535, 1), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)], [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)]]
    #ppsp = [(0, 240000), (1, 256608), (65535, 196609), (0, 196608), (0, 196608), (0, 196608), (0, 196608), (0, 196608), (0, 196608), (0, 196608)]
    ##ppsp = [(0, 4), (1, 4), (65535, 3), (0, 3), (0, 3), (0, 3), (0, 3), (0, 3), (0, 3), (0, 3)]
    #scp = [42330, 33, 0, 0, 1, 1, 0, 6, 300, 300, 7, 500, 1000, 0, 0, 0, 8528, 14, 576, 25, 4, 0, 30, 30, 10, 20, 20, 20, 20, 20]
    
    return render_to_response('tool_pulse_pattern_profile.html', {'ppp': ppp, 'ppsp': ppsp, 'scp': scp, 'object': tool, }, context_instance = RequestContext(request))


def tool_purge_log(request, object_id) :
    
    tool = Tool.objects.get(pk=object_id)
    
    tc = ToolCom(port = settings.COMPORT, baudrate=settings.BAUDRATE, bytesize=settings.DATABITS, parity=settings.PARITY, stopbits=settings.STOPBITS, timeout=settings.COMPORT_TIMEOUT)
    tapi = ToolAPI(tc)
    
    comcheck = tapi.echo('ABC123')
    if comcheck != 'ABC123' :
        tc.close()
        return HttpResponse("Communications check of the tool failed. Expected 'ABC123' got '%s'" % comcheck)
        
    tapi.purge_log()
    
    tc.close()
    
    return render_to_response('message.html', {'message': 'Tool MWD Log Purged', 'navigation_template': 'tool_menu.html', 'object':tool }, context_instance = RequestContext(request))

def tool_update(request, object_id, extra_context=None,) :
    
    tool = Tool.objects.get(pk=object_id)
    
    if request.method == 'POST': # If the form has been submitted...
        if request.POST['form_id'] == 'tool_update_form' :
            tool_form = ToolForm(request.POST, instance=tool) # A form bound to the POST data
            tool_notes_form = ToolNotesForm(initial = {'tool': object_id,})
            if tool_form.is_valid(): # All validation rules pass
                tool_form.save()            
                return HttpResponseRedirect(reverse('tool_update', args=[object_id]))
        else :
            tool_notes_form = ToolNotesForm(request.POST) # A form bound to the POST data
            tool_form = ToolForm(instance = tool)
            if tool_notes_form.is_valid() :
                tool_notes = ToolNotes(tool=tool, notes = tool_notes_form.cleaned_data['notes'])
                tool_notes.save()
                return HttpResponseRedirect(reverse('tool_update', args=[object_id]))
    else:
        tool_form = ToolForm(instance = tool)
        tool_notes_form = ToolNotesForm(initial = {'tool': object_id,})

    tool_notes = ToolNotes.objects.filter(tool=tool).order_by('time_stamp')
    
    data = {'tool_form':tool_form, 'object': tool, 'tool_notes_form': tool_notes_form, 'tool_notes': tool_notes }
    
    for key, value in extra_context.items():
        if callable(value):
            data[key] = value()
        else:
            data[key] = value    

    return render_to_response('tool_update_form.html', data, context_instance = RequestContext(request))


def tool_calibration_update(request, object_id, template_name, extra_context=None,) :
    
    tool = Tool.objects.get(pk=object_id)
    tc = ToolCom(port = settings.COMPORT, baudrate=settings.BAUDRATE, bytesize=settings.DATABITS, parity=settings.PARITY, stopbits=settings.STOPBITS, timeout=settings.COMPORT_TIMEOUT)
    tapi = ToolAPI(tc)
    
    comcheck = tapi.echo('ABC123')
    if comcheck != 'ABC123' :
        return HttpResponse("Communications check of the tool failed: '%s'" % comcheck)
    
    if request.method == 'POST': # If the form has been submitted...
        if request.POST['form_id'] == 'tool_update_form' :
            form = ToolCalibrationForm(request.POST) # A form bound to the POST data
            if form.is_valid(): # All validation rules pass
                #Save Calibration constants here
                pass
    else:
        c = tapi.get_calibration_contants()
        initial = {
            'accelerometer_x_offset': c[2],
            'accelerometer_x_gain': c[3],
            'accelerometer_y_offset': c[4],
            'accelerometer_y_gain': c[5],
            'accelerometer_z_offset': c[6],
            'accelerometer_z_gain': c[7],
            'magnetometer_x_offset': c[8],
            'magnetometer_x_gain': c[9],
            'magnetometer_y_offset': c[10],
            'magnetometer_y_gain': c[11],
            'magnetometer_z_offset': c[12],
            'magnetometer_z_gain': c[13],
            'temperatrue_offset':c[14],
            'temperature_gain': c[15],
        }
        form = ToolCalibrationForm(initial = initial)            
    
    data = {'form':form, 'object': tool, }
    
    for key, value in extra_context.items():
        if callable(value):
            data[key] = value()
        else:
            data[key] = value    

    return render_to_response(template_name, data, context_instance = RequestContext(request))
 
        
    
def run_activate(request, object_id) :    
    d = {}
    
    run = Run.objects.get(pk=object_id)
   
    active_run, created = Settings.objects.get_or_create(name='ACTIVE_RUN')
    
    active_run.value=run.pk
    active_run.save()
        
    return HttpResponseRedirect(reverse('run_list'))


def run_update(request, run_id, extra_context=None,) :
    
    run = Run.objects.get(pk=run_id)
    
    if request.method == 'POST': # If the form has been submitted...
        if request.POST['form_id'] == 'run_update_form' :
            run_form = RunForm(request.POST, instance=run) # A form bound to the POST data
            run_notes_form = RunNotesForm(initial = {'run': run_id,})
            if run_form.is_valid(): # All validation rules pass
                run_form.save()            
                return HttpResponseRedirect(reverse('run_update', args=[run.pk]))
        else :
            run_notes_form = RunNotesForm(request.POST) # A form bound to the POST data
            run_form = RunForm(instance = run)
            if run_notes_form.is_valid() :
                run_notes = RunNotes(run=run, notes = run_notes_form.cleaned_data['notes'])
                run_notes.save()
                return HttpResponseRedirect(reverse('run_update', args=[run.pk]))
    else:
        run_form = RunForm(instance = run)
        run_notes_form = RunNotesForm(initial = {'run': run_id,})

    run_notes = RunNotes.objects.filter(run=run).order_by('time_stamp')
    
    data = {'run_form':run_form, 'run':run, 'run_notes_form': run_notes_form, 'run_notes': run_notes }
    
    for key, value in extra_context.items():
        if callable(value):
            data[key] = value()
        else:
            data[key] = value    

    return render_to_response('run_update_form.html', data, context_instance = RequestContext(request))


def run_download_status(request) :
    
    p = bool(Settings.objects.get(name='LOG_DOWNLOAD_IN_PROGRESS').value)
    c = int(Settings.objects.get(name='LOG_DOWNLOAD_CNT').value)
        
    if p :
        if c > 0 :
            return HttpResponse("Downloading Log: %d" % c )
        elif c < 0 :
            return HttpResponse("Error while downloading: %d" % c)
        else :
            return HttpResponse("Starting Download...")
    elif  c == 0 :
        return HttpResponse("Not Downloading")  # No download in process or completed
    elif c < 0 :
        return HttpResponse("Error: %d" % c)
    else :
        return HttpResponse("Download Complete")


def run_download_status_json(request) :
    
    p = int(bool(Settings.objects.get(name='LOG_DOWNLOAD_IN_PROGRESS').value))
    c = int(Settings.objects.get(name='LOG_DOWNLOAD_CNT').value)
    s = Settings.objects.get(name='LOG_DOWNLOAD_STATUS').value
        
    data = simplejson.dumps({'downloading': p, 'cnt': c, 'status':s})   
    
    return HttpResponse(data, mimetype="application/javascript")    


# Canceling does not work reliablly because the download process does not get
# an updated copy of the session varibles
def run_download_cancel(request) :
    
    p = Settings.objects.get(name='LOG_DOWNLOAD_IN_PROGRESS')
    p.value=''
    p.save()
    
    s = Settings.objects.get(name='LOG_DOWNLOAD_STATUS')
    s.value='Download Canceled'
    s.save()
    
    return HttpResponse("Canceling")


def _download_log(run_id) :
    
    p = Settings.objects.get(name='LOG_DOWNLOAD_IN_PROGRESS')
    p.value='True'
    p.save()
           
    c = Settings.objects.get(name='LOG_DOWNLOAD_CNT')
    c.value='0'
    c.save()       
               
    run = Run.objects.get(pk=run_id)
    
    s = Settings.objects.get(name='LOG_DOWNLOAD_STATUS')
    s.value='Opening COM Port %s' % settings.COMPORT
    s.save()
    
    try :    
        tc = ToolCom(port = settings.COMPORT, baudrate=settings.BAUDRATE, bytesize=settings.DATABITS, parity=settings.PARITY, stopbits=settings.STOPBITS, timeout=settings.COMPORT_TIMEOUT)
    except :
        s.value='Error opening port %s' % settings.COMPORT
        s.save()
        p.value=''
        p.save()
        return
        
    tapi = ToolAPI(tc)
    
    s.value='Checking Tool'
    s.save()
    comcheck = tapi.echo('ABC123')
    if comcheck != 'ABC123' :
        p.value=''
        p.save()
        c.value = str(-1)
        c.save()
        s.value="Communications check of the tool failed. Expected 'ABC123' got '%s'" % comcheck
        s.save()
        tc.close()
        return

    def call_back(log_data) :
        
        c.value = str(int(c.value) + 1)
        c.save()            
        
        d = ToolMWDLog()        
        d.run_id = run_id
        d.raw_data = log_data.raw_data
        d.seconds = log_data.seconds
        d.status = log_data.status
        d.gravity_x = log_data.gravity_x
        d.gravity_y = log_data.gravity_y
        d.gravity_z = log_data.gravity_z
        d.magnetic_x = log_data.magnetic_x
        d.magnetic_y = log_data.magnetic_y
        d.magnetic_z = log_data.magnetic_z
        d.temperature = log_data.temperature
        d.gamma0 = log_data.gamma0
        d.gamma1 = log_data.gamma1
        d.gamma2 = log_data.gamma2
        d.gamma3 = log_data.gamma3
        d.save()
                
        p = Settings.objects.get(name='LOG_DOWNLOAD_IN_PROGRESS')        
        return bool(p.value)

    s.value='Downloading'
    s.save()
    rc = tapi.get_log(call_back)
    if rc == None :
        s.value='Download Error'
    elif rc == False :
        s.value='Download Canceled'
    else :
        s.value = 'Download Complete'
    s.save()
    
    p.value=''
    p.save()
            
    tc.close()
    
def run_start_download_log(request, object_id) :
    run = Run.objects.get(pk=object_id)
        
    p, created = Settings.objects.get_or_create(name='LOG_DOWNLOAD_IN_PROGRESS')
    p.value='True'
    p.save()
           
    c, created = Settings.objects.get_or_create(name='LOG_DOWNLOAD_CNT')
    c.value=str('0')
    c.save()
    
    s, created = Settings.objects.get_or_create(name='LOG_DOWNLOAD_STATUS')
    s.value=str('Starting Download')
    s.save()
    
    t = threading.Thread(target = _download_log, args=[object_id])
    t.setDaemon(True)
    t.start()
    return HttpResponse("Download Started")
        
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
    
