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

    start_time = forms.DateTimeField(widget = DynarchDateTimeWidget(datetime_button_html))
    end_time = forms.DateTimeField(required=False, widget = DynarchDateTimeWidget(datetime_button_html))

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