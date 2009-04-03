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
    

    
