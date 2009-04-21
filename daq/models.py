from django.db import models
from django.contrib import admin
from tdsurface.models import UUIDField

from tdsurface.depth.models import Well

# Create your models here.
class ChannelLog(models.Model) :
    uid = UUIDField(primary_key=True, editable=False)
    well = models.ForeignKey(Well)
    time_stamp = models.DateTimeField(db_index=True)    
    standpipe = models.FloatField(null=True, blank=True)
    hookload = models.FloatField(null=True, blank=True)
    above_collar = models.FloatField(null=True, blank=True)
    below_collar = models.FloatField(null=True, blank=True)
    regular_flow = models.FloatField(null=True, blank=True)
    venturi_flow = models.FloatField(null=True, blank=True)
    us_flow = models.FloatField(null=True, blank=True)
    depth = models.FloatField(null=True, blank=True)
    

admin.site.register(ChannelLog)
