from django import forms
from django.db import models
from django.forms import ModelForm
from tdsurface.depth.models import *

class DatePickerWidget(forms.DateTimeInput):
    class Media:
        css = {
            'all': ('/tdusurface/media/datepicker/css/datepicker.css', )
        }
        js = ('/tdsurface/media/datepicker/js/datepicker.js', )


class WellForm(ModelForm) :
    def __init__(self, *args, **kwargs):
        super(WellForm, self).__init__(*args, **kwargs)
        #self.fields['license_date'].widget = DatePickerWidget()
    
    class Meta :
        model = Well

    class Media:
        css = {
                'all': ('/tdsurface/media/css/forms.css',)
        }
