from django.db import models
from django.contrib import admin
from django.contrib.localflavor.us.models import USStateField
import uuid

LENGTH_UNIT_CHOICES = (('m','meters'), ('ft','feet'))
TEMP_UNIT_CHOICES = (('F','Fahrenheit'), ('C','Celsius'))

WITS0_NAMES = {1:{
    1:'Well Identifier',
    2:'Sidetrack/Hole Sect No.',
    3:'Record Identifier', 
    4:'Sequence Identifier', 
    5:'Date', 
    6:'Time', 
    7:'Activity Code',
    8:'Depth Bit (meas)',
    9:'Depth Bit (vert)',
    10:'Depth Hole (meas)', 
    11:'Depth Hole (vert)', 
    12:'Block Position', 
    13:'Rate of Penetration (avg)', 
    14:'Hookload (avg)', 
    15:'Hookload (max)', 
    16:'Weight-on-Bit (surf,avg)', 
    17:'Weight-on-Bit (surf,max)', 
    18:'Rotary Torque (surf,avg)', 
    19:'Rotary Torque (surf,max)', 
    20:'Rotary Speed (surf,avg)', 
    21:'Standpipe Pressure (avg)', 
    22:'Casing (Choke) Pressure', 
    23:'Pump Stroke Rate #1', 
    24:'Pump Stroke Rate #2', 
    25:'Pump Stroke Rate #3', 
    26:'Tank Volume (active)', 
    27:'Tank Volume Change (act)', 
    28:'Mud Flow Out %', 
    29:'Mud Flow Out (avg)', 
    30:'Mud Flow In (avg)', 
    31:'Mud Density Out (avg)', 
    32:'Mud Density In (avg)', 
    33:'Mud Temperature Out (avg)', 
    34:'Mud Temperature In (avg)', 
    35:'Mud Conductivity Out (avg)', 
    36:'Mud Conductivity In (avg)', 
    37:'Pump Stroke Count (cum)', 
    38:'Lag Strokes', 
    39:'Depth Returns (meas)', 
    40:'Gas (avg)', 
    41:'< SPARE 1 >', 
    42:'< SPARE 2 >', 
    43:'< SPARE 3 >', 
    44:'< SPARE 4 >', 
    45:'< SPARE 5 >',
    50:'Unknown'
},
    19:
        {
            84:'Vendor 1 Name/Service',
        }
}

class UUIDField(models.CharField) :
    
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = kwargs.get('max_length', 64 )
        kwargs['blank'] = True
        models.CharField.__init__(self, *args, **kwargs)
    
    def pre_save(self, model_instance, add):
        if add :
            value = str(uuid.uuid4())
            setattr(model_instance, self.attname, value)
            return value
        else:
            return super(models.CharField, self).pre_save(model_instance, add)


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
    
    uid = UUIDField(primary_key=True, editable=False)
    name = models.CharField(max_length=255, unique=True)
    owner = models.CharField(max_length=255, blank=True, null=True)
    mfgr = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=255, blank=True, choices = RIG_TYPE_CHOICES)
    yr_in_service = models.DateField(blank=True, null=True)
    rig_class = models.CharField(max_length=255, blank=True, null=True)
    approvals = models.CharField(max_length=255, blank=True, null=True)
    registration = models.CharField(max_length=255, blank=True, null=True)
    contact = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=255, blank=True, null=True)
    fax = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    def __unicode__(self) :
        return self.name

admin.site.register(Rig)


class Well(models.Model) :
    
    uid = UUIDField(primary_key=True, editable=False)    
    name = models.CharField(max_length=255, unique=True)
    legal_name = models.CharField(unique=True, max_length=255, null=True, blank=True)
    government_number = models.CharField(max_length=255, null=True, blank=True)
    api_number = models.CharField(max_length=255, null=True, blank=True)
    license_number = models.CharField(max_length=255, null=True, blank=True)
    license_date = models.DateField(null=True, blank=True)
    field = models.CharField(max_length=255, null=True, blank=True)
    block = models.CharField(max_length=255, null=True, blank=True)
    region = models.CharField(max_length=255, null=True, blank=True)
    district = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    state = USStateField(blank=True, null=True)
    county = models.CharField(max_length=255, null=True, blank=True)    
    timezone = models.CharField(max_length=255, null=True, blank=True)
    operator = models.CharField(max_length=255, null=True, blank=True)
    division = models.CharField(max_length=255, null=True, blank=True)
    interest = models.PositiveIntegerField(blank=True, null=True)
    water_depth = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)
    water_depth_units = models.CharField(max_length=2, choices = LENGTH_UNIT_CHOICES, null=True, blank=True)
    lat = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    lon = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
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
    
    
    uid = UUIDField(primary_key=True, editable=False)
    name = models.CharField(max_length=255, unique=True)
    well = models.ForeignKey(Well)
    parrent_wellbore_uid = models.ForeignKey('self', blank=True, null=True)
    rig = models.ForeignKey(Rig)
    purpose = models.CharField(max_length=255, blank=True)
    api_suffix = models.CharField(max_length=255, blank=True)
    type = models.CharField(max_length=255, blank=True, choices = WELLBORE_TYPE_CHOICES)
    shape = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True, null=True)
    def __unicode__(self) :
        return str(self.well) + ' - ' + self.name

admin.site.register(WellBore)


class ToolType(models.Model) :
    TOOL_INTERFACE_CHOICES = (('S','Serial'),('C','CAN-Bus'))
    type = models.CharField(max_length=32, unique=True)
    interface = models.CharField(max_length=1, choices = TOOL_INTERFACE_CHOICES)
    
    def __unicode__(self) :
        return self.type + self.interface

admin.site.register(ToolType)


class Tool(models.Model) :
    uid = UUIDField(primary_key=True, editable=False)
    serial_number = models.CharField(unique=True, max_length=255)
    type = models.ForeignKey(ToolType)    
    
    def __unicode__(self) :
        return 'Tool-' + self.serial_number

admin.site.register(Tool)


class ToolNotes(models.Model) :
    uid = UUIDField(primary_key=True, editable=False)
    tool = models.ForeignKey(Tool)
    time_stamp = models.DateTimeField(auto_now_add=True, editable=False, db_index=True)
    notes = models.TextField(blank=True, null=True)

admin.site.register(ToolNotes)


class ToolConfig(models.Model) :
    uid = UUIDField(primary_key=True, editable=False)
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
    calco13 = models.PositiveIntegerField()
    calco14 = models.PositiveIntegerField()
    calco15 = models.PositiveIntegerField()
    
    def __unicode__(self) :
        return str(self.tool) + " " + str(self.time_stamp)
        
admin.site.register(ToolConfig)

    
class Run(models.Model) :
    uid = UUIDField(primary_key=True, editable=False)
    name = models.CharField(max_length=255, unique=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(blank=True, null=True)
    tool_config = models.ForeignKey(ToolConfig, blank=True, null=True)
    well_bore = models.ForeignKey(WellBore)        
    
    def __unicode__(self) :
        return str(self.well_bore) + " " + str(self.start_time)
        
admin.site.register(Run)


class RunNotes(models.Model) :
    uid = UUIDField(primary_key=True, editable=False)
    run = models.ForeignKey(Run)
    time_stamp = models.DateTimeField(auto_now_add=True, editable=False, db_index=True)
    notes = models.TextField(blank=True, null=True)

admin.site.register(RunNotes)
    
    
class PipeTally(models.Model) :
    uid = UUIDField(primary_key=True, editable=False)
    run = models.ForeignKey(Run)
    time_stamp = models.DateTimeField(blank=True, null=True)
    duration = models.PositiveIntegerField(blank=True, null=True)
    length = models.DecimalField(max_digits=10, decimal_places=3)
    length_units = models.CharField(max_length=2, choices = LENGTH_UNIT_CHOICES)

admin.site.register(PipeTally)


class ToolMWDRealTime(models.Model) :
    VALUE_TYPE_CHOICES = (('G','Gravity'),('M','Magnetic'),('T','Temperature'),('R','Gamma Ray'),('A','Azimuth'),('I','Inclination'),)
    uid = UUIDField(primary_key=True, editable=False)
    run = models.ForeignKey(Run)    
    time_stamp = models.DateTimeField( db_index=True)
    type = models.CharField(max_length=1, choices = VALUE_TYPE_CHOICES, db_index=True)
    value = models.IntegerField(blank=True, null=True)
    value_x = models.IntegerField(blank=True, null=True)
    value_y = models.IntegerField(blank=True, null=True)
    value_z = models.IntegerField(blank=True, null=True)
    
admin.site.register(ToolMWDRealTime)
    
    
class ToolMWDLog(models.Model) :
    uid = UUIDField(primary_key=True, editable=False)    
    run = models.ForeignKey(Run)
    seconds = models.IntegerField()
    raw_data = models.CharField(max_length=255, blank=True, null=True)
    status = models.IntegerField()
    gravity_x = models.IntegerField()
    gravity_y = models.IntegerField()
    gravity_z = models.IntegerField()
    magnetic_x = models.IntegerField()
    magnetic_y = models.IntegerField()
    magnetic_z = models.IntegerField()
    temperature = models.IntegerField()
    gamma0 = models.IntegerField()
    gamma1 = models.IntegerField()
    gamma2 = models.IntegerField()
    gamma3 = models.IntegerField()

admin.site.register(ToolMWDLog)


class ManualDepth(models.Model) :
    uid = UUIDField(primary_key=True, editable=False)
    run = models.ForeignKey(Run)
    time_stamp = models.DateTimeField(db_index=True)
    depth = models.DecimalField(max_digits=10, decimal_places=3)
    depth_units = models.CharField(max_length=2, choices = LENGTH_UNIT_CHOICES)

    def __unicode__(self) :
        return str(self.time_stamp) + " " + str(self.depth)

admin.site.register(ManualDepth)


class BlockPosition(models.Model) :
    uid = UUIDField(primary_key=True, editable=False)
    run = models.ForeignKey(Run)
    time_stamp = models.DateTimeField(db_index=True)
    position = models.DecimalField(max_digits=10, decimal_places=3)
    position_units = models.CharField(max_length=2, choices = LENGTH_UNIT_CHOICES)

admin.site.register(BlockPosition)


class Slip(models.Model) :
    SLIP_STATUS_CHOICES = ((0,'Out'),(1,'In'))
    uid = UUIDField(primary_key=True, editable=False)
    run = models.ForeignKey(Run)
    time_stamp = models.DateTimeField(db_index=True)
    status = models.DecimalField(max_digits=1, decimal_places=0, choices = SLIP_STATUS_CHOICES)

admin.site.register(Slip)


class RigStatus(models.Model) :
    uid = UUIDField(primary_key=True, editable=False)
    time_stamp = models.DateTimeField(db_index=True)
    status = models.CharField(max_length=255)
    
    class Meta:        
        verbose_name_plural = "Rig status"
        
admin.site.register(RigStatus)


class Settings(models.Model) :    
    name = models.CharField(primary_key=True, max_length=32)
    value = models.CharField(max_length=255, blank=True)

    class Meta:        
        verbose_name_plural = "Settings"

    def get_active_run(self) :        
        active_run, created = Settings.objects.get_or_create(name='ACTIVE_RUN')
        return Run.objects.get(pk=active_run.value)

admin.site.register(Settings)


class WITSGeneralTimeBased(models.Model) :
    uid = UUIDField(primary_key=True, editable=False)
    run = models.ForeignKey(Run)
    time_stamp = models.DateTimeField(db_index=True)
    recid = models.IntegerField(blank=True, null=True)
    seqid = models.IntegerField(blank=True, null=True)
    actcod = models.IntegerField(blank=True, null=True)
    deptbitm = models.FloatField(blank=True, null=True)
    deptbitv = models.FloatField(blank=True, null=True)
    deptmeas = models.FloatField(blank=True, null=True)
    deptvert = models.FloatField(blank=True, null=True)
    blkpos = models.FloatField(blank=True, null=True)
    ropa = models.FloatField(blank=True, null=True)
    hkla = models.FloatField(blank=True, null=True)
    hklx = models.FloatField(blank=True, null=True)
    woba = models.FloatField(blank=True, null=True)
    wobx = models.FloatField(blank=True, null=True)
    torqa = models.FloatField(blank=True, null=True)
    torqx = models.FloatField(blank=True, null=True)
    rpma = models.IntegerField(blank=True, null=True)
    sppa = models.FloatField(blank=True, null=True)  
    chkp = models.FloatField(blank=True, null=True)
    spm1 = models.IntegerField(blank=True, null=True)
    spm2 = models.IntegerField(blank=True, null=True)
    spm3 = models.IntegerField(blank=True, null=True)
    tvolact = models.FloatField(blank=True, null=True)
    tvolcact = models.FloatField(blank=True, null=True)
    mfop = models.IntegerField(blank=True, null=True)
    mfoa = models.FloatField(blank=True, null=True)
    mfia = models.FloatField(blank=True, null=True)
    mdao = models.FloatField(blank=True, null=True)
    mdia = models.FloatField(blank=True, null=True)
    mtoa = models.FloatField(blank=True, null=True)
    mtia = models.FloatField(blank=True, null=True)
    mcoa = models.FloatField(blank=True, null=True)
    mcia = models.FloatField(blank=True, null=True)
    stkc = models.IntegerField(blank=True, null=True)
    lagstks = models.IntegerField(blank=True, null=True)
    deptretm = models.FloatField(blank=True, null=True)
    gasa = models.FloatField(blank=True, null=True)
    spare1 = models.FloatField(blank=True, null=True)
    spare2 = models.FloatField(blank=True, null=True)
    spare3 = models.FloatField(blank=True, null=True)
    spare4 = models.FloatField(blank=True, null=True)
    spare5 = models.FloatField(blank=True, null=True)
    
admin.site.register(WITSGeneralTimeBased)


class WITS0(models.Model) :
    uid = UUIDField(primary_key=True, editable=False)
    run = models.ForeignKey(Run)
    time_stamp = models.DateTimeField(db_index=True)
    recid = models.IntegerField(db_index=True)
    itemid = models.IntegerField(db_index=True)
    value = models.CharField(max_length=255, blank=True, null=True)
    
    def description(self) :
        try :
            desc = WITS0_NAMES[self.recid][self.itemid]
        except :
            return None
        return desc
    
admin.site.register(WITS0) 