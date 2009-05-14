from pytz import common_timezones
from django.db import models
from django.contrib import admin
from django.contrib.localflavor.us.models import USStateField
from tdsurface.models import UUIDField



from math import sqrt
from math import acos
from math import atan
from math import atan2
from math import pi

LENGTH_UNIT_CHOICES = (('m','meters'), ('ft','feet'))
WEIGHT_UNIT_CHOICES = (('lbs','pounds'), ('klbs','Kilo Pounds'), ('t', 'tons') )
TEMP_UNIT_CHOICES = (('F','Fahrenheit'), ('C','Celsius'))
TIMEZONE_CHOICES =  [(x,x) for x in common_timezones if x.startswith( 'US/' )]

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
    timezone = models.CharField(max_length=255, null=True, blank=False, choices = TIMEZONE_CHOICES)
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

    unique_together = (("name", "well"),)
    
    uid = UUIDField(primary_key=True, editable=False)
    name = models.CharField(max_length=255, unique=False)
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
    invert_magnetic_x = models.BooleanField(default=0)
    invert_magnetic_y = models.BooleanField(default=0)
    invert_magnetic_z = models.BooleanField(default=0)
    invert_gravity_x = models.BooleanField(default=0)
    invert_gravity_y = models.BooleanField(default=0)
    invert_gravity_z = models.BooleanField(default=0)
    
    def __unicode__(self) :
        return self.type

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


class ToolCalibration(models.Model) :
    uid = UUIDField(primary_key=True, editable=False)
    time_stamp = models.DateTimeField()
    tool = models.ForeignKey(Tool)
    
    calibration_id = models.PositiveIntegerField()
    tool_serial_number = models.PositiveIntegerField()
    
    accelerometer_x_offset = models.PositiveIntegerField()
    accelerometer_x_gain = models.PositiveIntegerField()
    accelerometer_y_offset = models.PositiveIntegerField()
    accelerometer_y_gain = models.PositiveIntegerField()
    accelerometer_z_offset = models.PositiveIntegerField()
    accelerometer_z_gain = models.PositiveIntegerField()
    
    magnetometer_x_offset = models.PositiveIntegerField()
    magnetometer_x_gain = models.PositiveIntegerField()
    magnetometer_y_offset = models.PositiveIntegerField()
    magnetometer_y_gain = models.PositiveIntegerField()
    magnetometer_z_offset = models.PositiveIntegerField()
    magnetometer_z_gain = models.PositiveIntegerField()
    
    temperature_offset = models.PositiveIntegerField()
    temperature_gain = models.PositiveIntegerField()
        
    def __unicode__(self) :
        return str(self.tool) + " " + str(self.time_stamp)
        
admin.site.register(ToolCalibration)

    
class Run(models.Model) :

    unique_together = (("name", "well_bore"),)
    
    uid = UUIDField(primary_key=True, editable=False)
    name = models.CharField(max_length=255, unique=False)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(blank=True, null=True)
    tool = models.ForeignKey(Tool, blank=True, null=True)
    tool_calibration = models.ForeignKey(ToolCalibration, blank=True, null=True, editable=False)
    well_bore = models.ForeignKey(WellBore)        
    
    def __unicode__(self) :
        return str(self.well_bore) + ' - ' + str(self.name)
        
admin.site.register(Run)


class RunNotes(models.Model) :
    uid = UUIDField(primary_key=True, editable=False)
    run = models.ForeignKey(Run)
    time_stamp = models.DateTimeField(auto_now_add=True, editable=False, db_index=True)
    notes = models.TextField(blank=True, null=True)

admin.site.register(RunNotes)


class RollTest(models.Model) :
    uid = UUIDField(primary_key=True, editable=False)
    run = models.ForeignKey(Run)
    time_stamp = models.DateTimeField(auto_now_add=True, editable=False, db_index=True)    
    comment = models.CharField(max_length=255, blank=True, null=True)
    azimuth = models.DecimalField(max_digits=10, decimal_places=1)
    inclination = models.DecimalField(max_digits=10, decimal_places=1)
    toolface = models.DecimalField(max_digits=10, decimal_places=1)
    temperature = models.DecimalField(max_digits=10, decimal_places=1)
    azimuth = models.DecimalField(max_digits=10, decimal_places=1)
    gravity = models.DecimalField(max_digits=10, decimal_places=1)
    magnetic = models.DecimalField(max_digits=10, decimal_places=1)
    gamma = models.DecimalField(max_digits=10, decimal_places=1)

    def __unicode__(self) :
        return str(self.run) + ' - ' + str(self.comment) + " " + str(self.time_stamp)
    
admin.site.register(RollTest)
    
    
class PipeTally(models.Model) :
    uid = UUIDField(primary_key=True, editable=False)
    run = models.ForeignKey(Run)
    order = models.PositiveIntegerField()
    duration = models.PositiveIntegerField(blank=True, null=True)
    pipe_length = models.DecimalField(max_digits=10, decimal_places=3, blank=False, null=False, default=0)
    length_units = models.CharField(max_length=2, choices = LENGTH_UNIT_CHOICES)
    note = models.TextField(blank=True, null=True)

admin.site.register(PipeTally)


class ToolMWDRealTime(models.Model) :
    VALUE_TYPE_CHOICES = (('g','Gravity'),('H','Magnetic'),('temperature','Temperature'),('gammaray','Gamma Ray'),('azimuth','Azimuth'),('inclination','Inclination'),('toolface','Tool Face'),('status', 'Status'))
    uid = UUIDField(primary_key=True, editable=False)
    well = models.ForeignKey(Well)    
    time_stamp = models.DateTimeField( db_index=True)
    type = models.CharField(max_length=32, choices = VALUE_TYPE_CHOICES, db_index=True)
    value = models.IntegerField(blank=True, null=True)
    value_x = models.IntegerField(blank=True, null=True)
    value_y = models.IntegerField(blank=True, null=True)
    value_z = models.IntegerField(blank=True, null=True)
    depth = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True, db_index=True)
    depth_units = models.CharField(max_length=2, null=True, blank=True, choices = LENGTH_UNIT_CHOICES)
    
admin.site.register(ToolMWDRealTime)

class ToolMWDLogGamma(models.Model) :
    uid = UUIDField(primary_key=True, editable=False)    
    run = models.ForeignKey(Run)
    seconds = models.IntegerField(db_index=True)
    status = models.IntegerField()
    gamma = models.IntegerField()
    depth = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True, db_index=True)
    depth_units = models.CharField(max_length=2, null=True, blank=True, choices = LENGTH_UNIT_CHOICES)

    def gamma_cps(self) :
        return round((pow(10, self.gamma*2/10000.0 ) * 2),1)

    
class ToolMWDLog(models.Model) :
    uid = UUIDField(primary_key=True, editable=False)    
    run = models.ForeignKey(Run)
    seconds = models.IntegerField(db_index=True)
    raw_data = models.CharField(max_length=255, blank=True, null=True)
    status = models.IntegerField()
    gravity_x = models.IntegerField()
    gravity_y = models.IntegerField()
    gravity_z = models.IntegerField()
    magnetic_x = models.IntegerField()
    magnetic_y = models.IntegerField()
    magnetic_z = models.IntegerField()
    temperature = models.IntegerField()    
    depth = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True, db_index=True)
    depth_units = models.CharField(max_length=2, null=True, blank=True, choices = LENGTH_UNIT_CHOICES)

    def _calibrate(self, value, offset, gain, flip=False) :
        c = round( (value - offset)/(1.0 * gain),3)
        if flip :
            c = c * -1
        return c

    def temperature_f(self) :
        """Already calibrated, but needs to be detransfered"""
        return round(self.temperature*500/10000.0, 1)

    def temperature_c(self) :
        """Already calibrated, but needs to be detransfered"""
        return round(((self.temperature*500/10000.0) - 32 ) * 5 / 9, 1)
    
    def gravity_x_calibrated(self, run=None) :
        """When looping of a list of ToolMWDLog it is best to pass a run in
        otherwize the ORM queries the constants and flips every time through the loop.
        """
        if not run :
            run = self.run
        
        flip = run.tool_calibration.tool.type.invert_gravity_x        
        return self._calibrate(self.gravity_x, run.tool_calibration.accelerometer_x_offset, run.tool_calibration.accelerometer_x_gain, flip)

    def gravity_y_calibrated(self, run=None) :
        if not run :
            run = self.run
        flip = run.tool_calibration.tool.type.invert_gravity_y
        return self._calibrate(self.gravity_y, run.tool_calibration.accelerometer_y_offset, run.tool_calibration.accelerometer_y_gain, flip)

    def gravity_z_calibrated(self, run=None) :
        if not run :
            run = self.run
        flip = run.tool_calibration.tool.type.invert_gravity_z
        return self._calibrate(self.gravity_z, run.tool_calibration.accelerometer_z_offset, run.tool_calibration.accelerometer_z_gain, flip)

    def magnetic_x_calibrated(self, run=None) :
        if not run :
            run = self.run
        flip = run.tool_calibration.tool.type.invert_magnetic_x
        return self._calibrate(self.magnetic_x, run.tool_calibration.magnetometer_x_offset, run.tool_calibration.magnetometer_x_gain, flip)

    def magnetic_y_calibrated(self, run=None) :
        if not run :
            run = self.run
        flip = run.tool_calibration.tool.type.invert_magnetic_y
        return self._calibrate(self.magnetic_y, run.tool_calibration.magnetometer_y_offset, run.tool_calibration.magnetometer_y_gain, flip)

    def magnetic_z_calibrated(self, run=None) :
        if not run :
            run = self.run
        flip = run.tool_calibration.tool.type.invert_magnetic_z
        return self._calibrate(self.magnetic_z, run.tool_calibration.magnetometer_z_offset, run.tool_calibration.magnetometer_z_gain, flip)

    def total_gravity(self, run=None) :
        return round(sqrt(pow(self.gravity_x_calibrated(run),2)+pow(self.gravity_y_calibrated(run),2)+pow(self.gravity_z_calibrated(run),2)),3)

    def total_magnetic(self, run=None) :
        return round(sqrt(pow(self.magnetic_x_calibrated(run),2)+pow(self.magnetic_y_calibrated(run),2)+pow(self.magnetic_z_calibrated(run),2)),3)

    def inclination(self, run=None) :
        return round(acos(self.gravity_z_calibrated(run)/self.total_gravity(run)) * 180.0/pi, 3)

    def azimuth(self, run=None) :
        Gt = self.total_gravity(run)
        Gx = self.gravity_x_calibrated(run)        
        Gy = self.gravity_y_calibrated(run)
        Gz = self.gravity_z_calibrated(run)
        
        Bx = self.magnetic_x_calibrated(run)
        By = self.magnetic_y_calibrated(run)
        Bz = self.magnetic_z_calibrated(run)

        n = Gt * ( (By * Gx) - (Bx * Gy) )
        d = (Bz * (pow(Gx,2) + pow(Gy,2))) - (Gz * (Bx*Gx + By*Gy))
        if -0.0001 < d < 0.0001 :
            d = 0.0001

        a = round(atan2( n, d ) * 180.0 / pi, 3)

        if a < 0 :
            a = 360.0 + tf  
        return 

    def tool_face_magnetic(self, run=None) :
        Bx = self.magnetic_x_calibrated(run)
        By = self.magnetic_y_calibrated(run)

        if -0.0001 < By < 0.0001 :
            By = 0.0001
        
        tf = round(atan2(Bx,By) * 180.0/pi, 3)
        
        if tf < 0 :
            tf = 360.0 + tf  
        return tf
        

    def tool_face_gravity(self, run=None) :
        Gx = self.gravity_x_calibrated(run)        
        Gy = self.gravity_y_calibrated(run)
        
        if -0.0001 < Gy < 0.0001 :
            Gy = 0.0001

        tf = round( atan2(Gx,Gy) * 180.0/pi, 3)        
            
        if tf < 0 :
            tf = 360.0 + tf  
        return tf
        
admin.site.register(ToolMWDLog)


class ManualDepth(models.Model) :
    uid = UUIDField(primary_key=True, editable=False)
    run = models.ForeignKey(Run)
    time_stamp = models.DateTimeField(db_index=True)
    depth = models.DecimalField(max_digits=10, decimal_places=3, db_index=True)
    depth_units = models.CharField(max_length=2, choices = LENGTH_UNIT_CHOICES)
    notes = models.TextField(blank=True, null=True)

    def __unicode__(self) :
        return str(self.time_stamp) + " " + str(self.depth)

admin.site.register(ManualDepth)


class BlockPosition(models.Model) :
    uid = UUIDField(primary_key=True, editable=False)
    well = models.ForeignKey(Well)
    time_stamp = models.DateTimeField(db_index=True)
    position = models.DecimalField(max_digits=10, decimal_places=3)
    position_units = models.CharField(max_length=2, choices = LENGTH_UNIT_CHOICES)

admin.site.register(BlockPosition)


class HookLoad(models.Model) :
    uid = UUIDField(primary_key=True, editable=False)
    well = models.ForeignKey(Well)
    time_stamp = models.DateTimeField(db_index=True)
    value = models.DecimalField(max_digits=10, decimal_places=3)
    value_units = models.CharField(max_length=2, choices = WEIGHT_UNIT_CHOICES)

admin.site.register(HookLoad)


class Slip(models.Model) :
    SLIP_STATUS_CHOICES = ((0,'Out'),(1,'In'))
    uid = UUIDField(primary_key=True, editable=False)
    well = models.ForeignKey(Well)
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

    def get_active_well(self) :        
        active_well, created = Settings.objects.get_or_create(name='ACTIVE_WELL')
        return Well.objects.get(pk=active_well.value)

admin.site.register(Settings)


class WITSGeneralTimeBased(models.Model) :
    uid = UUIDField(primary_key=True, editable=False)
    well = models.ForeignKey(Well)
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
    well = models.ForeignKey(Well)
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

    def __unicode__(self) :
        return self.description() + " " + str(self.value)
        
admin.site.register(WITS0) 
