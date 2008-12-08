from django.db import models
from django.contrib import admin


LENGTH_UNIT_CHOICES = (('m','meters'), ('ft','feet'))
TEMP_UNIT_CHOICES = (('F','Fahrenheit'), ('C','Celsius'))

class Country(models.Model) :
    country = models.CharField(max_length=255, primary_key=True)
    
    def __unicode__(self) :
        return self.country

admin.site.register(Country)
    
  
class State(models.Model) :
    state = models.CharField(max_length=255, primary_key=True)
    country = models.ForeignKey(Country)
    
    def __unicode__(self) :
        return self.state

admin.site.register(State)    
    
class Rig(models.Model) :
    RIG_TYPE_CHOICES = (
        ('barge', 'Barge rig'),
        ('coiled tubing', 'Coiled tubing rig'),
        ('floater', 'Floating rig'),
        ('jackup', 'Jackup rig'),
        ('land', 'Land rig'),
        ('platform', 'Fixed Platform'),
        ('simi-submersible', 'Semisubmersible rig'),
        ('unknown', 'unknown'),
        )
    
    uid = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    owner = models.CharField(max_length=255, blank=True)
    mfgr = models.CharField(max_length=255, blank=True)
    type = models.CharField(max_length=255, blank=True, choices = RIG_TYPE_CHOICES)
    yr_in_service = models.PositiveIntegerField(blank=True)
    rig_class = models.CharField(max_length=255, blank=True)
    approvals = models.CharField(max_length=255, blank=True)
    registration = models.CharField(max_length=255, blank=True)
    contact = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=255, blank=True)
    fax = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    
    def __unicode__(self) :
        return self.name

admin.site.register(Rig)


class Well(models.Model) :
    
    uid = models.CharField(max_length=255, primary_key=True)    
    name = models.CharField(max_length=255, unique=True)
    legal_name = models.CharField(unique=True, max_length=255, blank=True)
    government_number = models.CharField(max_length=255)
    api_number = models.CharField(max_length=255, blank=True)
    license_number = models.CharField(max_length=255, blank=True)
    license_date = models.DateField()
    field = models.CharField(max_length=255, blank=True)
    block = models.CharField(max_length=255, blank=True)
    region = models.CharField(max_length=255, blank=True)
    district = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=255, blank=True)
    state = models.CharField(max_length=255, blank=True)
    county = models.CharField(max_length=255, blank=True)    
    timezone = models.CharField(max_length=255)
    operator = models.CharField(max_length=255, blank=True)
    division = models.CharField(max_length=255, blank=True)
    interest = models.PositiveIntegerField(blank=True)
    water_depth = models.DecimalField(max_digits=7, decimal_places=2, blank=True)
    water_depth_units = models.CharField(max_length=2, choices = LENGTH_UNIT_CHOICES, blank=True)
    lat = models.DecimalField(max_digits=9, decimal_places=6)
    lon = models.DecimalField(max_digits=9, decimal_places=6)

    def __unicode__(self) :
        return self.name

admin.site.register(Well)


class WellBore(models.Model) :
    WELLBORE_TYPE_CHOICES = (
        ('bypass','bypass'),
        ('initial','initial'),
        ('redrill','redrill'),
        ('reentry','reentry'),
        ('respud','respud'),
        ('sidetrack', 'sidestrack'),
        ('unknown', 'unknown'),
        )
    
    
    uid = models.CharField(primary_key=True, max_length=255)
    name = models.CharField(max_length=255, unique=True)
    well = models.ForeignKey(Well)
    parrent_wellbore_uid = models.CharField(max_length=255, blank=True)
    rig = models.ForeignKey(Rig)
    purpose = models.CharField(max_length=255, blank=True)
    api_suffix = models.CharField(max_length=255, blank=True)
    type = models.CharField(max_length=255, blank=True, choices = WELLBORE_TYPE_CHOICES)
    shape = models.CharField(max_length=255, blank=True)
    
    def __unicode__(self) :
        return self.name

admin.site.register(WellBore)


class ToolType(models.Model) :
    TOOL_INTERFACE_CHOICES = (('S','Serial'),('C','CAN-Bus'))
    type = models.CharField(max_length=32, unique=True)
    interface = models.CharField(max_length=1, choices = TOOL_INTERFACE_CHOICES)
    
    def __unicode__(self) :
        return self.serial_number

admin.site.register(ToolType)


class Tool(models.Model) :
    serial_number = models.CharField(primary_key=True, max_length=255)
    type = models.ForeignKey(ToolType)

    def __unicode__(self) :
        return self.serial_number

admin.site.register(Tool)


class ToolConfig(models.Model) :
    uid = models.CharField(primary_key=True, max_length=255)
    time_stamp = models.DateTimeField()
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
        return str(self.tool) + " " + str(self.start_time)
        
admin.site.register(ToolConfig)

    
class Run(models.Model) :
    uid = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    tool_config = models.ForeignKey(ToolConfig)
    well_bore = models.ForeignKey(WellBore)        
        
    def __unicode__(self) :
        return str(self.well_bore) + " " + str(self.start_time)
        
admin.site.register(Run)

    
class PipeTally(models.Model) :
    tally_id = models.CharField(max_length=64, primary_key=True)
    run = models.ForeignKey(Run)
    time_stamp = models.DateTimeField(blank=True)
    duration = models.PositiveIntegerField(blank=True)
    length = models.DecimalField(max_digits=10, decimal_places=3)
    length_units = models.CharField(max_length=2, choices = LENGTH_UNIT_CHOICES)

admin.site.register(PipeTally)

    
class MWDRealTime(models.Model) :
    uid = models.CharField(max_length=255, primary_key=True)
    run = models.ForeignKey(Run)
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
    uid = models.CharField(max_length=255, primary_key=True)
    run = models.ForeignKey(Run)
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
    uid = models.CharField(max_length=255, primary_key=True)
    run = models.ForeignKey(Run)
    time_stamp = models.DateTimeField()
    depth = models.DecimalField(max_digits=10, decimal_places=3)
    depth_units = models.CharField(max_length=2, choices = LENGTH_UNIT_CHOICES)

    def __unicode__(self) :
        return str(self.time_stamp) + " " + str(self.depth)

admin.site.register(ManualDepth)


class BlockPosition(models.Model) :
    uid = models.CharField(max_length=255, primary_key=True)
    run = models.ForeignKey(Run)
    time_stamp = models.DateTimeField()
    position = models.DecimalField(max_digits=10, decimal_places=3)
    position_units = models.CharField(max_length=2, choices = LENGTH_UNIT_CHOICES)

admin.site.register(BlockPosition)


class Slip(models.Model) :
    SLIP_STATUS_CHOICES = ((0,'Out'),(1,'In'))
    uid = models.CharField(max_length=255, primary_key=True)
    run = models.ForeignKey(Run)
    time_stamp = models.DateTimeField()
    status = models.DecimalField(max_digits=1, decimal_places=0, choices = SLIP_STATUS_CHOICES)

admin.site.register(Slip)


class RigStatus(models.Model) :
    uid = models.CharField(max_length=255, primary_key=True)
    time_stamp = models.DateTimeField()
    status = models.CharField(max_length=255)
    
admin.site.register(RigStatus)
