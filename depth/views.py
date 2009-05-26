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
from time import mktime
from datetime import datetime
from datetime import timedelta
from pytz import timezone
import pytz

from tdsurface.depth.models import *
from tdsurface.depth.forms import *

from tdsurface.bha.models import BHA

from tdsurface.toolcom import ToolCom
from tdsurface.toolapi import ToolAPI
from django.conf import settings

import threading
import logging

logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s', filename='/var/log/tdsurface/tdsurface.log',level=logging.DEBUG,)


def test(request) :
    form = RunFormForm()
        
    return render_to_response('generic_form.html', {'form': form,}, context_instance = RequestContext(request))



def mainmenu(request) :
    d = {}
    return render_to_response('mainmenu.html', d)
    
    
def pull_calibration(request, object_id) :    
    d = {}
    
    tool = Tool.objects.get(pk=object_id)
    d['object'] = tool
    
    tc = ToolCom(port = settings.COMPORT, baudrate=settings.BAUDRATE, bytesize=settings.DATABITS, parity=settings.PARITY, stopbits=settings.STOPBITS, timeout=settings.COMPORT_TIMEOUT)
    tapi = ToolAPI(tc)
    
    if not tapi.sync_tool() :
        tc.close()
        return HttpResponse('Communications sync with the tool failed.')
    
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
            
            if not tapi.sync_tool() :
                tc.close()
                return HttpResponse('Communications sync with the tool failed.')
                
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
    
    if not tapi.sync_tool() :
        tc.close()
        return HttpResponse('Communications sync with the tool failed.')
               
    tapi.set_time(datetime.datetime(2001,1,1,0,0,0)) # Set the timer to 0 using tool base time (2001-01-01 00:00:00) (year & month are ignored on the timer)
    
    tc.close()
    
    return render_to_response('message.html', {'message': 'Tool timer reset to 0', 'navigation_template': 'tool_menu.html' , 'object':tool }, context_instance = RequestContext(request))
        
def tool_status(request, object_id) :
    
    tool = Tool.objects.get(pk=object_id)
    
    tc = ToolCom(port = settings.COMPORT, baudrate=settings.BAUDRATE, bytesize=settings.DATABITS, parity=settings.PARITY, stopbits=settings.STOPBITS, timeout=settings.COMPORT_TIMEOUT)
    tapi = ToolAPI(tc)    
        
    if not tapi.sync_tool() :
        tc.close()
        return HttpResponse('Communications sync with the tool failed.')
    
    calibration = tapi.get_calibration_contants()
    log_address = tapi.get_current_log_address()
    bytes_in_log = tapi.get_bytes_in_log()
    scp = tapi.get_status_constant_profile()
    logging_interval = scp.logging_interval
    sensor = tapi.get_sensor_readings()
    tool_timer = tapi.get_timer()    
    tc.close()
    
    return render_to_response('tool_status.html', {'calibration': calibration, 'scp': scp, 'logging_interval': logging_interval, 'sensor': sensor, 'tool_timer': tool_timer, 'object': tool, 'log_address': log_address, 'bytes_in_log': bytes_in_log}, context_instance = RequestContext(request))


def tool_general_config(request, object_id, extra_context=None) :
    
    tool = Tool.objects.get(pk=object_id)

    data = {'object': tool}
    if request.method == 'POST': # If the form has been submitted...
        form = ToolGeneralConfigForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass                                            
            tc = ToolCom(port = settings.COMPORT, baudrate=settings.BAUDRATE, bytesize=settings.DATABITS, parity=settings.PARITY, stopbits=settings.STOPBITS, timeout=settings.COMPORT_TIMEOUT)
            tapi = ToolAPI(tc)
            
            if not tapi.sync_tool() :
                tc.close()
                return HttpResponse('Communications sync with the tool failed.')
        
            scp = tapi.get_status_constant_profile()
            logging_interval = scp.logging_interval
            if logging_interval != form.cleaned_data['logging_interval'] :
                tapi.set_logging_interval(form.cleaned_data['logging_interval'])

            if scp.advanced_sequence_pattern != form.cleaned_data['advanced_sequence_pattern'] :
                tapi.toggle_advanced_sequence_pattern_mode()

            if scp.tool_face_zeroing != form.cleaned_data['tool_face_zeroing'] :
                tapi.toggle_tool_face_zeroing()

            if scp.rotation_sensing != form.cleaned_data['rotation_sensing'] :
                tapi.toggle_rotation_sensing()

            if scp.gammaray_log_size != form.cleaned_data['gammaray_log_size'] :
                tapi.set_gammaray_log_size(form.cleaned_data['gammaray_log_size'])            
                                
            tc.close()
           
    else:
        tc = ToolCom(port = settings.COMPORT, baudrate=settings.BAUDRATE, bytesize=settings.DATABITS, parity=settings.PARITY, stopbits=settings.STOPBITS, timeout=settings.COMPORT_TIMEOUT)
        tapi = ToolAPI(tc)
            
        if not tapi.sync_tool() :
            tc.close()
            return HttpResponse('Communications sync with the tool failed.')
        
        scp = tapi.get_status_constant_profile()
        initial = {'advanced_sequence_pattern': scp.advanced_sequence_pattern,
                   'tool_face_zeroing': scp.tool_face_zeroing,
                   'rotation_sensing': scp.rotation_sensing,
                   'logging_interval': scp.logging_interval,
                   'gammaray_log_size': scp.gammaray_log_size,
                          
                  }

        form = ToolGeneralConfigForm(initial = initial) # An unbound form

    data['form'] = form
        
    if extra_context :
        for key, value in extra_context.items():
            if callable(value):
                data[key] = value()
            else:
                data[key] = value    

    
    
    return render_to_response('tool_general_config_form.html', data, context_instance = RequestContext(request))


def tool_motor_config(request, object_id, extra_context=None) :
    
    tool = Tool.objects.get(pk=object_id)

    data = {'object': tool}
    if request.method == 'POST': # If the form has been submitted...
        form = ToolMotorConfigForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass                                            
            tc = ToolCom(port = settings.COMPORT, baudrate=settings.BAUDRATE, bytesize=settings.DATABITS, parity=settings.PARITY, stopbits=settings.STOPBITS, timeout=settings.COMPORT_TIMEOUT)
            tapi = ToolAPI(tc)
            
            if not tapi.sync_tool() :
                tc.close()
                return HttpResponse('Communications sync with the tool failed.')

            scp = tapi.get_status_constant_profile()
            ms = tapi.get_motor_status()
            
            if scp.motor_open_position_offset != form.cleaned_data['open_position_offset'] :
                tapi.set_motor_open_position_offset(form.cleaned_data['open_position_offset'])
            if scp.motor_shut_position_offset != form.cleaned_data['shut_position_offset'] :
                tapi.set_motor_shut_position_offset(form.cleaned_data['shut_position_offset'])
                
            if scp.motor_open_max_acceleration != form.cleaned_data['open_max_acceleration'] :
                tapi.set_motor_open_max_acceleration(form.cleaned_data['open_max_acceleration'])
            if scp.motor_shut_max_acceleration != form.cleaned_data['shut_max_acceleration'] :
                tapi.set_motor_shut_max_acceleration(form.cleaned_data['shut_max_acceleration'])
            
            if scp.motor_open_acceleration_delay != form.cleaned_data['open_acceleration_delay'] :
                tapi.set_motor_open_acceleration_delay(form.cleaned_data['open_acceleration_delay'])
            if scp.motor_shut_acceleration_delay != form.cleaned_data['shut_acceleration_delay'] :
                tapi.set_motor_shut_acceleration_delay(form.cleaned_data['shut_acceleration_delay'])

            if scp.motor_calibration_initial_acceleration != form.cleaned_data['calibration_initial_acceleration'] :
                tapi.set_motor_calibration_initial_acceleration(form.cleaned_data['calibration_initial_acceleration'])

            if scp.pulse_time != form.cleaned_data['pulse_time'] :
                tapi.set_pulse_time(form.cleaned_data['pulse_time'])
                tapi.set_code_pulse_time(form.cleaned_data['pulse_time'])

            if scp.narrow_pulse_time != form.cleaned_data['narrow_pulse_time'] :
                tapi.set_narrow_pulse_time(form.cleaned_data['narrow_pulse_time'])

            if scp.wide_pulse_time != form.cleaned_data['wide_pulse_time'] :
                tapi.set_wide_pulse_time(form.cleaned_data['wide_pulse_time'])

            if scp.gear_numerator != form.cleaned_data['gear_numerator'] :
                tapi.set_gear_numerator(form.cleaned_data['gear_numerator'])

            if scp.gear_denominator != form.cleaned_data['gear_denominator'] :
                tapi.set_gear_denominator(form.cleaned_data['gear_denominator'])
                
            tc.close()
           
    else:
        tc = ToolCom(port = settings.COMPORT, baudrate=settings.BAUDRATE, bytesize=settings.DATABITS, parity=settings.PARITY, stopbits=settings.STOPBITS, timeout=settings.COMPORT_TIMEOUT)
        tapi = ToolAPI(tc)
            
        if not tapi.sync_tool() :
            tc.close()
            return HttpResponse('Communications sync with the tool failed.')

        scp = tapi.get_status_constant_profile()
        ms = tapi.get_motor_status()
        tc.close()
        
        initial = {'open_position_offset': scp.motor_open_position_offset,
                   'open_acceleration_delay': scp.motor_open_acceleration_delay,
                   'open_max_acceleration': scp.motor_open_max_acceleration,
                   'shut_position_offset': scp.motor_shut_position_offset,
                   'shut_acceleration_delay': scp.motor_shut_acceleration_delay,
                   'shut_max_acceleration': scp.motor_shut_max_acceleration,
                   'calibration_initial_acceleration': scp.motor_calibration_initial_acceleration,
                   'pulse_time': scp.pulse_time,
                   'narrow_pulse_time': scp.narrow_pulse_time,
                   'wide_pulse_time': scp.wide_pulse_time,
                   'gear_numerator': scp.gear_numerator,
                   'gear_denominator': scp.gear_denominator,           
                  }

        form = ToolMotorConfigForm(initial = initial) # An unbound form

    data['form'] = form
    data['scp'] = scp
    data['ms'] = ms
    
    if extra_context :
        for key, value in extra_context.items():
            if callable(value):
                data[key] = value()
            else:
                data[key] = value    

    
    
    return render_to_response('tool_motor_config_form.html', data, context_instance = RequestContext(request))


def tool_motor_command(request, object_id, command) :
    
    tool = Tool.objects.get(pk=object_id)

    tc = ToolCom(port = settings.COMPORT, baudrate=settings.BAUDRATE, bytesize=settings.DATABITS, parity=settings.PARITY, stopbits=settings.STOPBITS, timeout=settings.COMPORT_TIMEOUT)
    tapi = ToolAPI(tc)

    if command == 'capture' :
        tapi.motor_capture()
    elif command == 'release' :
        tapi.motor_release()
    elif command == 'open' :
        tapi.motor_open()
    elif command == 'shut' :
        tapi.motor_shut()
    else :
        tc.close()
        return HttpResponse("Invalid Motor Command '%s'" % command)    

    tc.close()
    return HttpResponse("'%s' command complete" % command)    

def tool_sensors(request, object_id, extra_context=None) :
    
    tool = Tool.objects.get(pk=object_id)
    
    tc = ToolCom(port = settings.COMPORT, baudrate=settings.BAUDRATE, bytesize=settings.DATABITS, parity=settings.PARITY, stopbits=settings.STOPBITS, timeout=settings.COMPORT_TIMEOUT)
    tapi = ToolAPI(tc)
    
    if not tapi.sync_tool() :
        tc.close()
        return HttpResponse('Communications sync with the tool failed.')
                
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
            
            if not tapi.sync_tool() :
                tc.close()
                return HttpResponse('Communications sync with the tool failed.')

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



def tool_face_zero_json(request, object_id) :
    
    tool = Tool.objects.get(pk=object_id)
    
    tc = ToolCom(port = settings.COMPORT, baudrate=settings.BAUDRATE, bytesize=settings.DATABITS, parity=settings.PARITY, stopbits=settings.STOPBITS, timeout=settings.COMPORT_TIMEOUT)
    tapi = ToolAPI(tc)
    
    sensor = tapi.get_sensor_readings()
    time.sleep(1)
    scp = tapi.get_status_constant_profile()        
    tc.close()
    
    data = {'tool_face': sensor.tool_face, 'tool_face_zeroed': scp.tool_face_zeroing }

    data = simplejson.dumps(data)
    
    return HttpResponse(data, mimetype="application/javascript")        


def tool_face_zero_start(request, object_id) :
    
    tool = Tool.objects.get(pk=object_id)
    
    tc = ToolCom(port = settings.COMPORT, baudrate=settings.BAUDRATE, bytesize=settings.DATABITS, parity=settings.PARITY, stopbits=settings.STOPBITS, timeout=settings.COMPORT_TIMEOUT)
    tapi = ToolAPI(tc)
        
    scp = tapi.get_status_constant_profile()
    if scp.tool_face_zeroing :
        tapi.toggle_tool_face_zeroing()
        
    tc.close()
    
    return HttpResponse("Waiting for Gamma Ray Source...")

    
def tool_sensors_json(request, object_id) :
    
    tool = Tool.objects.get(pk=object_id)
    
    tc = ToolCom(port = settings.COMPORT, baudrate=settings.BAUDRATE, bytesize=settings.DATABITS, parity=settings.PARITY, stopbits=settings.STOPBITS, timeout=settings.COMPORT_TIMEOUT)
    tapi = ToolAPI(tc)
                    
    sensor = tapi.get_sensor_readings()
    tc.close()
    
    data = simplejson.dumps(sensor.__dict__)   
    
    return HttpResponse(data, mimetype="application/javascript")        

def tool_motor_calibrate_json(request, object_id) :
    
    tool = Tool.objects.get(pk=object_id)
    
    tc = ToolCom(port = settings.COMPORT, baudrate=settings.BAUDRATE, bytesize=settings.DATABITS, parity=settings.PARITY, stopbits=settings.STOPBITS, timeout=settings.COMPORT_TIMEOUT)
    tapi = ToolAPI(tc)
    
    if not tapi.sync_tool() :
        tc.close()
        return HttpResponse('Communications sync with the tool failed.')
                
    ms = tapi.motor_calibrate()
    tc.close()
    
    data = simplejson.dumps(ms.__dict__)   
    
    return HttpResponse(data, mimetype="application/javascript")
    

def tool_pulse_pattern_profile(request, object_id) :
    
    tool = Tool.objects.get(pk=object_id)

    tc = ToolCom(port = settings.COMPORT, baudrate=settings.BAUDRATE, bytesize=settings.DATABITS, parity=settings.PARITY, stopbits=settings.STOPBITS, timeout=settings.COMPORT_TIMEOUT)
    tapi = ToolAPI(tc)

    if not tapi.sync_tool() :
        tc.close()
        return HttpResponse('Communications sync with the tool failed.')

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
        
        adv_seq = False
        adv_seq_cur = False
        print 'scp_adv_seq_cur', request.POST['scp_adv_seq_cur']
        if request.POST['scp_adv_seq_cur'] == 'True' :
            adv_seq_cur = True
        if request.POST.has_key('scp_adv_seq') :
            adv_seq=True
        if adv_seq != adv_seq_cur :
            tapi.toggle_advanced_sequence_pattern_mode()
                
    ppp = tapi.get_pulse_pattern_profile()
    ppsp = tapi.get_pulse_pattern_sequence_profile()
    scp = tapi.get_status_constant_profile()
    tc.close()
        
    return render_to_response('tool_pulse_pattern_profile.html', {'ppp': ppp, 'ppsp': ppsp, 'scp': scp, 'object': tool, }, context_instance = RequestContext(request))


def tool_frame_mode_buffer(request, object_id) :
    
    tool = Tool.objects.get(pk=object_id)

    tc = ToolCom(port = settings.COMPORT, baudrate=settings.BAUDRATE, bytesize=settings.DATABITS, parity=settings.PARITY, stopbits=settings.STOPBITS, timeout=settings.COMPORT_TIMEOUT)
    tapi = ToolAPI(tc)

    if not tapi.sync_tool() :
        tc.close()
        return HttpResponse('Communications sync with the tool failed.')

    if request.method == 'POST':
        form = ToolFrameModeBufferForm(request.POST) 
        
        if form.is_valid(): 
            mode_cur = tapi.get_frame_mode_buffer()
        
            for frame in range(len(mode_cur)) :            
                mode = form.cleaned_data['fmb'+str(frame)]
                
                if (mode != mode_cur[frame]):
                    tapi.set_frame_mode_buffer(frame, mode)                    

    else :
        mode_cur = tapi.get_frame_mode_buffer()
        b = {}
        for frame in range(len(mode_cur)) :
            b['fmb'+str(frame)] = mode_cur[frame]
        form = ToolFrameModeBufferForm(initial = b)
    tc.close()
    
    
    return render_to_response('generic_form.html', {'object': tool, 'form': form, 'subtitle': 'Frame Mode Configuration', 'navigation_template': 'tool_config_menu.html'}, context_instance = RequestContext(request))


def tool_purge_log(request, object_id) :
    
    tool = Tool.objects.get(pk=object_id)
    
    tc = ToolCom(port = settings.COMPORT, baudrate=settings.BAUDRATE, bytesize=settings.DATABITS, parity=settings.PARITY, stopbits=settings.STOPBITS, timeout=settings.COMPORT_TIMEOUT)
    tapi = ToolAPI(tc)
    
    if not tapi.sync_tool() :
        tc.close()
        return HttpResponse('Communications sync with the tool failed.')
                
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
    
            if not tapi.sync_tool() :
                tc.close()
                return HttpResponse('Communications sync with the tool failed.')
                
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
    
        if not tapi.sync_tool() :
            tc.close()
            return HttpResponse('Communications sync with the tool failed.')
                
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


def well_activate(request, object_id) :    
    d = {}
    
    well = Well.objects.get(pk=object_id)
   
    active_well, created = Settings.objects.get_or_create(name='ACTIVE_WELL')
    
    active_well.value=well.pk
    active_well.save()
        
    return HttpResponseRedirect(reverse('well_list'))    


def run_create(request, template_name,
        post_save_redirect, extra_context=None) :

    if request.method == 'POST' :
        run_form = RunFormForm(request.POST)
        if run_form.is_valid():
            well_bore = run_form.cleaned_data['well_bore']
            tool = run_form.cleaned_data['tool']
            ltz = timezone(well_bore.well.timezone)
            start_time = run_form.cleaned_data['start_time']
            if start_time :
                start_time = ltz.localize(start_time).astimezone(pytz.utc).replace(tzinfo=None)
                
            end_time = run_form.cleaned_data['end_time']
            if end_time :
                end_time = ltz.localize(end_time).astimezone(pytz.utc).replace(tzinfo=None)
            
            new_run = Run(name=run_form.cleaned_data['name'],
                          start_time=start_time,
                          end_time=end_time,
                          well_bore=well_bore,
                          tool=tool)
            new_run.save()                                        
            return HttpResponseRedirect(post_save_redirect % new_run.__dict__)
    else :
        run_form = RunFormForm()

    data = { 'form':run_form }
    for key, value in extra_context.items():
        if callable(value):
            data[key] = value()
        else:
            data[key] = value    
    
    return render_to_response(template_name , data, context_instance = RequestContext(request))

        
def run_update(request, object_id, extra_context=None,) :
    
    run = Run.objects.get(pk=object_id)
    
    if request.method == 'POST': # If the form has been submitted...
        if request.POST['form_id'] == 'run_update_form' :
            run_form = RunFormForm(request.POST) # A form bound to the POST data
            run_notes_form = RunNotesForm()
            if run_form.is_valid(): # All validation rules pass                
                #well_bore = WellBore.objects.get(pk=run_form.cleaned_data['well_bore'])
                well_bore = run_form.cleaned_data['well_bore']
                # Convert user entered Well Local Time to to UTC
                wlt = timezone(well_bore.well.timezone)                
                start_time = run_form.cleaned_data['start_time']
                if start_time :
                    start_time = wlt.localize(start_time).astimezone(pytz.utc).replace(tzinfo=None)
                    
                end_time = run_form.cleaned_data['end_time']
                if end_time :
                    end_time = wlt.localize(end_time).astimezone(pytz.utc).replace(tzinfo=None)
                
                run.name=run_form.cleaned_data['name']
                run.tool = run_form.cleaned_data['tool']
                run.start_time=start_time
                run.end_time=end_time
                run.well_bore=well_bore                
                run.save()           
                return HttpResponseRedirect(reverse('run_update', args=[run.pk]))
        else :
            run_notes_form = RunNotesForm(request.POST) # A form bound to the POST data
            run_form = RunForm(instance = run)
            if run_notes_form.is_valid() :
                run_notes = RunNotes(run=run, notes = run_notes_form.cleaned_data['notes'])
                run_notes.save()
                return HttpResponseRedirect(reverse('run_update', args=[run.pk]))
    else:
        # Converted DB UTC to well local time
        wlt = timezone(run.well_bore.well.timezone)
        start_time = run.start_time
        if start_time :
            start_time = pytz.utc.localize(start_time).astimezone(wlt).replace(tzinfo=None)
        end_time = run.end_time
        if end_time :
            end_time = pytz.utc.localize(end_time).astimezone(wlt).replace(tzinfo=None)
        initial = {
                    'name':run.name,
                    'start_time':start_time,
                    'end_time':end_time,
                    'well_bore':run.well_bore_id,
                    'tool':run.tool_id                    
                  }
        run_form = RunFormForm(initial=initial)
        run_notes_form = RunNotesForm()

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
        percent = c * 100 / t
        
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
    if not tapi.sync_tool() :
        p.value=''
        p.save()
        c.value = str(-1)
        c.save()
        s.value="Communications sync with the tool failed."
        s.save()
        tc.close()
        return

    s.value='Getting calibration constants'
    s.save()
    cal_vals = tapi.get_calibration_contants()
    cal = ToolCalibration(time_stamp = datetime.datetime.utcnow(),
                         tool=run.tool,
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
    cal.save()
    run.tool_calibration = cal
    run.save()

    s.value='Getting gamma interval'
    s.save()
    scp = tapi.get_status_constant_profile()
    gamma_interval = scp.logging_interval/1000/scp.gammaray_log_size

    s.value='Calculating log size'
    s.save()
    b = Settings.objects.get(name='LOG_DOWNLOAD_SIZE')    
    # Lines of log = 20 bytes for the Grav, Mag & Temp + 2 per gamma ray
    b.value=str(tapi.get_bytes_in_log()/( 20 + (scp.gammaray_log_size * 2) ))
    b.save()

    s.value='Downloading'
    s.save()

    rc = True
    for log_data in tapi.get_log_generator() :
                
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
        d.save()
        
        seconds = log_data.seconds
        for g in log_data.gamma :
            d = ToolMWDLogGamma()
            d.run_id = run_id
            d.seconds = seconds
            seconds += gamma_interval
            d.status = log_data.status
            d.gamma = g
            d.save()
                
        p = Settings.objects.get(name='LOG_DOWNLOAD_IN_PROGRESS')        
        rc = bool(p.value)
        if rc != True :
            tapi.get_log_cancel()

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

    wits = WITS0.objects.filter(well=run.well_bore.well).order_by('-time_stamp','recid','itemid')[num_skip: num_skip+num_latest]
    
    data = {'wits':wits, 'num_latest':num_latest, 'neg_num_latest':neg_num_latest, 'num_skip':num_skip, 'run':run, 'object':run }
    
    for key, value in extra_context.items():
        if callable(value):
            data[key] = value()
        else:
            data[key] = value    
    
    return render_to_response('wits0_detail.html', data , context_instance = RequestContext(request)) 
    
def well_real_time_json(request, object_id, num_latest=5) :

    well = Well.objects.get(pk=object_id)
    num_latest=int(num_latest)
    wltz = pytz.timezone(well.timezone)

    hoursago = datetime.datetime.utcnow() - timedelta(hours=1)
    
    azimuth = []
    [azimuth.append({'timestamp': pytz.utc.localize(x.time_stamp).astimezone(wltz).replace(tzinfo=None).strftime('%Y/%m/%d %H:%M:%S'), 'value':x.value}) for x in ToolMWDRealTime.objects.filter(well=well, type='azimuth', time_stamp__gt=hoursago).order_by('-time_stamp')[:num_latest] ]
    toolface = []
    [toolface.append({'timestamp': pytz.utc.localize(x.time_stamp).astimezone(wltz).replace(tzinfo=None).strftime('%Y/%m/%d %H:%M:%S'), 'value':x.value}) for x in ToolMWDRealTime.objects.filter(well=well, type='toolface', time_stamp__gt=hoursago).order_by('-time_stamp')[:num_latest] ]
    inclination = []
    [inclination.append({'timestamp': pytz.utc.localize(x.time_stamp).astimezone(wltz).replace(tzinfo=None).strftime('%Y/%m/%d %H:%M:%S'), 'value':x.value}) for x in ToolMWDRealTime.objects.filter(well=well, type='inclination', time_stamp__gt=hoursago).order_by('-time_stamp')[:num_latest] ]
    gamma = []
    
    [gamma.append({'timestamp': pytz.utc.localize(x.time_stamp).astimezone(wltz).replace(tzinfo=None).strftime('%Y/%m/%d %H:%M:%S'),'value':x.value}) for x in ToolMWDRealTime.objects.filter(well=well).filter(type='gammaray', time_stamp__gt=hoursago).order_by('-time_stamp')[:num_latest*10] ]
    temperature = []
    [temperature.append({'timestamp': pytz.utc.localize(x.time_stamp).astimezone(wltz).replace(tzinfo=None).strftime('%Y/%m/%d %H:%M:%S'), 'value':x.value}) for x in ToolMWDRealTime.objects.filter(well=well, type='temperature', time_stamp__gt=hoursago).order_by('-time_stamp')[:num_latest] ]


    hole_depth = []
    [hole_depth.append({'timestamp': pytz.utc.localize(x.time_stamp).astimezone(wltz).replace(tzinfo=None).strftime('%Y/%m/%d %H:%M:%S'),'value':x.value}) for x in WITS0.objects.filter(well=well).filter(recid=1,itemid=10).order_by('-time_stamp')[:num_latest] ]
    bit_depth = []
    [bit_depth.append({'timestamp': pytz.utc.localize(x.time_stamp).astimezone(wltz).replace(tzinfo=None).strftime('%Y/%m/%d %H:%M:%S'),'value':x.value}) for x in WITS0.objects.filter(well=well).filter(recid=1,itemid=8).order_by('-time_stamp')[:num_latest] ]    
    weight_on_bit = []
    [weight_on_bit.append({'timestamp': pytz.utc.localize(x.time_stamp).astimezone(wltz).replace(tzinfo=None).strftime('%Y/%m/%d %H:%M:%S'),'value':x.value}) for x in WITS0.objects.filter(well=well).filter(recid=1,itemid=17).order_by('-time_stamp')[:num_latest] ]
    mud_flow_in = []
    [mud_flow_in.append({'timestamp': pytz.utc.localize(x.time_stamp).astimezone(wltz).replace(tzinfo=None).strftime('%Y/%m/%d %H:%M:%S'),'value':x.value}) for x in WITS0.objects.filter(well=well).filter(recid=1,itemid=30).order_by('-time_stamp')[:num_latest] ]
    rop = []
    [rop.append({'timestamp': pytz.utc.localize(x.time_stamp).astimezone(wltz).replace(tzinfo=None).strftime('%Y/%m/%d %H:%M:%S'),'value':x.value}) for x in WITS0.objects.filter(well=well).filter(recid=1,itemid=13).order_by('-time_stamp')[:num_latest] ]
    
    data =  {
        'azimuth': azimuth,
        'toolface': toolface,    
        'inclination': inclination,
        'gamma': gamma,
        'temperature': temperature,
        'hole_depth': hole_depth,
        'bit_depth': bit_depth,        
        'weight_on_bit': weight_on_bit,
        'mud_flow_in': mud_flow_in,
        'rop': rop,
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

        
def run_pipe_tally_grid_edit(request, object_id) :    
    run = Run.objects.get(pk=object_id)
    
    if request.method=='POST' :
        if request.POST['id'] == 'new' :
            order = request.POST['order']
            if order == 'end' :
                order = 9999
            order = int(order)
                           
            pt = PipeTally(run = run,
                           order = order,                           
                           pipe_length = request.POST['pipe_length'],
                           length_units = request.POST['units'],
                           note = request.POST['note'])
            if request.POST['duration'] :
                pt.duration = request.POST['duration']
            
            ptl = PipeTally.objects.filter(run=object_id).order_by('order')
            max_order = 0
            for x in ptl :
                if x.order >= pt.order :
                    x.order += 1                
                    x.save()
                if x.order > max_order :
                    max_order = x.order            

            if pt.order >= max_order :
                pt.order = max_order + 1
            pt.save()    
            
        else :            
            pt = PipeTally.objects.get(pk = request.POST['id'])            
            order = int(request.POST['order'])
            if pt.order != order :
                ptl = PipeTally.objects.filter(order = order)
                if len(ptl) :
                    ptl[0].order = pt.order
                    ptl[0].save()                
            pt.order = order
            pt.length_units = request.POST['units']
            if request.POST['duration'] :
                pt.duration = request.POST['duration']
            pt.note = request.POST['note']
            pt.save()                
        
            
    data = simplejson.dumps(pt.pk)       
    return HttpResponse(data, mimetype="application/javascript")            
    #return HttpResponse(str(pt.pk), mimetype="test/plain")
    

def run_pipe_tally_grid_delete(request, object_id) :    
    run = Run.objects.get(pk=object_id)
    
    if request.method=='POST' :        
        pt = PipeTally.objects.get(pk = request.POST['id'])
        order = pt.order
        pt.delete()
        ptl = PipeTally.objects.filter(run=object_id).order_by('order')
        for x in ptl :
            if x.order > order :
                x.order -= 1                
                x.save()
            
        return HttpResponse('true', mimetype="application/javascript")            




def wits0_depth_to_mwdlog(request, object_id) :
    run = Run.objects.get(pk=object_id)

    mwdlogs = ToolMWDLog.objects.filter(run=run)
    mwdgammalogs = ToolMWDLogGamma.objects.filter(run=run)
    bha, created = BHA.objects.get_or_create(run=run)

    for logs in (mwdlogs,mwdgammalogs) :    
        for l in logs :
            time_stamp = run.start_time + timedelta(seconds=l.seconds)
            try :                
                lower = WITS0.objects.filter(well = run.well_bore.well, recid=1, itemid=8, time_stamp__lt = time_stamp ).order_by('-time_stamp')[0]
                higher = WITS0.objects.filter(well = run.well_bore.well, recid=1, itemid=8, time_stamp__gt = time_stamp ).order_by('time_stamp')[0]
            except:
                continue

            # Linear Interpolation where x = seconds and y = depth    
            x = time.mktime(time_stamp.timetuple())
            xa = time.mktime(lower.time_stamp.timetuple())
            xb = time.mktime(higher.time_stamp.timetuple())

            ya = float(lower.value)
            yb = float(higher.value)
            
            y = ya + ((x - xa) * (yb - ya))/(xb - xa)
            y = y - float(bha.gammaray_sensor_offset)          #Offest position of tool in BHA
            
            l.depth=str(y)
            l.depth_units='ft'
            l.save()

    return HttpResponseRedirect(reverse('las_from_mwdlog', args=[object_id]))    


def wits0_depth_to_rtlog(request, object_id) :
    run = Run.objects.get(pk=object_id)
    bha, created = BHA.objects.get_or_create(run=run)
    
    if not run.start_time or not run.end_time :
        return render_to_response('message.html', {'message': 'The Run Start Time and End Time are required', 'navigation_template': 'run_detail_menu.html' , 'object':run }, context_instance = RequestContext(request))
        
    logs = ToolMWDRealTime.objects.filter(well=run.well_bore.well, time_stamp__gte=run.start_time, time_stamp__lte=run.end_time)

    for l in logs :
        time_stamp = l.time_stamp
        try :            
            lower = WITS0.objects.filter(well=run.well_bore.well, recid=1, itemid=8, time_stamp__lt = time_stamp ).order_by('-time_stamp')[0]
            higher = WITS0.objects.filter(well=run.well_bore.well, recid=1, itemid=8, time_stamp__gt = time_stamp ).order_by('time_stamp')[0]
        except:
            continue

        # Linear Interpolation where x = seconds and y = depth    
        x = time.mktime(time_stamp.timetuple())
        xa = time.mktime(lower.time_stamp.timetuple())
        xb = time.mktime(higher.time_stamp.timetuple())

        ya = float(lower.value)
        yb = float(higher.value)
        
        y = ya + ((x - xa) * (yb - ya))/(xb - xa)
        y = y - float(bha.gammaray_sensor_offset)          #Offest position of tool in BHA

        l.depth=str(y)
        l.depth_units='ft'
        l.save()

    return HttpResponseRedirect(reverse('las_from_mwdlog', args=[object_id]))    
    
