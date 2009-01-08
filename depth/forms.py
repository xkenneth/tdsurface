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

    license_date = forms.DateField(widget=DynarchDateTimeWidget(date_button_html, format='%Y-%m-%d'))
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


class SetTimeForm(forms.Form) :
    set_time_to = forms.DateTimeField(widget = DynarchDateTimeWidget(datetime_button_html))