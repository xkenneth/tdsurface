from django.db import models
from django.forms import ModelForm
from tdsurface.depth.models import *

class WellForm(ModelForm) :
    class Meta :
        model = Well