from django.db import models
from django.contrib import admin


LENGTH_UNIT_CHOICES = (('m','meters'), ('ft','feet'))
TEMP_UNIT_CHOICES = (('F','Fahrenheit'), ('C','Celsius'))

    
class Rig(models.Model) :
    rig_id = models.CharField(max_length=64, primary_key=True)
    name = models.CharField(max_length=255)
    owner = models.CharField(max_length=255, blank=True)
    type = models.CharField(max_length=255, blank=True)
    
    def __unicode__(self) :
        return self.name

admin.site.register(Rig)


class Well(models.Model) :
    
    COUNTRY_CHOICES = (
        ('USA', 'United States of America'),
        ('MEX', 'Mexico'),
        ('CAN', 'Canada')
    )
    name_legal = models.CharField('Legal Name', primary_key=True, max_length=255, blank=True)
    name = models.CharField(max_length=255)
    num_govt = models.CharField('Government Number', max_length=255)
    field = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=3, choices = COUNTRY_CHOICES)
    state = models.CharField(max_length=255, blank=True)
    county = models.CharField(max_length=255, blank=True)
    block = models.CharField(max_length=255, blank=True)
    timezone = models.CharField(max_length=255)
    operator = models.CharField(max_length=255, blank=True)
    water_depth = models.DecimalField(max_digits=7, decimal_places=2, blank=True)
    water_depth_units = models.CharField(max_length=2, choices = LENGTH_UNIT_CHOICES, blank=True)
    lat = models.DecimalField(max_digits=9, decimal_places=6)
    lon = models.DecimalField(max_digits=9, decimal_places=6)
    

    def __unicode__(self) :
        return self.name

admin.site.register(Well)


class WellBore(models.Model) :
    wellbore_id = models.CharField(primary_key=True, max_length=255)
    name = models.CharField(max_length=255)
    well = models.ForeignKey(Well)
    
    def __unicode__(self) :
        return self.name

admin.site.register(WellBore)


class Tool(models.Model) :
    TOOL_TYPE_CHOICES = (('MWD1','MWD1'),)
    serial_number = models.CharField(primary_key=True, max_length=255)
    type = models.CharField(max_length=4, choices = TOOL_TYPE_CHOICES )

    def __unicode__(self) :
        return self.serial_number

admin.site.register(Tool)

    
class Trip(models.Model) :
    trip_id = models.CharField(max_length=64, primary_key=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    well_bore = models.ForeignKey(WellBore)
    rig = models.ForeignKey(Rig)
    tool = models.ForeignKey(Tool)
    calco0 = models.PositiveIntegerField()
    calco1 = models.PositiveIntegerField()
    calco2 = models.PositiveIntegerField()
    calco3 = models.PositiveIntegerField()
    calco4 = models.PositiveIntegerField()
    calco5 = models.PositiveIntegerField()
    calco6 = models.PositiveIntegerField()
    calco7 = models.PositiveIntegerField()
    calco8 = models.PositiveIntegerField()
    calco9 = models.PositiveIntegerField()
    calco10 = models.PositiveIntegerField()
    calco11 = models.PositiveIntegerField()
    calco12 = models.PositiveIntegerField()
        
    def __unicode__(self) :
        return str(self.well_bore) + " " + str(self.start_time)
        
admin.site.register(Trip)

    
class PipeTally(models.Model) :
    tally_id = models.CharField(max_length=64, primary_key=True)
    trip = models.ForeignKey(Trip)
    time_stamp = models.DateTimeField()
    length = models.DecimalField(max_digits=10, decimal_places=3)
    length_units = models.CharField(max_length=2, choices = LENGTH_UNIT_CHOICES)

admin.site.register(PipeTally)

    
class MWDRealTime(models.Model) :
    rt_id = models.CharField(max_length=64, primary_key=True)
    trip = models.ForeignKey(Trip)
    time_stamp = models.DateTimeField()
    raw_data = models.CharField(max_length=255)
    gravity_x = models.IntegerField(blank=True)
    gravity_y = models.IntegerField(blank=True)
    gravity_z = models.IntegerField(blank=True)
    magnetic_x = models.IntegerField(blank=True)
    magnetic_y = models.IntegerField(blank=True)
    magnetic_z = models.IntegerField(blank=True)
    temperature = models.IntegerField(blank=True)
    temperature_units = models.CharField(max_length=1, choices = TEMP_UNIT_CHOICES, blank=True)
    gama0 = models.IntegerField(blank=True)
    gama1 = models.IntegerField(blank=True)
    gama2 = models.IntegerField(blank=True)
    gama3 = models.IntegerField(blank=True)

admin.site.register(MWDRealTime)
    
    
class MWDLog(models.Model) :
    log_id = models.CharField(max_length=64, primary_key=True)
    trip = models.ForeignKey(Trip)
    time_stamp = models.DateTimeField()
    raw_data = models.CharField(max_length=255)
    gravity_x = models.IntegerField()
    gravity_y = models.IntegerField()
    gravity_z = models.IntegerField()
    magnetic_x = models.IntegerField()
    magnetic_y = models.IntegerField()
    magnetic_z = models.IntegerField()
    temperature = models.IntegerField()
    temperature_units = models.CharField(max_length=1, choices = TEMP_UNIT_CHOICES)
    gama0 = models.IntegerField()
    gama1 = models.IntegerField()
    gama2 = models.IntegerField()
    gama3 = models.IntegerField()

admin.site.register(MWDLog)


class ManualDepth(models.Model) :
    md_id = models.CharField(max_length=64, primary_key=True)
    trip = models.ForeignKey(Trip)
    time_stamp = models.DateTimeField()
    depth = models.DecimalField(max_digits=10, decimal_places=3)
    depth_units = models.CharField(max_length=2, choices = LENGTH_UNIT_CHOICES)

    def __unicode__(self) :
        return str(self.time_stamp) + " " + str(self.depth)

admin.site.register(ManualDepth)


class BlockPosition(models.Model) :
    bp_id = models.CharField(max_length=64, primary_key=True)
    trip = models.ForeignKey(Trip)
    time_stamp = models.DateTimeField()
    position = models.DecimalField(max_digits=10, decimal_places=3)
    position_units = models.CharField(max_length=2, choices = LENGTH_UNIT_CHOICES)

admin.site.register(BlockPosition)


class Slip(models.Model) :
    SLIP_STATUS_CHOICES = ((0,'Out'),(1,'In'))
    slip_id = models.CharField(max_length=64, primary_key=True)
    trip = models.ForeignKey(Trip)
    time_stamp = models.DateTimeField()
    status = models.DecimalField(max_digits=1, decimal_places=0, choices = SLIP_STATUS_CHOICES)

admin.site.register(Slip)

