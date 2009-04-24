from django.db import models
from django.contrib import admin
from tdsurface.models import UUIDField

from tdsurface.depth.models import Run

class BHA(models.Model) :
    uid = UUIDField(primary_key=True, editable=False)
    run = models.OneToOneField(Run, editable=False)
    gammaray_sensor_offset = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    accelerometer_offset = models.DecimalField(max_digits=10, decimal_places=3, default=0)

class Pump(models.Model) :
    uid = UUIDField(primary_key=True, editable=False)
    bha = models.ForeignKey(BHA, editable=False)
    number = models.PositiveIntegerField(editable=False)
    liner_size = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    stroke_length = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    stroke_volume = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    spp_max = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    efficiency = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)

class Component(models.Model) :
    uid = UUIDField(primary_key=True, editable=False)
    bha = models.ForeignKey(BHA)
    order = models.PositiveIntegerField()
    description = models.CharField(max_length=255, blank=True, null=True)
    serial_number = models.CharField(max_length=255, blank=True, null=True)
    odia = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True, default=0)
    idia = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True, default=0)
    fn_length = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True, default=0)
    top_conn = models.CharField(max_length=255, blank=True, null=True)
    pb = models.CharField(max_length=255, blank=True, null=True)
    length = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True, default=0)

class Bit(models.Model) :

    BIT_TYPE_CHOICES = (
        ('tri-cone','tri-cone'),
        ('PDC','PDC'),        
        ('unknown', 'unknown'),
        )
    
    uid = UUIDField(primary_key=True, editable=False)
    bha = models.OneToOneField(BHA, editable=False)
    bit_number = models.PositiveIntegerField(blank=True, null=True)
    run_number = models.PositiveIntegerField(blank=True, null=True)
    serial_number = models.CharField(max_length=255, blank=True, null=True)
    manufacturer = models.CharField(max_length=255, blank=True, null=True)
    size = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    type = models.CharField(max_length=255, choices=BIT_TYPE_CHOICES, blank=True, null=True)
    blade_cnt = models.PositiveIntegerField(blank=True, null=True)
    cutter_size = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    gauge_length = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    tfa = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    dull_ir = models.PositiveIntegerField(blank=True, null=True)
    dull_or = models.PositiveIntegerField(blank=True, null=True)
    dull_dc = models.CharField(max_length=8, blank=True, null=True)
    dull_loc = models.CharField(max_length=8, blank=True, null=True)
    dull_bs = models.PositiveIntegerField(blank=True, null=True)
    dull_g16 = models.PositiveIntegerField(blank=True, null=True)
    dull_oc = models.CharField(max_length=8, blank=True, null=True)
    dull_r_pld = models.CharField(max_length=8, blank=True, null=True)

class Jet(models.Model) :
    uid = UUIDField(primary_key=True, editable=False)
    bit = models.ForeignKey(Bit, editable=False)
    value = models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=3)



    
