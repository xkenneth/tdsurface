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

    value = forms.DecimalField(widget=forms.TextInput(attrs={'size':'6'}) )

class PumpForm(ModelForm) :
    
    class Meta :
        model = Pump

    class Media:
        css = {
                'all': (form_css,)
        }
    
    liner_size = forms.DecimalField(widget=forms.TextInput(attrs={'size':'6'}) )
    stroke_length = forms.DecimalField(widget=forms.TextInput(attrs={'size':'6'}) )
    stroke_volume = forms.DecimalField(widget=forms.TextInput(attrs={'size':'6'}) )
    spp_max = forms.DecimalField(widget=forms.TextInput(attrs={'size':'6'}) )
    efficiency = forms.DecimalField(widget=forms.TextInput(attrs={'size':'6'}) )
