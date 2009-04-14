from django import forms
from django.db import models
from django.forms import ModelForm
from django.contrib.localflavor.us.forms import USPhoneNumberField
from django.contrib.localflavor.us.forms import USStateSelect
from tdsurface.depth.models import *

from tdsurface.widgets import *

form_css = '/tdsurface/media/css/forms.css'

class WellForm(ModelForm) :
    
    class Meta :
        model = Well

    class Media:
        css = {
                'all': (form_css,)
        }

    license_date = forms.DateField(required=False, widget=DynarchDateTimeWidget(date_button_html, format='%Y-%m-%d'))
    state = USStateSelect()
    

    
class RigForm(ModelForm) :
    
    class Meta :
        model = Rig
        
    class Media:
        css = {
                'all': (form_css,)
        }
    
    yr_in_service = forms.DateField(required=False, widget=DynarchDateTimeWidget(date_button_html, format='%Y-%m-%d'))
    phone = USPhoneNumberField(required=False)
    fax = USPhoneNumberField(required=False)


class RunForm(ModelForm) :
    
    class Meta :
        model = Run

    class Media:
        css = {
                'all': (form_css,)
        }

    start_time = forms.DateTimeField(label="Start Time (UTC)", widget = DynarchDateTimeWidget(datetime_button_html))
    end_time = forms.DateTimeField(label = "End Time (UTC)", required=False, widget = DynarchDateTimeWidget(datetime_button_html))

class RunFormForm(forms.Form) :
    
    class Media:
        css = {
                'all': (form_css,)
        }

    name = forms.CharField()
    start_time = forms.DateTimeField(label="Start Time", widget = DynarchDateTimeWidget(datetime_button_html))
    end_time = forms.DateTimeField(label = "End Time", required=False, widget = DynarchDateTimeWidget(datetime_button_html))
    #tool_calibration = forms.ChoiceField(choices = [('','---------')] + [(x.pk,x) for x in ToolCalibration.objects.all().order_by('-time_stamp')])
    tool_calibration = forms.ModelChoiceField(ToolCalibration.objects.all().order_by('-time_stamp'))
    #well_bore = forms.ChoiceField(choices=[('','---------')] + [(x.pk,x) for x in WellBore.objects.all().order_by('well')])
    well_bore = forms.ModelChoiceField(WellBore.objects.all().order_by('well'))

class RunNotesForm(forms.Form) :
    
    class Media:
        css = {
                'all': (form_css,)
        }

    notes = forms.CharField(widget=forms.Textarea)
    

class ToolForm(ModelForm) :
    class Meta :
        model=Tool
    
    class Media:
        css = {
                'all': (form_css,)
        }
    
class ToolNotesForm(forms.Form) :
    
    class Media:
        css = {
                'all': (form_css,)
        }

    notes = forms.CharField(widget=forms.Textarea)    

class SetTimeForm(forms.Form) :
    set_time_to = forms.DateTimeField(widget = DynarchDateTimeWidget(datetime_button_html))
    
    
    
class ToolCalibrationForm(forms.Form) :
    
    class Media:
        css = {
                'all': (form_css,)
        }

    accelerometer_x_offset = forms.DecimalField(required=True, max_value=65535, min_value=0, max_digits=5, decimal_places=0)
    accelerometer_x_gain = forms.DecimalField(required=True, max_value=65535, min_value=0, max_digits=5, decimal_places=0)    
    accelerometer_y_offset = forms.DecimalField(required=True, max_value=65535, min_value=0, max_digits=5, decimal_places=0)
    accelerometer_y_gain = forms.DecimalField(required=True, max_value=65535, min_value=0, max_digits=5, decimal_places=0)
    accelerometer_z_offset = forms.DecimalField(required=True, max_value=65535, min_value=0, max_digits=5, decimal_places=0)
    accelerometer_z_gain = forms.DecimalField(required=True, max_value=65535, min_value=0, max_digits=5, decimal_places=0)    

    magnetometer_x_offset = forms.DecimalField(required=True, max_value=65535, min_value=0, max_digits=5, decimal_places=0)
    magnetometer_x_gain = forms.DecimalField(required=True, max_value=65535, min_value=0, max_digits=5, decimal_places=0)    
    magnetometer_y_offset = forms.DecimalField(required=True, max_value=65535, min_value=0, max_digits=5, decimal_places=0)
    magnetometer_y_gain = forms.DecimalField(required=True, max_value=65535, min_value=0, max_digits=5, decimal_places=0)
    magnetometer_z_offset = forms.DecimalField(required=True, max_value=65535, min_value=0, max_digits=5, decimal_places=0)
    magnetometer_z_gain = forms.DecimalField(required=True, max_value=65535, min_value=0, max_digits=5, decimal_places=0)    
    
    temperature_offset = forms.DecimalField(required=True, max_value=65535, min_value=0, max_digits=5, decimal_places=0)
    temperature_gain = forms.DecimalField(required=True, max_value=65535, min_value=0, max_digits=5, decimal_places=0)


class RoleTestForm(forms.Form) :
    
    class Media:
        css = {
                'all': (form_css,)
        }

    comment = forms.CharField()

    
class ToolGeneralConfigForm(forms.Form) :

    class Media:
        css = {
                'all': (form_css,)
        }

    advanced_squence_pattern = forms.BooleanField(required=False)
    tool_face_zeroing = forms.BooleanField(label="Tool Face Zeroed", required=False)
    rotation_sensing = forms.BooleanField(required=False)
    logging_interval = forms.IntegerField(label='Logging Interval (ms)',max_value=3600000, min_value=0, widget=forms.TextInput(attrs={'size':'6'}))
    gammaray_log_size = forms.IntegerField(label='Gamma Ray Logs / Interval',max_value=60, min_value=1, widget=forms.TextInput(attrs={'size':'4'}))


class ToolMotorConfigForm(forms.Form) :
    class Media:
        css = {
                'all': (form_css,)
        }

    calibration_initial_acceleration = forms.IntegerField(min_value=0, max_value=15, widget=forms.TextInput(attrs={'size':'4'}))

    open_position_offset = forms.IntegerField(widget=forms.TextInput(attrs={'size':'4'}))
    shut_position_offset = forms.IntegerField(widget=forms.TextInput(attrs={'size':'4'}))
    
    open_acceleration_delay = forms.IntegerField(min_value=1, max_value=10, widget=forms.TextInput(attrs={'size':'4'}))
    shut_acceleration_delay = forms.IntegerField(min_value=1, max_value=10, widget=forms.TextInput(attrs={'size':'4'}))
    
    open_max_acceleration = forms.IntegerField(min_value=0, max_value=15, widget=forms.TextInput(attrs={'size':'4'}))    
    shut_max_acceleration = forms.IntegerField(min_value=0, max_value=15, widget=forms.TextInput(attrs={'size':'4'}))

    pulse_time = forms.IntegerField(label='Pulse time (ms)', min_value=0, max_value=2000, widget=forms.TextInput(attrs={'size':'4'}))
    narrow_pulse_time = forms.IntegerField(label='Narrow pulse time (ms)', min_value=0, max_value=5000, widget=forms.TextInput(attrs={'size':'4'}))
    wide_pulse_time = forms.IntegerField(label='Wide pulse time (ms)', min_value=0, max_value=5000, widget=forms.TextInput(attrs={'size':'4'}))

    gear_numerator = forms.IntegerField(min_value=0, max_value=1000, widget=forms.TextInput(attrs={'size':'4'}))
    gear_denominator = forms.IntegerField(min_value=0, max_value=1000, widget=forms.TextInput(attrs={'size':'4'}))


    
class ToolFrameModeBufferForm(forms.Form) :
    class Media:
        css = {
                'all': (form_css,)
        }
        
    TOOL_FRAME_MODE_CHOICES = [('','---------'), ('0','Survey Only'), ('1', 'Instantaneous Only'), ('2','Survey then Instantaneous'), ('3','Instantaneous then Survey'), ]
    
    fmb0 = forms.TypedChoiceField(coerce=int, choices=TOOL_FRAME_MODE_CHOICES, label='Tool Status')
    fmb1 = forms.TypedChoiceField(coerce=int, choices=TOOL_FRAME_MODE_CHOICES, label='Azimuth')
    fmb2 = forms.TypedChoiceField(coerce=int, choices=TOOL_FRAME_MODE_CHOICES, label='Inclination')
    fmb3 = forms.TypedChoiceField(coerce=int, choices=TOOL_FRAME_MODE_CHOICES, label='G')
    fmb4 = forms.TypedChoiceField(coerce=int, choices=TOOL_FRAME_MODE_CHOICES, label='H')
    fmb5 = forms.TypedChoiceField(coerce=int, choices=TOOL_FRAME_MODE_CHOICES, label='Gz')
    fmb6 = forms.TypedChoiceField(coerce=int, choices=TOOL_FRAME_MODE_CHOICES, label='Hz')
    fmb7 = forms.TypedChoiceField(coerce=int, choices=TOOL_FRAME_MODE_CHOICES, label='GxGy')
    fmb8 = forms.TypedChoiceField(coerce=int, choices=TOOL_FRAME_MODE_CHOICES, label='HxHy')
    fmb9 = forms.TypedChoiceField(coerce=int, choices=TOOL_FRAME_MODE_CHOICES, label='Temperature')
    fmb10 = forms.TypedChoiceField(coerce=int, choices=TOOL_FRAME_MODE_CHOICES, label='Pressure')
    fmb11 = forms.TypedChoiceField(coerce=int, choices=TOOL_FRAME_MODE_CHOICES, label='Tool Face')
    fmb12 = forms.TypedChoiceField(coerce=int, choices=TOOL_FRAME_MODE_CHOICES, label='Gamma Ray')
    fmb13 = forms.TypedChoiceField(coerce=int, choices=TOOL_FRAME_MODE_CHOICES, label='Low resolution G')
    fmb14 = forms.TypedChoiceField(coerce=int, choices=TOOL_FRAME_MODE_CHOICES, label='Low resolution H')
    fmb15 = forms.TypedChoiceField(coerce=int, choices=TOOL_FRAME_MODE_CHOICES, label='Low resolution GxGy')
    fmb16 = forms.TypedChoiceField(coerce=int, choices=TOOL_FRAME_MODE_CHOICES, label='Low resolution HxGy')
    fmb17 = forms.TypedChoiceField(coerce=int, choices=TOOL_FRAME_MODE_CHOICES, label='Low resolution Toolface')
    fmb18 = forms.TypedChoiceField(coerce=int, choices=TOOL_FRAME_MODE_CHOICES, label='Low resolution Gamma Ray')
    fmb19 = forms.TypedChoiceField(coerce=int, choices=TOOL_FRAME_MODE_CHOICES, label='Low resolution Toolface and Gamma Ray')
