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

logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s', filename='/var/log/tdsurface/tdsurface.log',level=logging.DEBUG,)


import matplotlib
matplotlib.use("Agg") # do this before pylab so you don'tget the default back end.

import pylab
import matplotlib.numerix as N

def test_matplotlib(request) :
    # Generate and plot some simple data:
    x = N.arange(0, 2*N.pi, 0.1)
    y = N.sin(x)+1

    pylab.ylim(8,0)
    pylab.plot(y,x)
    F = pylab.gcf()

    # Now check everything with the defaults:
    DPI = F.get_dpi()    
    DefaultSize = F.get_size_inches()
    F.set_size_inches( (2, 5) )
    filename = settings.MEDIA_ROOT + '/images/test1.png'
    F.savefig(filename)
     
    data = simplejson.dumps({'filename': filename})   
    
    return HttpResponse(data, mimetype="application/javascript")

def test(request) :
    data = simplejson.dumps({'test': 'foo', 'test2':'bar', })   
    
    return HttpResponse(data, mimetype="application/javascript")

def test_matplotlib_weight_on_bit(request) :
    x = []
    y = []
    
    r = WITS0.objects.filter(recid=1,itemid=17, value__gt=0).order_by('-time_stamp')[:300]
        
    [x.append(v.value) for v in r]
    [y.append(v.time_stamp) for v in r]

    pylab.ylim(10,0)
    #pylab.xlim(0,40)
    pylab.grid(True)
    pylab
    pylab.plot(x,y)    
    F = pylab.gcf()

    # Now check everything with the defaults:
    DPI = F.get_dpi()    
    #DefaultSize = F.get_size_inches()
    F.set_size_inches( (2, 5) )
    filename = settings.MEDIA_ROOT + '/images/test1.png'
    F.savefig(filename)
     
    data = simplejson.dumps({'filename': filename})   
    
    #return HttpResponse(data, mimetype="application/javascript")
    return HttpResponseRedirect('/tdsurface/media/images/test1.png')


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
    
   
    
    d['time_stamp'] = datetime.datetime.utcnow()
    tc = ToolCalibration(time_stamp = d['time_stamp'],
                         tool=tool,
                         calibration_id=cal_vals[0],
                         tool_serial_number=cal_vals[1],
                         accelerometer_x_offset=cal_vals[2],
                         accelerometer_x_gain=cal_vals[3],
                         accelerometer_y_offset=cal_vals[4],
                         accelerometer_y_gain=cal_vals[5],
                         accelerometer_z_offset=cal_vals[6],
                         accelerometer_z_gain=cal_vals[7],
                         
                         magnetometer_x_offset=cal_vals[8],
                         magnetometer_x_gain=cal_vals[9],
                         magnetometer_y_offset=cal_vals[10],
                         magnetometer_y_gain=cal_vals[11],
                         magnetometer_z_offset=cal_vals[12],
                         magnetometer_z_gain=cal_vals[13],
                         
                         temperature_offset=cal_vals[14],
                         temperature_gain=cal_vals[15],
                        )                         
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
    log_address = tapi.get_current_log_address()
    bytes_in_log = int(log_address, 16) - int('D600', 16)
    scp = tapi.get_status_constant_profile()
    logging_interval = (0x10000*scp[88]) + scp[89]
    sensor = tapi.get_sensor_readings()
    tool_timer = tapi.get_timer()    
    tc.close()
    
    return render_to_response('tool_status.html', {'calibration': calibration, 'scp': scp, 'logging_interval': logging_interval, 'sensor': sensor, 'tool_timer': tool_timer, 'object': tool, 'log_address': log_address, 'bytes_in_log': bytes_in_log}, context_instance = RequestContext(request))


def tool_config(request, object_id, extra_context=None) :
    
    tool = Tool.objects.get(pk=object_id)

    data = {'object': tool}
    if request.method == 'POST': # If the form has been submitted...
        form = ToolConfigForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass                                            
            tc = ToolCom(port = settings.COMPORT, baudrate=settings.BAUDRATE, bytesize=settings.DATABITS, parity=settings.PARITY, stopbits=settings.STOPBITS, timeout=settings.COMPORT_TIMEOUT)
            tapi = ToolAPI(tc)
            
            comcheck = tapi.echo('ABC123')
            if comcheck != 'ABC123' :
                return HttpResponse("Communications check of the tool failed: '%s'" % comcheck)

            scp = tapi.get_status_constant_profile()
            logging_interval = (0x10000*scp[88]) + scp[89]
            if logging_interval != form.cleaned_data['logging_interval'] :
                tapi.set_logging_interval(form.cleaned_data['logging_interval'])

            if bool(scp[3]) != form.cleaned_data['advanced_squence_pattern'] :
                tapi.toggle_advanced_sequence_pattern_mode()

            if bool(scp[4]) != form.cleaned_data['tool_face_zeroing'] :
                tapi.toggle_tool_face_zeroing()

            if bool(scp[5]) != form.cleaned_data['rotation_sensing'] :
                tapi.toggle_rotation_sensing()
            
            tc.close()
           
    else:
        tc = ToolCom(port = settings.COMPORT, baudrate=settings.BAUDRATE, bytesize=settings.DATABITS, parity=settings.PARITY, stopbits=settings.STOPBITS, timeout=settings.COMPORT_TIMEOUT)
        tapi = ToolAPI(tc)
            
        comcheck = tapi.echo('ABC123')
        if comcheck != 'ABC123' :
            return HttpResponse("Communications check of the tool failed: '%s'" % comcheck)

        scp = tapi.get_status_constant_profile()
        initial = {'advanced_squence_pattern': bool(scp[3]),
                   'tool_face_zeroing': bool(scp[4]),
                   'rotation_sensing': bool(scp[5]),
                   'logging_interval': (0x10000*scp[88]) + scp[89],                   
                  }

        form = ToolConfigForm(initial = initial) # An unbound form

    data['form'] = form
        
    if extra_context :
        for key, value in extra_context.items():
            if callable(value):
                data[key] = value()
            else:
                data[key] = value    

    
    
    return render_to_response('tool_config_form.html', data, context_instance = RequestContext(request))



def tool_sensors(request, object_id, extra_context=None) :
    
    tool = Tool.objects.get(pk=object_id)
    
    tc = ToolCom(port = settings.COMPORT, baudrate=settings.BAUDRATE, bytesize=settings.DATABITS, parity=settings.PARITY, stopbits=settings.STOPBITS, timeout=settings.COMPORT_TIMEOUT)
    tapi = ToolAPI(tc)
    
    comcheck = tapi.echo('ABC123')
    if comcheck != 'ABC123' :
        tc.close()
        return HttpResponse("Communications check of the tool failed. Expected 'ABC123' got '%s'" % comcheck)
                
    sensor = tapi.get_sensor_readings()
    tc.close()
    
    data = {'sensor': sensor, 'object': tool}
    if extra_context :
        for key, value in extra_context.items():
            if callable(value):
                data[key] = value()
            else:
                data[key] = value    
    
    return render_to_response('tool_sensors.html', data, context_instance = RequestContext(request))


def run_roll_test(request, object_id, extra_context=None) :
    
    run = Run.objects.get(pk=object_id)

    data = {'object': run}
    if request.method == 'POST': # If the form has been submitted...
        form = RoleTestForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass                                            
            tc = ToolCom(port = settings.COMPORT, baudrate=settings.BAUDRATE, bytesize=settings.DATABITS, parity=settings.PARITY, stopbits=settings.STOPBITS, timeout=settings.COMPORT_TIMEOUT)
            tapi = ToolAPI(tc)
            
            comcheck = tapi.echo('ABC123')
            if comcheck != 'ABC123' :
                return HttpResponse("Communications check of the tool failed: '%s'" % comcheck)

            sensor = tapi.get_sensor_readings()
            tc.close()

            rt = RollTest(run=run,
                          temperature= '%.1f' % sensor.temperature,
                          comment = form.cleaned_data['comment'],
                          azimuth = '%.1f' % sensor.azimuth,
                          inclination = '%.1f' % sensor.inclination,
                          toolface = '%.1f' % sensor.tool_face,                                                    
                          gravity = '%.1f' % sensor.gravity,
                          magnetic = '%.1f' % sensor.magnetic,
                          gamma = '%.1f' % sensor.gamma_ray)
            rt.save()                
            
            data['sensor'] = sensor            
    else:
        form = RoleTestForm() # An unbound form

    data['form'] = form
        
    if extra_context :
        for key, value in extra_context.items():
            if callable(value):
                data[key] = value()
            else:
                data[key] = value    

    data['rolltest'] = RollTest.objects.filter(run=run).order_by('-time_stamp')
    
    return render_to_response('run_roll_test.html', data, context_instance = RequestContext(request))
        
    
def tool_sensors_json(request, object_id) :
    
    tool = Tool.objects.get(pk=object_id)
    
    tc = ToolCom(port = settings.COMPORT, baudrate=settings.BAUDRATE, bytesize=settings.DATABITS, parity=settings.PARITY, stopbits=settings.STOPBITS, timeout=settings.COMPORT_TIMEOUT)
    tapi = ToolAPI(tc)
    
    comcheck = tapi.echo('ABC123')
    if comcheck != 'ABC123' :
        tc.close()
        return HttpResponse("Communications check of the tool failed. Expected 'ABC123' got '%s'" % comcheck)
                
    sensor = tapi.get_sensor_readings()
    tc.close()
    
    data = simplejson.dumps(sensor.__dict__)   
    
    return HttpResponse(data, mimetype="application/javascript")        


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
    
    # Debug values
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
        
    if request.method == 'POST': # If the form has been submitted...
        
        form = ToolCalibrationForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Open port after validation so the user does not have to wait so long to error messages
            tc = ToolCom(port = settings.COMPORT, baudrate=settings.BAUDRATE, bytesize=settings.DATABITS, parity=settings.PARITY, stopbits=settings.STOPBITS, timeout=settings.COMPORT_TIMEOUT)
            tapi = ToolAPI(tc)
    
            comcheck = tapi.echo('ABC123')
            if comcheck != 'ABC123' :
                return HttpResponse("Communications check of the tool failed: '%s'" % comcheck)
                
            for k,v in form.cleaned_data.items() :                
                cur_cal = tapi.set_calibration_contant(k,int(v))
                
            tcal = ToolCalibration()
            tcal.tool = tool
            tcal.time_stamp =  datetime.datetime.utcnow()
            tcal.calibration_id = cur_cal[0]
            tcal.tool_serial_number = cur_cal[1]
            
            tcal.accelerometer_x_offset = form.cleaned_data['accelerometer_x_offset']
            tcal.accelerometer_x_gain = form.cleaned_data['accelerometer_x_gain']
            tcal.accelerometer_y_offset = form.cleaned_data['accelerometer_y_offset']
            tcal.accelerometer_y_gain = form.cleaned_data['accelerometer_y_gain']
            tcal.accelerometer_z_offset = form.cleaned_data['accelerometer_z_offset']
            tcal.accelerometer_z_gain = form.cleaned_data['accelerometer_z_gain']
            
            tcal.magnetometer_x_offset = form.cleaned_data['magnetometer_x_offset']
            tcal.magnetometer_x_gain = form.cleaned_data['magnetometer_x_gain']
            tcal.magnetometer_y_offset = form.cleaned_data['magnetometer_y_offset']
            tcal.magnetometer_y_gain = form.cleaned_data['magnetometer_y_gain']
            tcal.magnetometer_z_offset = form.cleaned_data['magnetometer_z_offset']
            tcal.magnetometer_z_gain = form.cleaned_data['magnetometer_z_gain']
            
            tcal.temperature_offset = form.cleaned_data['temperature_offset']
            tcal.temperature_gain = form.cleaned_data['temperature_gain']
            
            tcal.save()
    else:
        tc = ToolCom(port = settings.COMPORT, baudrate=settings.BAUDRATE, bytesize=settings.DATABITS, parity=settings.PARITY, stopbits=settings.STOPBITS, timeout=settings.COMPORT_TIMEOUT)
        tapi = ToolAPI(tc)
    
        comcheck = tapi.echo('ABC123')
        if comcheck != 'ABC123' :
            return HttpResponse("Communications check of the tool failed: '%s'" % comcheck)
        
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
            'temperature_offset':c[14],
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


def run_update(request, object_id, extra_context=None,) :
    
    run = Run.objects.get(pk=object_id)
    
    if request.method == 'POST': # If the form has been submitted...
        if request.POST['form_id'] == 'run_update_form' :
            run_form = RunForm(request.POST, instance=run) # A form bound to the POST data
            run_notes_form = RunNotesForm(initial = {'run': run.pk,})
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
        run_notes_form = RunNotesForm(initial = {'run': run.pk,})

    run_notes = RunNotes.objects.filter(run=run).order_by('time_stamp')
    
    data = {'run_form':run_form, 'run':run, 'object':run, 'run_notes_form': run_notes_form, 'run_notes': run_notes }
    
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
    t = int(Settings.objects.get(name='LOG_DOWNLOAD_SIZE').value)
    percent = 0
    if t :
        # Note: 28 bytes per log line
        percent = c * 28 * 100 / t
        
    data = simplejson.dumps({'downloading': p, 'cnt': c, 'status':s, 'percent':percent})   
    
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

    b = Settings.objects.get(name='LOG_DOWNLOAD_SIZE')
    b.value=str(tapi.get_bytes_in_log())
    b.save()


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
    
    tot, created = Settings.objects.get_or_create(name='LOG_DOWNLOAD_SIZE')
    tot.value=str('0')
    tot.save()
    
    s, created = Settings.objects.get_or_create(name='LOG_DOWNLOAD_STATUS')
    s.value=str('Starting Download')
    s.save()
    
    t = threading.Thread(target = _download_log, args=[object_id])
    t.setDaemon(True)
    t.start()
    return HttpResponse("Download Started")
        
def run_wits0_latest(request, object_id, num_latest=100, num_skip=0, extra_context={}) :
    run = Run.objects.get(pk=object_id)

    num_latest=int(num_latest)
    neg_num_latest = -num_latest
    num_skip = int(num_skip)

    wits = WITS0.objects.filter(run=run).order_by('-time_stamp','recid','itemid')[num_skip: num_skip+num_latest]
    
    data = {'wits':wits, 'num_latest':num_latest, 'neg_num_latest':neg_num_latest, 'num_skip':num_skip, 'run':run, 'object':run }
    
    for key, value in extra_context.items():
        if callable(value):
            data[key] = value()
        else:
            data[key] = value    
    
    return render_to_response('wits0_detail.html', data , context_instance = RequestContext(request)) 
    
def run_real_time_json(request, object_id, num_latest=5) :

    run = Run.objects.get(pk=object_id)
    num_latest=int(num_latest)

    azimuth = []
    [azimuth.append(x.value) for x in ToolMWDRealTime.objects.filter(run=run).filter(type='A').order_by('-time_stamp')[:num_latest] ]
    toolface = []
    [toolface.append(x.value) for x in ToolMWDRealTime.objects.filter(run=run).filter(type='F').order_by('-time_stamp')[:num_latest] ]
    inclination = []
    [inclination.append(x.value) for x in ToolMWDRealTime.objects.filter(run=run).filter(type='I').order_by('-time_stamp')[:num_latest] ]
    gamma = []
    [gamma.append({'timestamp': x.time_stamp.strftime('%H:%M:%S'),'value':x.value}) for x in ToolMWDRealTime.objects.filter(run=run).filter(type='R').order_by('-time_stamp')[:num_latest] ]
    hole_depth = []
    [hole_depth.append({'timestamp': x.time_stamp.strftime('%H:%M:%S'),'value':x.value}) for x in WITS0.objects.filter(run=run).filter(recid=1,itemid=10).order_by('-time_stamp')[:num_latest] ]
    bit_depth = []
    [bit_depth.append({'timestamp': x.time_stamp.strftime('%H:%M:%S'),'value':x.value}) for x in WITS0.objects.filter(run=run).filter(recid=1,itemid=8).order_by('-time_stamp')[:num_latest] ]    
    weight_on_bit = []
    [weight_on_bit.append({'timestamp': x.time_stamp.strftime('%H:%M:%S'),'value':x.value}) for x in WITS0.objects.filter(run=run).filter(recid=1,itemid=17).order_by('-time_stamp')[:num_latest] ]
    mud_flow_in = []
    [mud_flow_in.append({'timestamp': x.time_stamp.strftime('%H:%M:%S'),'value':x.value}) for x in WITS0.objects.filter(run=run).filter(recid=1,itemid=30).order_by('-time_stamp')[:num_latest] ]
    
    data =  {
        'azimuth': azimuth,
        'toolface': toolface,    
        'inclination': inclination,
        'gamma': gamma,
        'hole_depth': hole_depth,
        'bit_depth': bit_depth,        
        'weight_on_bit': weight_on_bit,
        'mud_flow_in': mud_flow_in,
        }
    
    data = simplejson.dumps(data)   
    
    return HttpResponse(data, mimetype="application/javascript")
    
def run_pipe_tally_grid(request, object_id) :

    page = int(request.GET['page'])
    rows = int(request.GET['rows'])
    
    sort_order= ''
    if request.GET['sord'] == 'desc' :
        sort_order= '-'
    
    pt = PipeTally.objects.filter(run=object_id).order_by(sort_order+request.GET['sidx'])
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
        rd["id"] = r.pk        
        rd['order'] = str(r.order)        
        rd['duration'] = str(r.duration)
        if r.duration == None :
            rd['duration'] = ''
        rd['pipe_length'] = str(r.pipe_length)
        rd['units'] = r.length_units
        rd['note'] = r.note
        data['rows'].append(rd)

    data = simplejson.dumps(data)   
    #data = """{"total": 1, "page": 1, "records": 3, "rows": [{ "cell": ["test1", "0", "30", "ft", "test"], "id": "1"}, {"cell": ["test2", "0", "29.7", "ft", ""], "id": "2"}, {"cell": ["test1", "0", "29.7", "ft", "Notes"], "id": "3"}]}"""
    return HttpResponse(data, mimetype="application/javascript")

        

    
    
    
