from django import forms
from django.db import models
from django.forms import ModelForm
from tdsurface.bha.models import *

from tdsurface.widgets import *

form_css = '/tdsurface/media/css/forms.css'

class BHAForm(ModelForm) :
    
    class Meta :
        model = BHA

    class Media:
        css = {
                'all': (form_css,)
        }
    
class BitForm(ModelForm) :
    
    class Meta :
        model = Bit

    class Media:
        css = {
                'all': (form_css,)
        }


class JetForm(ModelForm) :
    
    class Meta :
        model = Jet

    class Media:
        css = {
                'all': (form_css,)
        }

    value = forms.DecimalField(required=False, widget=forms.TextInput(attrs={'size':'6'}) )

class PumpForm(ModelForm) :
    
    class Meta :
        model = Pump

    class Media:
        css = {
                'all': (form_css,)
        }
    
    liner_size = forms.DecimalField(required=False, widget=forms.TextInput(attrs={'size':'6'}) )
    stroke_length = forms.DecimalField(required=False, widget=forms.TextInput(attrs={'size':'6'}) )
    stroke_volume = forms.DecimalField(required=False, widget=forms.TextInput(attrs={'size':'6'}) )
    spp_max = forms.DecimalField(required=False, widget=forms.TextInput(attrs={'size':'6'}) )
    efficiency = forms.DecimalField(required=False, widget=forms.TextInput(attrs={'size':'6'}) )

class CollarForm(forms.Form) :

    class Media:
        css = {
                'all': (form_css,)
        }

    top_xover = forms.CharField(required=False)
    drill_collar = forms.CharField(required=False)
    collar_double_pin = forms.CharField(required=False)
    bottom_xover = forms.CharField(required=False)
    flow_guide = forms.CharField(required=False)
    mud_screen = forms.CharField(required=False)

class ProbeForm(forms.Form) :

    class Media:
        css = {
                'all': (form_css,)
        }

    pulser = forms.CharField(required=False)
    turbine = forms.CharField(required=False)
    probe_double_pin = forms.CharField(required=False)
    battery = forms.CharField(required=False)
    stinger = forms.CharField(required=False)
    electronics_barrel = forms.CharField(required=False)
    battery_barrel = forms.CharField(required=False)

class SurfaceGearForm(forms.Form) :

    class Media:
        css = {
                'all': (form_css,)
        }

    data_acquisition = forms.CharField(required=False)
    computer_1 = forms.CharField(required=False)
    computer_2 = forms.CharField(required=False)
    ups = forms.CharField(required=False)
    rig_phone = forms.CharField(required=False)
    rig_internet = forms.CharField(required=False)
    stand_pipe_pressure_sensor = forms.CharField(required=False)
    flow_meter = forms.CharField(required=False)
    hook_load_sensor = forms.CharField(required=False)
    depth_sensor = forms.CharField(required=False)
    
